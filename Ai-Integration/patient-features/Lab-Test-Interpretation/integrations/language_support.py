
import asyncio
from transformers import MarianMTModel, MarianTokenizer
import spacy
import torch
import logging

class LanguageProcessor:
    def __init__(self):
        self.translation_models = {}
        self.nlp_models = {}
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        self.logger.info("Initializing LanguageProcessor...")

        # Initialize translation models
        model_names = {
            'fr': 'Helsinki-NLP/opus-mt-en-fr',
            'es': 'Helsinki-NLP/opus-mt-en-es',
            'de': 'Helsinki-NLP/opus-mt-en-de',
            'it': 'Helsinki-NLP/opus-mt-en-it',
            'pt': 'Helsinki-NLP/opus-mt-en-pt',
            'nl': 'Helsinki-NLP/opus-mt-en-nl',
            'ru': 'Helsinki-NLP/opus-mt-en-ru',
            'zh': 'Helsinki-NLP/opus-mt-en-zh',
            'ja': 'Helsinki-NLP/opus-mt-en-jap',
            'ar': 'Helsinki-NLP/opus-mt-en-ar'
        }
        for lang, model_name in model_names.items():
            self.logger.info(f"Loading translation model for {lang}...")
            self.translation_models[lang] = {
                'model': await asyncio.to_thread(MarianMTModel.from_pretrained, model_name),
                'tokenizer': await asyncio.to_thread(MarianTokenizer.from_pretrained, model_name)
            }

        # Initialize NLP models
        nlp_model_names = {
            'en': 'en_core_web_sm',
            'fr': 'fr_core_news_sm',
            'es': 'es_core_news_sm',
            'de': 'de_core_news_sm',
            'it': 'it_core_news_sm',
            'pt': 'pt_core_news_sm',
            'nl': 'nl_core_news_sm',
            'ru': 'ru_core_news_sm',
            'zh': 'zh_core_web_sm',
            'ja': 'ja_core_news_sm'
        }
        for lang, model_name in nlp_model_names.items():
            self.logger.info(f"Loading NLP model for {lang}...")
            try:
                self.nlp_models[lang] = await asyncio.to_thread(spacy.load, model_name)
            except OSError:
                self.logger.warning(f"Model {model_name} not found. You may need to download it using: python -m spacy download {model_name}")

        self.logger.info("LanguageProcessor initialization complete.")

    async def detect_language(self, text):
        self.logger.info("Detecting language...")
        common_words = {
            'en': set(['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I']),
            'fr': set(['le', 'de', 'un', 'à', 'être', 'et', 'en', 'avoir', 'que', 'pour']),
            'es': set(['el', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 'no']),
            'de': set(['der', 'die', 'das', 'und', 'in', 'zu', 'den', 'von', 'für', 'nicht']),
            'it': set(['il', 'di', 'che', 'e', 'a', 'in', 'un', 'è', 'per', 'non']),
            'pt': set(['o', 'que', 'de', 'a', 'e', 'do', 'da', 'em', 'para', 'com']),
            'nl': set(['de', 'en', 'van', 'een', 'het', 'in', 'is', 'dat', 'op', 'te']),
            'ru': set(['и', 'в', 'не', 'на', 'я', 'быть', 'он', 'с', 'что', 'а']),
            'zh': set(['的', '是', '不', '了', '在', '人', '有', '我', '他', '这']),
            'ja': set(['の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し'])
        }
        
        words = set(text.lower().split())
        scores = {lang: len(words.intersection(common)) for lang, common in common_words.items()}
        detected_lang = max(scores, key=scores.get)
        self.logger.info(f"Detected language: {detected_lang}")
        return detected_lang

    async def translate(self, text, target_lang):
        self.logger.info(f"Translating to {target_lang}...")
        source_lang = await self.detect_language(text)
        if source_lang == target_lang:
            self.logger.info("Source and target languages are the same. No translation needed.")
            return text

        if target_lang not in self.translation_models:
            self.logger.error(f"Translation model for {target_lang} not available.")
            return text

        model = self.translation_models[target_lang]['model']
        tokenizer = self.translation_models[target_lang]['tokenizer']

        inputs = await asyncio.to_thread(tokenizer, text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        translated = await asyncio.to_thread(model.generate, **inputs)
        result = await asyncio.to_thread(tokenizer.decode, translated[0], skip_special_tokens=True)
        self.logger.info("Translation complete.")
        return result

    async def process_text(self, text, lang):
        self.logger.info(f"Processing text in {lang}...")
        if lang not in self.nlp_models:
            self.logger.error(f"NLP model for {lang} not available.")
            return None

        nlp = self.nlp_models[lang]
        doc = await asyncio.to_thread(nlp, text)
        
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        result = {
            'tokens': [token.text for token in doc],
            'entities': entities,
            'noun_chunks': [chunk.text for chunk in doc.noun_chunks],
            'dependencies': [(token.text, token.dep_, token.head.text) for token in doc]
        }
        self.logger.info("Text processing complete.")
        return result

