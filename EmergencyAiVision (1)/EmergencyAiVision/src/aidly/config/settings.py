"""
Configuration settings for the Aidly application.
"""

# API Keys and Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Application Settings
APP_NAME = "Aidly"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Emergency Response AI Assistant"

# UI Settings
THEME_COLOR = "#FF4B4B"
BACKGROUND_COLOR = "#f0f2f6"
TEXT_COLOR = "#262730"

# Speech Settings
SPEECH_RATE = 0.9
SPEECH_LANG = "en-IN"

# Location Settings
DEFAULT_LATITUDE = 28.6139  # New Delhi
DEFAULT_LONGITUDE = 77.2090
DEFAULT_RADIUS = 5  # kilometers 