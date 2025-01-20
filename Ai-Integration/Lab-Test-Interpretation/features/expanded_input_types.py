
import xml.etree.ElementTree as ET
import hl7
import pydicom
from PIL import Image
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path
import io
import os
from typing import Dict, Any, List
import speech_recognition as sr
import librosa
from pydub import AudioSegment



class ExpandedInputProcessor:
    def __init__(self):
        self.supported_extensions = {
            'xml': self.parse_xml,
            'hl7': self.parse_hl7,
            'dcm': self.parse_dicom,
            'jpg': self.process_image,
            'jpeg': self.process_image,
            'png': self.process_image,
            'gif': self.process_image,
            'pdf': self.process_pdf,
            'wav': self.process_audio,
            'mp3': self.process_audio
        }

    def process_input(self, file_path: str) -> Dict[str, Any]:
        file_extension = file_path.split('.')[-1].lower()
        if file_extension not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        return self.supported_extensions[file_extension](file_path)

    def parse_xml(self, file_path: str) -> Dict[str, Any]:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        extracted_data = {}
        for elem in root.iter():
            if elem.tag in ['test_name', 'result', 'unit', 'reference_range']:
                extracted_data[elem.tag] = elem.text
        
        return extracted_data

    def parse_hl7(self, file_path: str) -> Dict[str, Any]:
        with open(file_path, 'r') as f:
            hl7_message = hl7.parse(f.read())
        
        extracted_data = {
            'test_name': str(hl7_message.segment('OBX')[3]),
            'result': str(hl7_message.segment('OBX')[5]),
            'unit': str(hl7_message.segment('OBX')[6]),
            'reference_range': str(hl7_message.segment('OBX')[7])
        }
        
        return extracted_data

    def parse_dicom(self, file_path: str) -> Dict[str, Any]:
        ds = pydicom.dcmread(file_path)
        
        extracted_data = {
            'patient_name': str(ds.PatientName),
            'study_description': str(ds.StudyDescription),
            'series_description': str(ds.SeriesDescription),
            'modality': str(ds.Modality)
        }
        
        return extracted_data

    def process_image(self, image_path: str) -> Dict[str, Any]:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Improve contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Binarization
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Deskew
        coords = np.column_stack(np.where(binary > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = binary.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(binary, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        # OCR
        text = pytesseract.image_to_string(rotated)
        
        return {'extracted_text': text}

    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        images = convert_from_path(pdf_path)
        extracted_text = ""
        
        for image in images:
            image_np = np.array(image)
            gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Improve contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # Binarization
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR
            text = pytesseract.image_to_string(binary)
            extracted_text += text + "\n"
        
        return {'extracted_text': extracted_text}

    def process_audio(self, audio_path: str) -> Dict[str, Any]:
        recognizer = sr.Recognizer()
    
          # Load the audio file
        audio_extension = os.path.splitext(audio_path)[1].lower()
    
        if audio_extension == '.wav':
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
        elif audio_extension in ['.mp3', '.ogg', '.flac']:
              # Convert to WAV first
             audio = AudioSegment.from_file(audio_path, format=audio_extension[1:])
             wav_path = audio_path.rsplit('.', 1)[0] + '.wav'
             audio.export(wav_path, format="wav")
             with sr.AudioFile(wav_path) as source:
                audio = recognizer.record(source)
             os.remove(wav_path)  
        else:
            raise ValueError(f"Unsupported audio format: {audio_extension}")
    
         # Perform noise reduction
        y, sr = librosa.load(audio_path)
        y_denoised = librosa.effects.preemphasis(y)
    
          # Convert the denoised audio to AudioData object
        frame_data = (y_denoised * 32767).astype(np.int16).tobytes()
        denoised_audio = sr.AudioData(frame_data, sr, 2)
    
        try:
            text = recognizer.recognize_google(denoised_audio)
        except sr.UnknownValueError:
            text = "Speech Recognition could not understand the audio"
        except sr.RequestError as e:
            text = f"Could not request results from Speech Recognition service; {e}"
   
        text = text.lower()
        text = ''.join(char for char in text if char.isalnum() or char.isspace())
    
        return {
            'extracted_text': text,
            'audio_duration': librosa.get_duration(y=y, sr=sr),
            'sample_rate': sr
        }


expanded_input_processor = ExpandedInputProcessor()

def process_expanded_input(file_path: str) -> Dict[str, Any]:
    return expanded_input_processor.process_input(file_path)
