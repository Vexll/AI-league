# File: report_chatbot/main.py

import openai
import json
import datetime
import os
import base64
import io
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from typing import List, Dict, Optional, Any, Union


class EmergencyReportingBot:
    def __init__(self):
        """Initialize the Emergency Reporting Bot"""
        # Set up OpenAI API key
        self.api_key = "YOUR_OPENAI_API_KEY"
        openai.api_key = self.api_key

        # Initialize image captioning model
        self.processor = BlipProcessor.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )
        self.image_model = BlipForConditionalGeneration.from_pretrained(
            "Salesforce/blip-image-captioning-base"
        )

        # Create reports directory if it doesn't exist
        self.reports_dir = (
            r"C:\Users\Hatim\Desktop\Ai_Legue\report_chatbot\reoprts_json"
        )
        os.makedirs(self.reports_dir, exist_ok=True)

        # Define system prompt
        self.system_prompt = """
        أنت مساعد ذكي مخصص لتلقي بلاغات الطوارئ داخل الملاعب، يعمل من خلال واجهة محادثة تفاعلية (مثل واتساب أو تيليجرام). وظيفتك هي:
        - استقبال البلاغات من المستخدمين.
        - التفاعل معهم لفهم الحالة (مثل إغماء، سقوط، شيء غريب).
        - طلب الموقع (بصورة أو كتابة).
        - تأكيد استلام البلاغ بلغة لبقة.

        تتكلم عربي وإنجليزي. حدد لغة المستخدم من رسائله ورد عليه بنفس اللغة. كن ودوداً وسريع الفهم.

        You are a smart assistant dedicated to receiving emergency reports inside stadiums through a chat interface (like WhatsApp). Your job is to:
        - Understand emergencies (fainting, fallen objects, strange situations).
        - Ask for location (image or manual input).
        - Confirm the report kindly.

        Speak the same language the user uses (Arabic or English). Do not switch between languages unless the user does.

        Keep your tone polite, helpful, and human. If you're receiving an emergency report, immediately ask for location details or an image of the location.

        In emergency situations such as "someone fainted" (أغمي عليه شخص), immediately respond by requesting location information (send location, describe nearby signs, or take a picture).

        When location is provided, confirm receipt of the report with a message like "Your report has been sent. Stay safe" (تم ارسال البلاغ دمتم بسلام).
        """

    def decode_image(self, image_data: str) -> Optional[Image.Image]:
        """Decode base64 image data to PIL Image"""
        try:
            # Remove data URL prefix if present
            if "base64," in image_data:
                image_data = image_data.split("base64,")[1]

            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            return image
        except Exception as e:
            print(f"Error decoding image: {str(e)}")
            return None

    def analyze_image(self, image: Image.Image) -> str:
        """Analyze image using BLIP model"""
        try:
            inputs = self.processor(image, return_tensors="pt")
            out = self.image_model.generate(**inputs)
            caption = self.processor.decode(out[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            return "Unable to analyze the image content."

    def generate_response(self, conversation: List[Dict[str, str]]) -> str:
        """Generate response using GPT model"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # or any other model you prefer
                messages=conversation,
                temperature=0.7,
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "عذراً، حدث خطأ في معالجة طلبك. حاول مرة أخرى لاحقاً. (Sorry, there was an error processing your request. Please try again later.)"

    def save_report(self, data: Dict[str, Any]) -> str:
        """Save report to JSON file"""
        timestamp = datetime.datetime.now().isoformat().replace(":", "-")
        report_path = os.path.join(self.reports_dir, f"report_{timestamp}.json")

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return report_path

    def process_message(
        self,
        message: str,
        image_data: Optional[str] = None,
        conversation_history: List[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Process incoming message and generate a response

        Args:
            message: User's text message
            image_data: Optional base64 encoded image data
            conversation_history: Previous conversation history

        Returns:
            Dictionary containing the response and updated conversation
        """
        # Initialize conversation if not provided
        if conversation_history is None:
            conversation_history = []

        # Create full conversation with system prompt
        full_conversation = [{"role": "system", "content": self.system_prompt}]
        full_conversation.extend(conversation_history)

        # Add user's new message
        if message:
            full_conversation.append({"role": "user", "content": message})

        # Process image if provided
        image_caption = None
        if image_data:
            image = self.decode_image(image_data)
            if image:
                image_caption = self.analyze_image(image)
                # Add image description to conversation
                full_conversation.append(
                    {
                        "role": "user",
                        "content": f"[Image uploaded] Description: {image_caption}",
                    }
                )

        # Generate AI response
        ai_response = self.generate_response(full_conversation)

        # Add AI response to conversation
        full_conversation.append({"role": "assistant", "content": ai_response})

        # Create report data
        report_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_message": message,
            "image_provided": bool(image_data),
            "image_caption": image_caption,
            "ai_response": ai_response,
            "conversation": full_conversation[
                1:
            ],  # Exclude system prompt from saved conversation
        }

        # Save report
        report_path = self.save_report(report_data)

        # Return response
        return {
            "response": ai_response,
            "conversation": full_conversation[
                1:
            ],  # Return conversation without system prompt
            "report_saved": True,
            "report_path": report_path,
        }
