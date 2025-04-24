import json
import os
import openai
from typing import Dict, Any

# ===================== Memory =====================


class ConversationMemory:
    def __init__(self, max_history_length=10000):
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
    def __init__(self, dataset_filename: str = None):
        self.dataset_filename = dataset_filename
        self.dataset = self.load_dataset()

    def load_dataset(self):
        if not self.dataset_filename:
            return None
        try:
            path = os.path.join("preorder_chatbot\datasets", self.dataset_filename)
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading dataset {self.dataset_filename}: {e}")
            return None

    def get_relevant_dataset_info(self):
        if self.dataset:
            return f"Dataset info: {json.dumps(self.dataset)}"
        return ""

    def generate_response(self, query: str, memory: "ConversationMemory") -> str:
        try:
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "system", "content": self.get_relevant_dataset_info()},
                {"role": "system", "content": memory.get_conversation_context()},
                {"role": "user", "content": query},
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages, max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I encountered an error: {e}"

    def get_system_prompt(self):
        raise NotImplementedError("Subclasses must implement this")


# ===================== Specialized Agents =====================


class FoodAgent(BaseAgent):
    def __init__(self):
        super().__init__("restaurants.json")

    def get_system_prompt(self):
        return "You are a helpful food and restaurant assistant."


class SportsAgent(BaseAgent):
    def __init__(self):
        super().__init__("fifa_rules.json")

    def get_system_prompt(self):
        return "You are a sports assistant for match rules and general sports info."


class GeneralAgent(BaseAgent):
    def __init__(self):
        super().__init__(None)

    def get_system_prompt(self):
        return "You are a general-purpose assistant."


class ClubHistoryAgent(BaseAgent):
    def __init__(self):
        super().__init__("Saudi Team.json")

    def get_system_prompt(self):
        return """
        You are an assistant specialized in international football clubs related to Saudi Arabia.
        Provide info on achievements, current team, FIFA ranking, and current squad.
        """


class Match_Momments(BaseAgent):
    def __init__(self):
        super().__init__("key_momments.json")

    def get_system_prompt(self):
        return """
        You are an assistant specialized in providing key moments of matches related to Saudi Arabia.
        """


class PlayerHistoryAgent(BaseAgent):
    def __init__(self):
        super().__init__("players.json")

    def get_system_prompt(self):
        return """
        You provide history for Saudi football players: club career, personal info, achievements.
        """


class ChantAgent(BaseAgent):
    def __init__(self):
        super().__init__("chant.json")

    def get_system_prompt(self):
        return """
        You describe or translate chants of the Saudi National Football Team. Include title, lyrics, and meaning.
        """


class PlaceOrderAgent(BaseAgent):
    def __init__(self):
        super().__init__(None)  # No dataset needed for order placement

    def get_system_prompt(self):
        return """
        You are an order assistant. When the user confirms they want to place an order,
        confirm their request, summarize what they want, then save the order.
        Respond with:
        - Order Summary
        - Ask for confirmation (yes/no)
        After confirmation, respond with a message like:
        "Your order has been placed successfully. Your order number is: X."
        """

    def save_order(self, order_details: str):
        order_path = "orders.json"
        if not os.path.exists(order_path):
            with open(order_path, "w") as f:
                json.dump([], f)

        with open(order_path, "r") as f:
            orders = json.load(f)

        new_order = {"order_number": len(orders) + 1, "details": order_details}
        orders.append(new_order)

        with open(order_path, "w") as f:
            json.dump(orders, f, indent=2)

        return new_order["order_number"]


# ===================== Modified LLMTeacher =====================
class LLMTeacher:
    def __init__(self):
        self.students = {
            "food": FoodAgent(),
            "sports": SportsAgent(),
            "general": GeneralAgent(),
            "club_history": ClubHistoryAgent(),
            "player_history": PlayerHistoryAgent(),
            "chants": ChantAgent(),
            "place_order": PlaceOrderAgent(),  # ✅ New
        }

    def route_query(self, query: str) -> Dict[str, Any]:
        try:
            classification_prompt = """
            Classify the query into one of the following categories:
            - food
            - sports
            - general
            - club_history
            - player_history
            - chants
            - place_order
            Just respond with the category.
            """
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": classification_prompt},
                    {"role": "user", "content": query},
                ],
                max_tokens=10,
            )
            category = response.choices[0].message.content.strip().lower()
            if category not in self.students:
                category = "general"
            return {"agent": self.students[category], "category": category}
        except Exception as e:
            print(f"Routing failed: {e}")
            return {"agent": self.students["general"], "category": "general"}


# ===================== Final Chatbot API Handler =====================
class PreorderAgent:
    def __init__(self):
        self.teacher = LLMTeacher()
        self.memory = ConversationMemory()
        self.last_order_intent = None  # For tracking orders
        self.conversations = {}

    def process_order(self, query: str, memory_input: list):
        if memory_input:
            self.memory.memory = memory_input

        routing_result = self.teacher.route_query(query)
        agent = routing_result["agent"]
        category = routing_result["category"]

        response = agent.generate_response(query, self.memory)
        self.memory.add_interaction(query, response)

        if category == "place_order":
            if "yes" in query.lower():
                # Confirming previous order
                if self.last_order_intent:
                    order_number = agent.save_order(self.last_order_intent)
                    response = f"✅ Your order has been placed successfully. Your order number is: {order_number}."
                    self.memory.add_interaction(query, response)
                    self.last_order_intent = None
            else:
                self.last_order_intent = query  # Save what the user asked to order

        return {
            "response": response,
            "memory": self.memory.memory,
            "category": category,
        }
