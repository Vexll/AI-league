# In /backend/main.py

from fastapi import FastAPI
from chatbot.main import PreorderAgent
from chatbot.main import FansAssistant
from roadmap.roadmap_generator import RoadmapGenerator
from audio_description.processor import AudioDescriptionProcessor

app = FastAPI()

# Initialize components
preorder_bot = PreorderAgent()
fans_bot = FansAssistant()
roadmap_gen = RoadmapGenerator()
audio_processor = AudioDescriptionProcessor()

@app.post("/preorder/chat")
async def handle_preorder(request: dict): #done
    response = PreorderAgent.process_order(request["query"], request["memory"])
    return response

@app.post("/fans/chat") 
async def handle_fans_query(request: dict): # function take input : query and output LLM response 
    response = fans_bot.generate_response(request["query"], request["memory"])
    return response

@app.post("/roadmap/generate")
async def generate_roadmap(request: dict):
    user_inputs = process_flutter_input(request["data"]) 
    image =  roadmap_gen(user_input) # input: json file , output : image 
    return image 

@app.post("/audio/process")
async def process_audio(request: dict):#input : video , output : audio
    return audio_processor.handle_flutter_upload(request["video"])