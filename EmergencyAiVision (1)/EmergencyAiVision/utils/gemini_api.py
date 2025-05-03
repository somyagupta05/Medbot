import os
import requests
import json
import io
import base64
from PIL import Image
from .image_processing import image_to_base64

# Get API key from environment variables with fallback
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCkPqrUICeyv5_bWBhXEsirema0ngmAIQk")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def analyze_injury(image):
    """
    Analyze the uploaded injury image using Gemini API
    
    Args:
        image (PIL.Image): Preprocessed image of the injury
        
    Returns:
        dict: Analysis results including injury type, severity, and recommended actions
    """
    # Convert image to base64 string
    img_base64 = image_to_base64(image)
    
    # Prepare the prompt for Gemini API
    prompt = """
    You are an Aidly application analyzing an injury image for Indian users. 
    Analyze this image of an injury or medical condition and provide the following information:
    
    1. What type of injury or condition is shown in the image?
    2. Rate the severity on a scale of 1-10 (where 10 is most severe)
    3. What are the key symptoms or characteristics visible?
    4. What immediate actions should be taken?
    
    Format your response as a JSON object with the following keys:
    {
        "condition": "Brief name of the identified condition or injury",
        "severity_score": numeric severity value (1-10),
        "visible_symptoms": ["symptom1", "symptom2", ...],
        "immediate_actions": ["action1", "action2", ...],
        "additional_notes": "Any additional important information"
    }
    
    Be concise, accurate, and focus only on what's visible in the image.
    Consider Indian healthcare context where appropriate.
    """
    
    # Prepare the request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": img_base64
                        }
                    }
                ]
            }
        ],
        "generation_config": {
            "temperature": 0.4,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024
        }
    }
    
    # Make API request
    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract the response text
            response_text = result["candidates"][0]["content"]["parts"][0]["text"]
            
            # Extract JSON from the response text
            import re
            json_match = re.search(r'({.*?})', response_text, re.DOTALL)
            
            if json_match:
                try:
                    analysis_result = json.loads(json_match.group(0))
                    return analysis_result
                except json.JSONDecodeError:
                    # Fallback to manual parsing if JSON extraction fails
                    analysis_result = {
                        "condition": "Unknown",
                        "severity_score": 5,
                        "visible_symptoms": ["Unable to determine"],
                        "immediate_actions": ["Seek professional medical advice"],
                        "additional_notes": "Could not properly analyze the image"
                    }
                    return analysis_result
            else:
                # Create a structured response if JSON not found
                lines = response_text.split('\n')
                analysis_result = {
                    "condition": next((line.split(':')[1].strip() for line in lines if 'condition' in line.lower()), "Unknown"),
                    "severity_score": next((int(line.split(':')[1].strip()) for line in lines if 'severity' in line.lower()), 5),
                    "visible_symptoms": [s.strip() for s in next((line.split(':')[1].strip().split(',') for line in lines if 'symptom' in line.lower()), ["Unable to determine"])],
                    "immediate_actions": [a.strip() for a in next((line.split(':')[1].strip().split(',') for line in lines if 'action' in line.lower()), ["Seek professional medical advice"])],
                    "additional_notes": next((line.split(':')[1].strip() for line in lines if 'note' in line.lower()), "")
                }
                return analysis_result
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return {
                "condition": "Analysis Error",
                "severity_score": 5,
                "visible_symptoms": ["Unable to analyze"],
                "immediate_actions": ["Seek professional medical advice"],
                "additional_notes": f"API Error: {response.status_code}"
            }
    
    except Exception as e:
        print(f"Exception in analyze_injury: {e}")
        return {
            "condition": "Analysis Error",
            "severity_score": 5,
            "visible_symptoms": ["Unable to analyze due to technical error"],
            "immediate_actions": ["Seek professional medical advice"],
            "additional_notes": f"Error: {str(e)}"
        }

def generate_first_aid(analysis_result):
    """
    Generate first aid instructions based on the analysis result
    
    Args:
        analysis_result (dict): Analysis results from analyze_injury function
        
    Returns:
        str: First aid instructions in markdown format
    """
    condition = analysis_result.get("condition", "Unknown")
    severity = analysis_result.get("severity_score", 5)
    symptoms = analysis_result.get("visible_symptoms", [])
    immediate_actions = analysis_result.get("immediate_actions", [])
    
    # Prepare the prompt for Gemini API
    prompt = f"""
    You are an Aidly application providing first aid guidance for Indian users.
    
    Based on the following injury analysis, provide detailed first aid instructions:
    
    Condition: {condition}
    Severity: {severity}/10
    Visible Symptoms: {', '.join(symptoms)}
    Recommended Immediate Actions: {', '.join(immediate_actions)}
    
    Provide a comprehensive first aid guide with step-by-step instructions formatted in markdown. Include:
    
    1. Initial assessment steps
    2. Specific first aid procedures in order of priority
    3. Clear warnings about what NOT to do
    4. Signs that indicate when to seek immediate professional medical help (mention Indian emergency numbers 112 and 108)
    
    Make your instructions clear, concise, and easy to follow in an emergency situation. 
    Use bullet points and headers for readability.
    Consider Indian healthcare context where appropriate, including local medical terminology and available resources.
    """
    
    # Prepare the request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generation_config": {
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024
        }
    }
    
    # Make API request
    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract the response text
            first_aid_instructions = result["candidates"][0]["content"]["parts"][0]["text"]
            return first_aid_instructions
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return "Unable to generate first aid instructions. Please seek professional medical advice."
    
    except Exception as e:
        print(f"Exception in generate_first_aid: {e}")
        return "Error generating first aid instructions. Please seek professional medical advice."

def get_chatbot_response(user_query, language="en"):
    """
    Get a response from the Gemini-powered chatbot assistant
    
    Args:
        user_query (str): User's question or message
        language (str): Language code for the response
        
    Returns:
        str: Chatbot response
    """
    # Prepare the prompt for Gemini API
    prompt = f"""
    You are an Aidly emergency chatbot assistant for Indian users. You provide helpful, accurate, and 
    concise first aid and emergency guidance. The user has asked:
    
    "{user_query}"
    
    Provide a helpful response that is:
    1. Accurate and based on established first aid protocols
    2. Concise and easy to understand in an emergency
    3. Clear about when professional medical help should be sought (mention Indian emergency numbers: 112 for National Emergency, 108 for Ambulance when relevant)
    4. Formatted with bullet points or numbered steps if providing instructions
    
    If the query is not related to first aid or emergency response, politely redirect the conversation 
    to emergency and first aid topics only.
    
    Consider Indian healthcare context where appropriate, including local medical terminology and available resources.
    
    Language: {language}
    """
    
    # Prepare the request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generation_config": {
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024
        }
    }
    
    # Make API request
    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract the response text
            chatbot_response = result["candidates"][0]["content"]["parts"][0]["text"]
            return chatbot_response
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return "I'm sorry, I'm having trouble processing your request right now. For medical emergencies, please call emergency services immediately."
    
    except Exception as e:
        print(f"Exception in get_chatbot_response: {e}")
        return "I'm sorry, I encountered an error. For medical emergencies, please call emergency services immediately."
