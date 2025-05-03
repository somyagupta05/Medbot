# Aidly - Emergency Response AI Assistant

A comprehensive emergency response system with AI-powered assistance, providing real-time support for medical emergencies, disaster response, and crisis management.

## Features

- 🎤 Voice Recognition: Speak your emergency situation
- 🗣️ Text-to-Speech: Listen to responses
- 🏥 Hospital Locator: Find nearest medical facilities
- 🌐 Multi-language Support: Communicate in multiple languages
- 📸 Image Analysis: Upload and analyze emergency images
- 📍 Location Services: Get location-based emergency assistance

## Project Structure

```
aidly/
├── src/
│   └── aidly/
│       ├── core/           # Main application code
│       ├── utils/          # Utility functions
│       ├── services/       # External service integrations
│       ├── assets/         # Static assets
│       └── config/         # Configuration files
├── tests/                  # Test files
├── .streamlit/            # Streamlit configuration
└── requirements.txt       # Python dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aidly.git
cd aidly
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file with:
```
GEMINI_API_KEY=your_api_key_here
```

## Usage

1. Start the application:
```bash
streamlit run src/aidly/core/app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Use the application:
   - Click the microphone icon to start voice input
   - Type or speak your emergency situation
   - Upload images if needed
   - Get AI-powered assistance and nearest hospital information

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini API for AI capabilities
- Streamlit for the web interface
- OpenStreetMap for location data 