# SportsMate: AI-Powered Sports Experience Platform

## Overview

**SportsMate** is a comprehensive AI-driven platform designed to enhance sports event experiences through intelligent chatbots, trip planning, and real-time assistance. The platform combines multiple AI technologies including natural language processing, computer vision, and speech-to-text capabilities to provide an immersive and interactive experience for sports enthusiasts.

## Features

### 1. Intelligent Chatbots
- **Emergency Reporting Bot**: Real-time emergency reporting system for stadium incidents
- **Pre-order Bot**: Food and beverage ordering system with context awareness
- **Sports Information Bot**: Provides details about teams, players, rules, and match moments

### 2. Trip Planning
- Personalized itinerary generation
- Visual roadmap creation
- Interactive schedule management
- Venue and accommodation recommendations

### 3. Audio & Speech Features
- Speech-to-Text functionality for hands-free interaction
- Audio descriptions for enhanced accessibility
- Multi-language support for international users

### 4. Flutter Mobile Application
- Cross-platform mobile interface
- Real-time updates and notifications
- Interactive UI for chatbot interactions
- Integrated trip planning features

## Installation

### Prerequisites
- Python 3.8 or higher
- Flutter SDK
- Node.js and npm
- OpenAI API key

### Backend Setup
1. Clone the repository:
```bash
git clone https://github.com/vexll/ai-league.git
cd ai-league
Install Python dependencies:
bash
Copy code
pip install -r requirements.txt
Set up environment variables:
bash
Copy code
export OPENAI_API_KEY="your-key-here"
Flutter Frontend Setup
Navigate to the Flutter project directory:
bash
Copy code
cd flutter_app
Install Flutter dependencies:
bash
Copy code
flutter pub get
Run the application:
bash
Copy code
flutter run
Dependencies
Backend
fastapi==0.104.1
uvicorn==0.23.2
openai==0.28.0
transformers>=4.30.0
torch>=2.0.0
python-multipart==0.0.6
pillow>=9.0.0
Frontend (Flutter)
flutter_bloc
dio
shared_preferences
speech_to_text
flutter_tts
Usage
Chatbot Interaction
python
Copy code
from chatbots.preorder_chatbot.main import PreorderAgent

bot = PreorderAgent()
response = bot.process_order("I'd like to order food", memory_input=[])
print(response)
Speech-to-Text Implementation
python
Copy code
from transformers import WhisperProcessor, WhisperForConditionalGeneration

processor = WhisperProcessor.from_pretrained("openai/whisper-base")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-base")

# Process audio input
transcription = model.generate(audio_input)
Trip Planning
python
Copy code
from roadmap_gen import generate_roadmap_visual

# Generate visual roadmap
generate_roadmap_visual(num_nodes=5, filename="trip_roadmap.png")
Project Structure
Copy code
ai-league/
├── chatbots/
│   ├── preorder_chatbot/
│   ├── report_chatbot/
│   └── test_chat_BE.py
├── audio_des/
│   └── processor.py
├── flutter_app/
│   └── lib/
├── scraping/
├── requirements.txt
└── README.md
Future Enhancements
Real-time match statistics integration
AR stadium navigation
Social features for fan interaction
Enhanced voice command support
Multi-language expansion
Ticket booking integration
Contributing
Contributions are welcome! Please feel free to submit a Pull Request.


Developed with ❤️ by the SportsMate team
Making sports experiences more accessible, enjoyable, and memorable through AI
