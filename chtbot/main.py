import json
import os
import openai
from typing import Dict, List, Any

# Set up OpenAI API key

class ConversationMemory:
    def __init__(self, max_history_length=10):
        """
        Initialize conversation memory
        
        Args:
            max_history_length (int): Maximum number of previous interactions to remember
        """
        self.memory = []
        self.max_history_length = max_history_length
    
    def add_interaction(self, user_query: str, bot_response: str):
        """
        Add a new interaction to the memory
        
        Args:
            user_query (str): User's input
            bot_response (str): Bot's response
        """
        # Add new interaction
        self.memory.append({
            "user": user_query,
            "bot": bot_response
        })
        
        # Trim memory if it exceeds max length
        if len(self.memory) > self.max_history_length:
            self.memory = self.memory[-self.max_history_length:]
    
    def get_conversation_context(self) -> str:
        """
        Generate a context string from conversation history
        
        Returns:
            str: Formatted conversation history
        """
        context = "Conversation History:\n"
        for interaction in self.memory:
            context += f"User: {interaction['user']}\n"
            context += f"Bot: {interaction['bot']}\n"
        return context

class LLMTeacher:
    def __init__(self):
        self.students = {
            'food_agent': FoodAgent(),
            'sports_agent': SportsAgent(),
            'general_agent': GeneralAgent()
        }
    
    def route_query(self, user_query: str) -> Dict[str, Any]:
        """
        Determine which agent should handle the query
        Uses OpenAI to classify and route the query
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": """
                        You are an expert query router for an intelligent chatbot.
                        Classify the user's query into one of these categories:
                        1. food (ordering food, menu, dietary needs, restaurants)
                        2. sports (match details, rules, game moments)
                        3. general (anything else not covered by above categories)
                        
                        Respond ONLY with the category name.
                        """
                    },
                    {
                        "role": "user", 
                        "content": user_query
                    }
                ],
                max_tokens=10
            )
            
            category = response.choices[0].message.content.strip().lower()
            
            # Fallback mechanism
            if category not in self.students:
                category = 'general_agent'
            
            return {
                'agent': self.students[f'{category}_agent'],
                'category': category
            }
        
        except Exception as e:
            print(f"Routing error: {e}")
            return {
                'agent': self.students['general_agent'],
                'category': 'general'
            }

class BaseAgent:
    def __init__(self):
        self.datasets = self.load_datasets()
    
    def load_datasets(self):
        """Load all datasets from the datasets folder"""
        datasets = {}
        datasets_path = 'datasets'
        
        # Ensure datasets folder exists
        os.makedirs(datasets_path, exist_ok=True)
        
        # Load all JSON files in the datasets folder
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
        """Generate response using OpenAI with dataset context and conversation history"""
        try:
            # Prepare context messages
            context_messages = [
                {
                    "role": "system", 
                    "content": self.get_system_prompt()
                },
                {
                    "role": "system",
                    "content": f"Available datasets: {', '.join(self.datasets.keys())}"
                },
                {
                    "role": "system",
                    "content": memory.get_conversation_context()
                }
            ]
            
            # Add dataset contexts
            for dataset_name, dataset_content in self.datasets.items():
                context_messages.append({
                    "role": "system",
                    "content": f"Dataset for {dataset_name}: {json.dumps(dataset_content)}"
                })
            
            # Add user query
            context_messages.append({
                "role": "user", 
                "content": query
            })
            
            # Generate response
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=context_messages,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I encountered an error: {e}"
    
    def get_system_prompt(self):
        """Define system prompt for the agent"""
        raise NotImplementedError("Subclasses must implement this method")

class FoodAgent(BaseAgent):
    def get_system_prompt(self):
        return """
        You are a helpful food and restaurant assistant.
        Key responsibilities:
        - Assist with food orders
        - Provide menu information
        - Address dietary restrictions and allergies
        - Recommend meals
        - Provide nutritional information
        
        Important guidelines:
        - Use conversation history to provide context-aware responses
        - Reference available datasets for accurate information
        - Be friendly, informative, and prioritize user safety
        - Remember previous queries to offer more personalized assistance
        """

class SportsAgent(BaseAgent):
    def get_system_prompt(self):
        return """
        You are a comprehensive sports information assistant.
        Key responsibilities:
        - Explain sports rules and regulations
        - Provide match details and key moments
        - Discuss team and player information
        - Answer questions about sports events
        - Offer insights into game strategies
        
        Important guidelines:
        - Use conversation history to provide context-aware responses
        - Reference available datasets for accurate information
        - Be knowledgeable, descriptive, and exciting
        - Connect current query with previous conversation context
        """

class GeneralAgent(BaseAgent):
    def get_system_prompt(self):
        return """
        You are a versatile assistant capable of handling various queries.
        Key responsibilities:
        - Answer questions across different topics
        - Provide information from available datasets
        - Offer helpful and informative responses
        - Direct users to appropriate resources
        
        Important guidelines:
        - Use conversation history to understand context
        - Refer to available datasets for accurate information
        - Be helpful, clear, and adaptable
        - Maintain conversational continuity
        """

class SportsFanChatbot:
    def __init__(self):
        self.teacher = LLMTeacher()
        self.memory = ConversationMemory()
    
    def interact(self):
        print("Welcome to the Intelligent Chatbot!")
        print("Type 'exit' to end the conversation.")
        
        while True:
            user_query = input("\nYou: ")
            
            if user_query.lower() == 'exit':
                break
            
            # Route query to appropriate agent
            routing_result = self.teacher.route_query(user_query)
            agent = routing_result['agent']
            
            # Generate response
            response = agent.generate_response(user_query, self.memory)
            
            # Add interaction to memory
            self.memory.add_interaction(user_query, response)
            
            print(f"\nChatbot: {response}")

def main():
   
  
    
    # Run chatbot
    chatbot = SportsFanChatbot()
    chatbot.interact()

if __name__ == "__main__":
    main()