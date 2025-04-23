import json
import os
import openai
from typing import Dict, Any

# ===================== Memory =====================

class ConversationMemory:
    def __init__(self, max_history_length=10_000):
        self.memory = []
        self.max_history_length = max_history_length
        self.length = 0
    
    def add_interaction(self, user_query: str, bot_response: str):
        self.memory.append({"user": user_query, "bot": bot_response})
        self.length += len(str({"user": user_query, "bot": bot_response}))
        if self.length > self.max_history_length:
            self.length -= len(str(self.memory[0]))
            self.memory = self.memory[1:]

    
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

class ReportingAgent(BaseAgent):
    def get_system_prompt(self):
        return """
You are a report assistant
You will receive a concern or report from a customer, tell them that it is reported and will be fixed soon, etc.
"""

class GeneralAgent(BaseAgent):
    def get_system_prompt(self):
        return """
You are a general assistant for various topics not covered by food or sports.
Be helpful and versatile.
"""
class ClubHistoryAgent(BaseAgent):
    def get_system_prompt(self):
        return """
        You are an assistant specialized in international football clubs related to Saudi Arabia.
        You provide information on:
        - Major Historical Achievements
        - Current Team Highlights
        - Recent FIFA Ranking and Performance Trends
        - Current Squad Information
        Be factual and refer only to the relevant club data.
        """

class PlayerHistoryAgent(BaseAgent):
    def get_system_prompt(self):
        return """
        You are an assistant that provides international club history for Saudi football players.
        Provide:
        - Personal Info
        - Club Career (current and past clubs)
        - Achievements (trophies, records, international appearances)
        """

class ChantAgent(BaseAgent):
    def get_system_prompt(self):
        return """
        You are an assistant that handles Saudi Arabia National Football Team chants.
        You describe the chant or translate it for non-Arabic speakers.
        Format responses with:
        - Chant Title
        - Lyrics
        - Description or Translation
        Be culturally sensitive and engaging.
        """

# ===================== Modified LLMTeacher =====================

class LLMTeacher:
    def __init__(self):
        self.students = {
            'food': FoodAgent(),
            'sports': SportsAgent(),
            'general': GeneralAgent(),
            'club_history': ClubHistoryAgent(),
            'player_history': PlayerHistoryAgent(),
            'chants': ChantAgent()
        }

    def route_query(self, query: str) -> Dict[str, Any]:
        try:
            classification_prompt = """
            Classify the query into one of the following categories:
            - food
            - sports
            - general
            - club_history (international football clubs related to Saudi Arabia)
            - player_history (Saudi player international club history)
            - chants (Saudi national team chants)
            Just respond with the category.
            """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": classification_prompt},
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
