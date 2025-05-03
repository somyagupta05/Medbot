import os
import requests
import json

# Get API key from environment variables with fallback - using Gemini API key for translation as well
TRANSLATION_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY", os.getenv("GEMINI_API_KEY", "AIzaSyCkPqrUICeyv5_bWBhXEsirema0ngmAIQk"))

# Supported languages with their display names
SUPPORTED_LANGUAGES = {
    "en": "English"
}

def translate_text(text, target_language="en"):
    """
    Translate text to the target language using Google Cloud Translation API
    
    Args:
        text (str): Text to translate
        target_language (str): Target language code
        
    Returns:
        str: Translated text
    """
    if not text or target_language == "en":
        return text
    
    try:
        # Prepare the API URL
        url = f"https://translation.googleapis.com/language/translate/v2?key={TRANSLATION_API_KEY}"
        
        # Prepare the request payload
        payload = {
            "q": text,
            "target": target_language,
            "format": "text"
        }
        
        # Make the API request
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'data' in result and 'translations' in result['data'] and result['data']['translations']:
                translated_text = result['data']['translations'][0]['translatedText']
                return translated_text
            else:
                print("Translation API returned an unexpected response format")
                return text
        else:
            print(f"Translation API error: {response.status_code} - {response.text}")
            return text
    
    except Exception as e:
        print(f"Exception in translate_text: {e}")
        return text

def detect_language(text):
    """
    Detect the language of the given text using Google Cloud Translation API
    
    Args:
        text (str): Text to analyze
        
    Returns:
        str: Detected language code
    """
    if not text:
        return "en"
    
    try:
        # Prepare the API URL
        url = f"https://translation.googleapis.com/language/translate/v2/detect?key={TRANSLATION_API_KEY}"
        
        # Prepare the request payload
        payload = {
            "q": text
        }
        
        # Make the API request
        response = requests.post(url, data=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'data' in result and 'detections' in result['data'] and result['data']['detections']:
                detected_language = result['data']['detections'][0][0]['language']
                return detected_language
            else:
                print("Language detection API returned an unexpected response format")
                return "en"
        else:
            print(f"Language detection API error: {response.status_code} - {response.text}")
            return "en"
    
    except Exception as e:
        print(f"Exception in detect_language: {e}")
        return "en"

def get_supported_languages():
    """
    Get a list of supported languages from the Translation API
    
    Returns:
        dict: Dictionary mapping language codes to language names
    """
    try:
        # Prepare the API URL
        url = f"https://translation.googleapis.com/language/translate/v2/languages?key={TRANSLATION_API_KEY}&target=en"
        
        # Make the API request
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'data' in result and 'languages' in result['data']:
                languages = {}
                
                for lang in result['data']['languages']:
                    languages[lang['language']] = lang['name']
                
                return languages
            else:
                print("Languages API returned an unexpected response format")
                return SUPPORTED_LANGUAGES
        else:
            print(f"Languages API error: {response.status_code} - {response.text}")
            return SUPPORTED_LANGUAGES
    
    except Exception as e:
        print(f"Exception in get_supported_languages: {e}")
        return SUPPORTED_LANGUAGES
