

import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from flask import Flask, request, jsonify, send_file
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from langdetect import detect
import redis
import logging
from concurrent.futures import ThreadPoolExecutor
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import os
import schedule
import time
import threading
import requests
from functools import wraps
import speech_recognition as sr
from pydub import AudioSegment
from gtts import gTTS
import moviepy.editor as mp
import PyPDF2
import docx
import tempfile
import uuid
from werkzeug.utils import secure_filename
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Sentry for error tracking
sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FlaskIntegration()]
)

# Initialize Flask app
app = Flask(__name__)

# Set up rate limiting
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize Redis cache
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Initialize translation model
model_name = "facebook/m2m100_418M"
model = M2M100ForConditionalGeneration.from_pretrained(model_name)
tokenizer = M2M100Tokenizer.from_pretrained(model_name)

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Initialize thread pool for concurrent processing
executor = ThreadPoolExecutor(max_workers=4)

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
    'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'zh': 'Chinese',
    'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic', 'hi': 'Hindi'
}

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'mp3', 'wav', 'mp4', 'avi'}

# Error handling decorator
def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            sentry_sdk.capture_exception(e)
            return jsonify({'error': 'An unexpected error occurred'}), 500
    return decorated_function

def detect_language(text):
    try:
        return detect(text)
    except:
        return 'en'  # Default to English if detection fails

def translate_text(text, source_lang, target_lang):
    cache_key = f"{source_lang}:{target_lang}:{text}"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        return cached_result.decode('utf-8')
    
    try:
        tokenizer.src_lang = source_lang
        encoded_text = tokenizer(text, return_tensors="pt").to(device)
        generated_tokens = model.generate(
            **encoded_text,
            forced_bos_token_id=tokenizer.get_lang_id(target_lang),
            max_length=128
        )
        translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        
        # Cache the result
        redis_client.setex(cache_key, 3600, translated_text)  # Cache for 1 hour
        
        return translated_text
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        sentry_sdk.capture_exception(e)
        return None

@app.route('/chat', methods=['POST'])
@limiter.limit("20/minute")
@handle_errors
def chat():
    data = request.json
    text = data.get('text')
    target_lang = data.get('target_lang', 'en')
    file = data.get('file')
    file_type = data.get('file_type')

    if not text and not file:
        return jsonify({'error': 'Missing text or file'}), 400

    if target_lang not in SUPPORTED_LANGUAGES:
        return jsonify({'error': 'Unsupported target language'}), 400

    try:
        if file:
            if file_type == 'text':
                text = extract_text_from_file(file)
            elif file_type in ['audio', 'voice']:
                text = transcribe_audio(file)
            elif file_type == 'video':
                audio = extract_audio_from_video(file)
                text = transcribe_audio(audio)
            else:
                return jsonify({'error': 'Unsupported file type'}), 400

        source_lang = detect_language(text)
        translated_text = translate_text(text, source_lang, target_lang)

        if translated_text:
            response = f"Here's the translation from {SUPPORTED_LANGUAGES[source_lang]} to {SUPPORTED_LANGUAGES[target_lang]}:\n\n{translated_text}\n\nIs there anything else you'd like me to translate?"
            
            if file_type in ['audio', 'voice']:
                # Convert translated text back to speech
                tts = gTTS(text=translated_text, lang=target_lang)
                output_path = os.path.join(tempfile.gettempdir(), f"translated_audio_{uuid.uuid4()}.mp3")
                tts.save(output_path)
                return send_file(output_path, as_attachment=True, download_name="translated_audio.mp3")
            elif file_type == 'video':
                # Add subtitles to video
                srt_path = os.path.join(tempfile.gettempdir(), f"subtitles_{uuid.uuid4()}.srt")
                with open(srt_path, 'w', encoding='utf-8') as srt_file:
                    srt_file.write(f"1\n00:00:00,000 --> 99:59:59,999\n{translated_text}\n")
                
                video = mp.VideoFileClip(file)
                subtitles = mp.SubtitlesClip(srt_path, lambda txt: mp.TextClip(txt, font='Arial', fontsize=24, color='white'))
                final_video = mp.CompositeVideoClip([video, subtitles.set_position(('center', 'bottom'))])
                output_path = os.path.join(tempfile.gettempdir(), f"translated_video_{uuid.uuid4()}.mp4")
                final_video.write_videofile(output_path)
                return send_file(output_path, as_attachment=True, download_name="translated_video.mp4")
            else:
                return jsonify({
                    'original_text': text,
                    'translated_text': response,
                    'source_lang': source_lang,
                    'target_lang': target_lang
                })
        else:
            return jsonify({'error': 'Translation failed'}), 500
    except Exception as e:
        logger.error(f"Chat translation error: {str(e)}")
        sentry_sdk.capture_exception(e)
        return jsonify({'error': 'Processing failed'}), 500

@app.route('/api/translate', methods=['POST'])
@limiter.limit("10/minute")
@handle_errors
def translate():
    data = request.json
    text = data.get('text')
    target_lang = data.get('targetLanguage')
    
    if not text or not target_lang:
        return jsonify({'error': 'Missing text or target language'}), 400
    
    if target_lang not in SUPPORTED_LANGUAGES:
        return jsonify({'error': 'Unsupported target language'}), 400
    
    source_lang = detect_language(text)
    
    if source_lang == target_lang:
        return jsonify({'translatedText': text, 'sourceLang': source_lang})
    
    translated_text = translate_text(text, source_lang, target_lang)
    
    if translated_text:
        return jsonify({
            'translatedText': translated_text,
            'sourceLang': source_lang,
            'targetLang': target_lang
        })
    else:
        return jsonify({'error': 'Translation failed'}), 500

@app.route('/api/supported_languages', methods=['GET'])
@limiter.limit("100/minute")
@handle_errors
def get_supported_languages():
    return jsonify(SUPPORTED_LANGUAGES)

@app.route('/api/detect_language', methods=['POST'])
@limiter.limit("20/minute")
@handle_errors
def detect_lang():
    data = request.json
    text = data.get('text')
    
    if not text:
        return jsonify({'error': 'Missing text'}), 400
    
    detected_lang = detect_language(text)
    return jsonify({'detectedLanguage': detected_lang})

def background_translation(text, source_lang, target_lang, session_id):
    translated_text = translate_text(text, source_lang, target_lang)
    if translated_text:
        redis_client.setex(f"background_translation:{session_id}", 3600, translated_text)

@app.route('/api/background_translate', methods=['POST'])
@limiter.limit("5/minute")
@handle_errors
def background_translate():
    data = request.json
    text = data.get('text')
    target_lang = data.get('targetLanguage')
    session_id = data.get('sessionId')
    
    if not text or not target_lang or not session_id:
        return jsonify({'error': 'Missing text, target language, or session ID'}), 400
    
    if target_lang not in SUPPORTED_LANGUAGES:
        return jsonify({'error': 'Unsupported target language'}), 400
    
    source_lang = detect_language(text)
    
    executor.submit(background_translation, text, source_lang, target_lang, session_id)
    
    return jsonify({'message': 'Translation started', 'sessionId': session_id})

@app.route('/api/get_background_translation', methods=['GET'])
@limiter.limit("20/minute")
@handle_errors
def get_background_translation():
    session_id = request.args.get('sessionId')
    
    if not session_id:
        return jsonify({'error': 'Missing session ID'}), 400
    
    translated_text = redis_client.get(f"background_translation:{session_id}")
    
    if translated_text:
        return jsonify({'translatedText': translated_text.decode('utf-8')})
    else:
        return jsonify({'message': 'Translation not ready or not found'}), 404

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

# Function to update the model
def update_model():
    global model, tokenizer
    logger.info("Updating the model...")
    try:
        model = M2M100ForConditionalGeneration.from_pretrained(model_name)
        tokenizer = M2M100Tokenizer.from_pretrained(model_name)
        model.to(device)
        logger.info("Model updated successfully")
    except Exception as e:
        logger.error(f"Error updating model: {str(e)}")
        sentry_sdk.capture_exception(e)

# Schedule model updates
schedule.every().day.at("02:00").do(update_model)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduling thread
scheduling_thread = threading.Thread(target=run_schedule)
scheduling_thread.start()

# File translation functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(file):
    filename = secure_filename(file.filename)
    file_extension = filename.rsplit('.', 1)[1].lower()

    if file_extension == 'txt':
        return file.read().decode('utf-8')
    elif file_extension == 'pdf':
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    elif file_extension == 'docx':
        doc = docx.Document(file)
        return " ".join([paragraph.text for paragraph in doc.paragraphs])
    else:
        raise ValueError("Unsupported file type")

@app.route('/api/translate_file', methods=['POST'])
@limiter.limit("5/hour")
@handle_errors
def translate_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    target_lang = request.form.get('target_lang')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    if target_lang not in SUPPORTED_LANGUAGES:
        return jsonify({'error': 'Unsupported target language'}), 400

    try:
        text = extract_text_from_file(file)
        source_lang = detect_language(text)
        translated_text = translate_text(text, source_lang, target_lang)

        if translated_text:
            return jsonify({
                'translatedText': translated_text,
                'sourceLang': source_lang,
                'targetLang': target_lang
            })
        else:
            return jsonify({'error': 'Translation failed'}), 500
    except Exception as e:
        logger.error(f"File translation error: {str(e)}")
        sentry_sdk.capture_exception(e)
        return jsonify({'error': 'File processing failed'}), 500

# Voice translation functions
def transcribe_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        raise ValueError("Speech recognition could not understand the audio")
    except sr.RequestError:
        raise ValueError("Could not request results from speech recognition service")

@app.route('/api/translate_voice', methods=['POST'])
@limiter.limit("5/hour")
@handle_errors
def translate_voice():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    target_lang = request.form.get('target_lang')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    if target_lang not in SUPPORTED_LANGUAGES:
        return jsonify({'error': 'Unsupported target language'}), 400

    try:
        # Save the uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(temp_path)

        # Convert to WAV if necessary
        if not temp_path.lower().endswith('.wav'):
            audio = AudioSegment.from_file(temp_path)
            temp_path = os.path.join(temp_dir, "temp_audio.wav")
            audio.export(temp_path, format="wav")

        # Transcribe audio to text
        text = transcribe_audio(temp_path)
        source_lang = detect_language(text)
        translated_text = translate_text(text, source_lang, target_lang)

        if translated_text:
            # Convert translated text back to speech
            tts = gTTS(text=translated_text, lang=target_lang)
            output_path = os.path.join(temp_dir, "translated_audio.mp3")
            tts.save(output_path)

            return send_file(output_path, as_attachment=True, download_name="translated_audio.mp3")
        else:
            return jsonify({'error': 'Translation failed'}), 500
    except Exception as e:
        logger.error(f"Voice translation error: {str(e)}")
        sentry_sdk.capture_exception(e)
        return jsonify({'error': 'Voice processing failed'}), 500
    finally:
        # Clean up temporary files
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
        os.rmdir(temp_dir)

# Video translation functions
def extract_audio_from_video(video_path):
    video = mp.VideoFileClip(video_path)
    audio_path = video_path.rsplit('.', 1)[0] + ".wav"
    video.audio.write_audiofile(audio_path)
    return audio_path

@app.route('/api/translate_video', methods=['POST'])
@limiter.limit("2/hour")
@handle_errors
def translate_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    target_lang = request.form.get('target_lang')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    if target_lang not in SUPPORTED_LANGUAGES:
        return jsonify({'error': 'Unsupported target language'}), 400

    try:
        # Save the uploaded file temporarily
        temp_dir = tempfile.mkdtemp()
        video_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(video_path)

        # Extract audio from video
        audio_path = extract_audio_from_video(video_path)

        # Transcribe audio to text
        text = transcribe_audio(audio_path)
        source_lang = detect_language(text)
        translated_text = translate_text(text, source_lang, target_lang)

        if translated_text:
            # Generate subtitles (simplified approach)
            srt_path = os.path.join(temp_dir, "subtitles.srt")
            with open(srt_path, 'w', encoding='utf-8') as srt_file:
                srt_file.write(f"1\n00:00:00,000 --> 99:59:59,999\n{translated_text}\n")

            # Add subtitles to video
            video = mp.VideoFileClip(video_path)
            subtitles = mp.SubtitlesClip(srt_path, lambda txt: mp.TextClip(txt, font='Arial', fontsize=24, color='white'))
            final_video = mp.CompositeVideoClip([video, subtitles.set_position(('center', 'bottom'))])
            output_path = os.path.join(temp_dir, "translated_video.mp4")
            final_video.write_videofile(output_path)

            return send_file(output_path, as_attachment=True, download_name="translated_video.mp4")
        else:
            return jsonify({'error': 'Translation failed'}), 500
    except Exception as e:
        logger.error(f"Video translation error: {str(e)}")
        sentry_sdk.capture_exception(e)
        return jsonify({'error': 'Video processing failed'}), 500
    finally:
        # Clean up temporary files
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
        os.rmdir(temp_dir)


if __name__ == '__main__':
    # This block will only be executed if the script is run directly, not when imported
    print("To run this application in production, use Gunicorn:")
    print("gunicorn --bind 0.0.0.0:5000 your_app_file:app")
    
    # For development purposes only:
    # app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
