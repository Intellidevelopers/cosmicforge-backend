
import os
import json
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename

from .AILabInterpreter import AILabInterpreter
from .Database import PostgreSQLDatabase
from .Config import Config
from .OutputFormatter import OutputFormatter

app = Flask(__name__)
load_dotenv()

class LabReportAPI:
    def __init__(self, interpreter: AILabInterpreter, database: PostgreSQLDatabase):
        self.interpreter = interpreter
        self.database = database
        self.app = app
        self.output_formatter = OutputFormatter()
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/interpret', methods=['POST'])
        async def interpret_report():
            try:
                data = await request.get_json()
                lab_results = data['lab_results']
                patient_info = data['patient_info']
                patient_id = patient_info.get('id')
                use_voice = data.get('use_voice', False)
                target_lang = data.get('target_lang', 'en')

                if not patient_id:
                    return jsonify({'error': 'Patient ID is required'}), 400

                interpretations = await self.interpreter.interpret_lab_results(lab_results, patient_id, use_voice, target_lang)
                
                if use_voice:
                    audio_file = await self.interpreter.voice_interface.text_to_speech(interpretations['interpretation'])
                    return send_file(audio_file, mimetype='audio/mp3')
                else:
                    return jsonify(interpretations)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/update_guidelines', methods=['POST'])
        async def update_guidelines():
            try:
                await self.interpreter.update_medical_guidelines()
                return jsonify({"message": "Guidelines updated successfully"})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/explain', methods=['GET'])
        async def explain_interpretation():
            try:
                test_name = request.args.get('test_name')
                interpretation = request.args.get('interpretation')
                explanation = await self.interpreter.explain_interpretation(test_name, interpretation)
                return jsonify({"explanation": explanation})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/submit_feedback', methods=['POST'])
        async def submit_feedback():
            try:
                data = await request.get_json()
                await self.interpreter.submit_feedback(
                    data['lab_test_id'],
                    data['original_interpretation'],
                    data['corrected_interpretation'],
                    data['feedback_provider']
                )
                return jsonify({"status": "success"})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/voice_input', methods=['POST'])
        async def voice_input():
            try:
                if 'file' not in request.files:
                    return jsonify({'error': 'No file part'}), 400
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No selected file'}), 400
                if file and self.allowed_file(file.filename, {'wav', 'mp3'}):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    text = await self.interpreter.voice_interface.speech_to_text(filepath)
                    os.remove(filepath)  # Clean up the uploaded file
                    
                    return jsonify({'text': text})
                return jsonify({'error': 'Invalid file type'}), 400
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/expert_feedback', methods=['POST'])
        async def expert_feedback():
            try:
                data = await request.get_json()
                text = data['text']
                expert_interpretation = data['expert_interpretation']

                result = await self.interpreter.handle_expert_feedback(text, expert_interpretation)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/generate_report', methods=['POST'])
        async def generate_report():
            try:
                data = await request.get_json()
                interpretations = data['interpretations']
                patient_info = data['patient_info']
                report_format = data.get('format', 'pdf')

                if report_format == 'pdf':
                    pdf_path = 'temp_report.pdf'
                    self.output_formatter.to_pdf(interpretations, pdf_path, patient_info)
                    return send_file(pdf_path, as_attachment=True, attachment_filename='lab_report.pdf')
                elif report_format == 'html':
                    html_content = self.output_formatter.to_html(interpretations)
                    return html_content
                elif report_format == 'json':
                    return jsonify(interpretations)
                else:
                    return jsonify({'error': 'Unsupported report format'}), 400
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    def allowed_file(self, filename, allowed_extensions):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    async def start(self):
        self.app.run(host='0.0.0.0', port=5000)

async def main():
    # Load environment variables
    load_dotenv()

    # Initialize the config
    config = Config()

    # Initialize the database
    database = PostgreSQLDatabase(config.get_db_url())
    await database.initialize()

    # Initialize the interpreter
    interpreter = AILabInterpreter(config, database)
    await interpreter.initialize()

    # Train the interpreter (if needed)
    await interpreter.train(os.getenv('TRAINING_DATA_PATH'))

    # Save the trained models
    await interpreter.save_models(os.getenv('MODELS_DIR'))

    # Update medical guidelines
    await interpreter.update_medical_guidelines()

    # Process a sample lab report
    lab_report = {
        "patient_info": {
            "id": "12345",
            "name": "John Doe",
            "age": 45,
            "gender": "Male",
            "medical_history": ["hypertension", "type 2 diabetes"]
        },
        "results": {
            "Complete Blood Count": 7.5,
            "Lipid Panel": 220
        }
    }

    interpretations = await interpreter.interpret_lab_results(lab_report['results'], lab_report['patient_info']['id'])
    print("Lab Report Interpretations:")
    print(json.dumps(interpretations, indent=2))

    # Generate a narrative report
    report = await interpreter.generate_narrative_report(interpretations, lab_report["patient_info"])
    print("\nNarrative Report:")
    print(report)

    # Initialize and run the API
    api = LabReportAPI(interpreter, database)
    await api.start()

if __name__ == "__main__":
    asyncio.run(main())
