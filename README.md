# SportsMate: Intelligent Chatbot and Trip Planner

Welcome to SportsMate! A powerful application designed to enhance your sports experience with two key features:

- An Intelligent Chatbot system with specialized agents 🤖.
- A comprehensive Sports Event Trip Planner with visual roadmaps 🗺️.

---

## Table of Contents
- [SportsMate Chatbot](#sportsmate-chatbot)
  - [Overview](#overview)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Usage](#usage)
- [SportsMate Trip Planner](#sportsmate-trip-planner)
  - [Overview](#overview-1)
  - [Features](#features-1)
  - [Requirements](#requirements-1)
  - [Usage](#usage-1)
- [Setup Instructions](#setup-instructions)
- [About SportsMate](#about-sportsmate)
- [Future Improvements](#future-improvements)

---

## SportsMate Chatbot

### Overview
SportsMate's Intelligent Chatbot offers:
- Conversation memory tracking to provide context-aware responses 🧠.
- Specialized agents to handle different types of queries.
- Smart query routing, powered by OpenAI GPT-3.5-turbo.
- Integration with custom datasets for enhanced responses.

### Features

#### 1. Conversation Memory
- Remembers up to 10 previous interactions.
- Provides personalized, context-aware responses.

#### 2. Specialized Agents
- **FoodAgent**: Assists with food-related queries 🍔.
- **SportsAgent**: Provides sports-related information 🏅.
- **GeneralAgent**: A versatile assistant for miscellaneous queries.

#### 3. Query Routing
- GPT-3.5-turbo for intelligent classification of queries.
- Default fallback to **GeneralAgent** in case of errors or unrecognized queries.

### Requirements
- Python 3.8+
- openai library
- typing, json, and os libraries

### Usage
1. Set your OpenAI API key as an environment variable, or modify the code to include it.
2. Optionally, add JSON datasets to the datasets folder to enhance chatbot responses.
3. Launch the chatbot with:
   ```bash
   python chatbot/main.py
Chat with SportsMate and type 'exit' to end the session.

SportsMate Trip Planner
Overview
The SportsMate Trip Planner is a Jupyter Notebook that helps you:

Generate detailed trip itineraries.

Create visual roadmaps for sports events.

Features
1. User Input Collection
Collects key details like trip dates 📅, event preferences, accommodation needs, ticket status, and personal requirements.

2. Itinerary Generation
Generates a detailed daily schedule, including time-specific events ⏰.

Powered by OpenAI GPT-4-turbo for intelligent planning.

3. Visual Roadmap
Generates daily roadmap images.

Creates a final combined visualization of the trip with event details, times, and locations.

Requirements
Python 3.8+

openai library

datetime, os libraries

matplotlib, numpy, Pillow (PIL) libraries

Jupyter Notebook environment

Usage
Open the Scheduler.ipynb in Jupyter Notebook.

Provide your OpenAI API key as prompted.

Follow the interactive prompts to plan your trip.

Review your text-based itinerary and the final roadmap image.

The output will include:

A detailed text itinerary.

A sports_roadmap.png file (final roadmap).

Temporary daily roadmaps saved in the roadmap folder.

Setup Instructions
Install dependencies:

bash
Copy
Edit
pip install openai matplotlib numpy pillow
Additional Setup:

Obtain an OpenAI API key from OpenAI.

Create a datasets folder (optional) and add your custom JSON files to enhance the chatbot.

Run either the SportsMate Chatbot or Trip Planner based on your need.

About SportsMate
The SportsMate team is dedicated to enhancing the sports fan experience with smart, AI-driven technology. Whether you're seeking instant information on sports events or planning the perfect trip to a game, SportsMate provides personalized solutions to improve your experience.

Future Improvements
The following features are planned for future updates:

Persistent conversation storage for better user experience.

Enhanced dataset integration to improve chatbot responses.

Customizable roadmap designs for personalized trip planning.

Multi-language support to cater to a broader audience.

Audio descriptions for visually impaired fans to improve accessibility.
