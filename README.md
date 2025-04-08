# SportsMate: Intelligent Chatbot and Trip Planner

Developed by the SportsMate team, this project offers two powerful components:
1. An intelligent chatbot system with specialized agents
2. A comprehensive sports event trip planner with visual roadmaps

## SportsMate Chatbot

### Overview
SportsMate's intelligent chatbot system features:
- Conversation memory tracking
- Specialized agents for different domains
- Smart query routing powered by OpenAI
- Dataset integration for enhanced responses

### Features
1. **Conversation Memory**
   - Remembers up to 10 previous interactions
   - Provides context-aware responses

2. **Specialized Agents**
   - FoodAgent: Your guide for food-related queries (ordering, menus, dietary needs)
   - SportsAgent: Your sports companion (matches, rules, teams)
   - GeneralAgent: Your all-purpose assistant

3. **Query Routing**
   - Powered by OpenAI GPT-3.5-turbo for classification
   - Fallback to GeneralAgent on errors

### Requirements
- Python 3.8+
- openai
- typing
- json
- os

### Usage
1. Set your OpenAI API key as an environment variable or modify the code
2. Add JSON datasets to the datasets folder (optional)
3. Launch SportsMate:
```bash
python chatbot/main.py
