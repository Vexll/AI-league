# chatbot/main.py

import json
import os
import openai
from typing import Dict, Any

# ===================== Memory =====================

class ConversationMemory:
    def __init__(self, max_history_length=10):
        self.memory = []
        self.max_history_length = max_history_length
    
    def add_interaction(self, user_query: str, bot_response: str):
        self.memory.append({"user": user_query, "bot": bot_response})
        if len(self.memory) > self.max_history_length:
            self.memory = self.memory[-self.max_history_length:]
    
    def get_conversation_context(self) -> str:
        context = "Conversation History:\n"
        for interaction in self.memory:
            context += f"User: {interaction['user']}\n"
            context += f"Bot: {interaction['bot']}\n"
        return context

# ===================== Base Agent =====================

class BaseAgent:
    def __init__(self):
        self.datasets = self.load_datasets()
    
    def load_datasets(self):
        datasets = {}
        datasets_path = 'datasets'
        os.makedirs(datasets_path, exist_ok=True)

        for filename in os.listdir(datasets_path):
            if filename.endswith('.json'):
                filepath = os.path.join(datasets_path, filename)
                try:
                    with open(filepath, 'r') as f:
                        dataset_name = filename.split('.')[0]
                        datasets[dataset_name] = json.load(f)
                except Exception as e:
                    print(f"Error loading dataset {filename}: {e}")
        
        return datasets

    def generate_response(self, query: str, memory: ConversationMemory) -> str:
        try:
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "system", "content": f"Available datasets: {', '.join(self.datasets.keys())}"},
                {"role": "system", "content": memory.get_conversation_context()}
            ]

            for dataset_name, content in self.datasets.items():
                messages.append({
                    "role": "system",
                    "content": f"Dataset for {dataset_name}: {json.dumps(content)}"
                })

            messages.append({"role": "user", "content": query})

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I encountered an error: {e}"

    def get_system_prompt(self):
        raise NotImplementedError("Subclasses must implement this")

# ===================== Specialized Agents =====================

class FoodAgent(BaseAgent):
    def get_system_prompt(self):
        return """
        You are a helpful food and restaurant assistant.
        Assist with orders, menus, dietary needs, and be friendly and informative.
        """

class SportsAgent(BaseAgent):
    def get_system_prompt(self):
        return """
        You are a sports assistant. Explain rules, give match info, and help with sports-related queries.
        """

class GeneralAgent(BaseAgent):
    def get_system_prompt(self):
        return """
        You are a general assistant for various topics not covered by food or sports.
        Be helpful and versatile.
        """

# ===================== Router =====================

class LLMTeacher:
    def __init__(self):
        self.students = {
            'food': FoodAgent(),
            'sports': SportsAgent(),
            'general': GeneralAgent()
        }

    def route_query(self, query: str) -> Dict[str, Any]:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Classify this query as: food, sports, or general."},
                    {"role": "user", "content": query}
                ],
                max_tokens=10
            )
            category = response.choices[0].message.content.strip().lower()
            if category not in self.students:
                category = 'general'
            return {
                'agent': self.students[category],
                'category': category
            }
        except Exception as e:
            print(f"Routing failed: {e}")
            return {
                'agent': self.students['general'],
                'category': 'general'
            }

# ===================== Final Chatbot API Handler =====================

class PreorderAgent:
    def __init__(self):
        self.teacher = LLMTeacher()
        self.memory = ConversationMemory()
    
    def process_order(self, query: str, memory_input: list):
        # Optional: Load existing memory if sent from frontend
        if memory_input:
            self.memory.memory = memory_input

        routing_result = self.teacher.route_query(query)
        agent = routing_result['agent']
        response = agent.generate_response(query, self.memory)
        self.memory.add_interaction(query, response)
        return {
            "response": response,
            "memory": self.memory.memory,
            "category": routing_result['category']
        }
