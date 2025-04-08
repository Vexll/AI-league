# SportsMate: Intelligent Chatbot and Trip Planner

Welcome to **SportsMate** - the ultimate AI companion for sports enthusiasts! Our application combines two powerful components to enhance your sports experience:

1. 🤖 **Intelligent Chatbot System** with specialized sports knowledge agents
2. 🗺️ **Comprehensive Trip Planner** for sports events with visual roadmaps

## Table of Contents
- [Features Overview](#features-overview)
- [SportsMate Chatbot](#sportsmate-chatbot)
  - [Capabilities](#capabilities)
  - [Technical Details](#technical-details)
  - [Setup & Usage](#setup--usage)
- [SportsMate Trip Planner](#sportsmate-trip-planner)
  - [Capabilities](#capabilities-1)
  - [Technical Details](#technical-details-1)
  - [Setup & Usage](#setup--usage-1)
- [Installation Guide](#installation-guide)
- [Project Vision](#project-vision)
- [Roadmap](#roadmap)

## Features Overview

**SportsMate** integrates AI-powered conversation with intelligent trip planning to provide:

- Contextual sports information and recommendations
- Personalized sports event itineraries
- Visual roadmaps for easy trip navigation
- Food and venue recommendations for the complete fan experience

## SportsMate Chatbot

### Capabilities

Our intelligent chatbot system leverages advanced NLP technology to deliver:

- **Context-Aware Conversations**: Tracks your conversation history to provide more relevant and personalized responses
- **Domain Expertise**: Access specialized knowledge about sports, food, venues, and more
- **Intelligent Query Handling**: Automatically routes your questions to the most appropriate knowledge agent

### Technical Details

- **Conversation Memory**: Maintains context across up to 10 previous interactions
- **Specialized Agents**:
  - **SportsAgent**: Expert in teams, players, rules, schedules, and sports history
  - **FoodAgent**: Specializes in game day food, stadium concessions, and dining recommendations
  - **GeneralAgent**: Handles all other queries with versatile assistance
- **Smart Query Classification**: Powered by OpenAI GPT-3.5-turbo
- **Custom Datasets**: Enhanced responses through integrated sports knowledge bases

### Setup & Usage

1. Ensure your OpenAI API key is set as an environment variable
2. Optional: Enhance responses by adding custom JSON datasets to the `datasets` folder
3. Launch the chatbot:
   ```bash
   python chatbot/main.py
   ```
4. Chat naturally with SportsMate about any sports-related topics
5. Type 'exit' when you're done

## SportsMate Trip Planner

### Capabilities

Our Jupyter Notebook-based planner helps you:

- Create detailed, day-by-day itineraries for sports event trips
- Generate visual roadmaps showing your complete schedule
- Account for travel, accommodation, food, and event timing
- Personalize your experience based on preferences and requirements

### Technical Details

- **Intelligent Planning**: Powered by OpenAI GPT-4-turbo
- **User Input Collection**: Gathers key information about:
  - Trip dates and duration
  - Event details and preferences
  - Accommodation requirements
  - Transportation needs
  - Ticket status
  - Personal preferences and special requirements
- **Visual Roadmap Generation**:
  - Daily schedule visualizations
  - Comprehensive trip overview with color-coded activities
  - Time-specific event planning

### Setup & Usage

1. Open `Scheduler.ipynb` in a Jupyter Notebook environment
2. Enter your OpenAI API key when prompted
3. Follow the interactive prompts to input your trip details
4. Review and save your generated:
   - Text-based itinerary with detailed scheduling
   - Visual roadmap (`sports_roadmap.png`)
   - Daily schedule images (stored in the `roadmap` folder)

## Installation Guide

### Prerequisites
- Python 3.8 or higher
- Jupyter Notebook (for Trip Planner)

### Dependencies
Install all required packages:

```bash
pip install openai matplotlib numpy pillow
```

### Configuration
1. Obtain an API key from [OpenAI](https://openai.com)
2. Either:
   - Set it as an environment variable: `export OPENAI_API_KEY="your-key-here"`
   - Or be prepared to enter it when prompted

## Project Vision

**SportsMate** is designed to transform how fans experience sports events. Our AI-driven approach helps users:

- Access comprehensive sports knowledge instantly
- Plan memorable trips to sports events with minimal stress
- Navigate venues, find food options, and maximize enjoyment
- Create personalized experiences tailored to individual preferences

We believe technology should enhance the emotional and community aspects of sports fandom, not replace them.

## Roadmap

Future enhancements planned for SportsMate include:

- **Real-time Data Integration**: Live scores, stats, and event updates
- **Multi-platform Support**: Web interface and mobile applications
- **Enhanced Visualization**: Interactive maps and AR venue guidance
- **Social Features**: Connect with other fans attending the same events
- **Accessibility Improvements**: Audio descriptions for visually impaired users
- **Multi-language Support**: Serving international sports fans
- **Ticket Integration**: Direct purchase options through partner services
- **Persistent User Profiles**: Save preferences and past trips for better recommendations

---

Developed with ❤️ by the SportsMate team  
*Making sports experiences more accessible, enjoyable, and memorable through AI*
