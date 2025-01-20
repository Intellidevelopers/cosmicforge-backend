POST /interpret

Purpose: Interpret lab results
Request body:

{
  "text": "Lab result text",
  "patient_id": "patient_id",
  "use_voice": boolean (optional),
  "target_lang": "language_code" (optional)
}



Response: JSON object with interpretation results



POST /voice_input

Purpose: Convert voice input to text
Request body: Form data with 'file' field containing audio file (WAV or MP3)
Response: JSON object with converted text



POST /expert_feedback

Purpose: Handle expert feedback on interpretations
Request body:

{
  "text": "Original lab result text",
  "expert_interpretation": "Expert's interpretation"
}



Response: JSON object with update status



POST /update_guidelines

Purpose: Update medical guidelines
Request body: None
Response: JSON object with update status message



GET /explain

Purpose: Get explanation for a specific test interpretation
Query parameters:

test_name: Name of the test
interpretation: Interpretation to explain


Response: JSON object with explanation



POST /submit_feedback

Purpose: Submit feedback on lab test interpretation
Request body:

{
  "lab_test_id": "id",
  "original_interpretation": "original interpretation",
  "corrected_interpretation": "corrected interpretation",
  "feedback_provider": "provider name"
}



Response: JSON object with success status