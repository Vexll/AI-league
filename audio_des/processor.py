import os
import tempfile
import traceback
from typing import Dict, Any
import cv2
import numpy as np
import logging
import json
import base64
import requests
import time
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioDescriptionProcessor:
    def __init__(self):
        """
        Initialize the audio description processor with OpenAI client
        """
        # Get API key from environment variables or use the one provided
        self.api_key = "openai_api_key"
        openai.api_key = self.api_key
        self.vision_model = "gpt-4.1-mini"  # OpenAI's vision model   (gpt-4-vision-preview)
        self.text_model = "gpt-4.1-mini"  # OpenAI's text model for narrative generation
        
        logger.info("OpenAI client initialized")

    def extract_frames(self, video_path: str, sample_rate: int = 24) -> list:
        """
        Extract frames from video at specified sampling rate
        
        Args:
            video_path: Path to the video file
            sample_rate: Extract every Nth frame
            
        Returns:
            List of extracted frames as numpy arrays
        """
        try:
            frames = []
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Calculate appropriate sampling rate based on video length
            # For longer videos, we want fewer samples
            if duration > 60:  # If longer than 1 minute
                # Sample one frame every 2 seconds
                sample_rate = int(fps * 2)
            elif duration > 30:  # If longer than 30 seconds
                # Sample one frame every second
                sample_rate = int(fps)
            else:
                # For short videos, sample every half second
                sample_rate = max(1, int(fps / 2))
            
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % sample_rate == 0:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Extracted {len(frames)} frames from video with {fps} fps, duration: {duration:.2f}s")
            return frames
        except Exception as e:
            logger.error(f"Error extracting frames: {str(e)}")
            raise
    
    def _encode_image_to_base64(self, image_array):
        """Convert a numpy array image to base64 encoded string"""
        success, encoded_image = cv2.imencode('.jpg', cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR))
        if not success:
            return None
        return base64.b64encode(encoded_image.tobytes()).decode('utf-8')
    
    def analyze_frames(self, frames: list) -> list:
        """
        Generate descriptions for the extracted frames using OpenAI's vision model
        
        Args:
            frames: List of video frames
            
        Returns:
            List of descriptions for each analyzed frame
        """
        frame_descriptions = []
        
        try:
            for i, frame in enumerate(frames):
                if i % 10 == 0:
                    logger.info(f"Processing frame {i+1}/{len(frames)}")
                
                # Encode image to base64
                base64_image = self._encode_image_to_base64(frame)
                
                if not base64_image:
                    logger.warning(f"Failed to encode frame {i}")
                    continue
                
                # Use OpenAI's vision model to analyze the frame
                response = openai.ChatCompletion.create(
                    model=self.vision_model,
                messages = [
    {
        "role": "system",
        "content": (
            "You are a sports video analysis expert. Analyze the image with a focus on identifying key details relevant to football or sports action. "
            "Describe the scene in 1–2 sentences, including the players' positions, movements, ball location, play type (e.g., pass, tackle, goal attempt), "
            "and any notable context such as crowd reaction, referee involvement, or score indicators. Be precise, action-focused, and avoid generic descriptions."
        )
    },
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What is happening in this frame? Describe the key football/sport action clearly."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]
    }
]
                )
                
                description = response.choices[0].message.content
                
                frame_descriptions.append({
                    "frame_number": i,
                    "timestamp": i / len(frames),  # Normalized timestamp (0-1)
                    "description": description
                })
                
                # Rate limit to avoid hitting OpenAI's rate limits
                if i < len(frames) - 1:
                    time.sleep(0.5)
            
            return frame_descriptions
        except Exception as e:
            logger.error(f"Error analyzing frames with OpenAI: {str(e)}")
            raise
    
    def generate_audio_description(self, frame_descriptions: list) -> Dict[str, Any]:
        """
        Generate consolidated audio description from frame analysis using GPT-4
        
        Args:
            frame_descriptions: List of frame descriptions
            
        Returns:
            Dictionary with audio description data
        """
        try:
            # Prepare descriptions for GPT-4
            descriptions_text = "\n".join([
                f"Frame {desc['frame_number']} ({desc['timestamp']:.2f}): {desc['description']}"
                for desc in frame_descriptions
            ])
            
            # Use GPT-4 to create a coherent narrative
            response = openai.ChatCompletion.create(
                model=self.text_model,
           messages = [
    {
        "role": "system",
        "content": (
            "You are a professional audio description writer for sports and action videos. Your task is to transform a sequence of frame descriptions into a coherent, "
            "engaging, and natural-sounding audio narration script. Focus on visual storytelling—highlight key actions, transitions, and essential visual details without redundancy. "
            "The script should be concise, smooth, and suitable for real-time narration. Maintain flow, avoid over-explaining, and prioritize clarity and pacing."
        )
    },
    {
        "role": "user",
        "content": f"Based on the following frame-by-frame video descriptions, generate a polished audio narration script:\n\n{descriptions_text}\n\nEnsure the narrative flows well and is suitable for voiceover in a sports context."
    }
]
            )
            
            narrative = response.choices[0].message.content
            
            # Create timestamps for the narrative
            scenes = self._segment_into_scenes(frame_descriptions)
            
            return {
                "status": "success",
                "raw_descriptions": frame_descriptions,
                "scenes": scenes,
                "narrative": narrative
            }
        except Exception as e:
            logger.error(f"Error generating audio description: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _segment_into_scenes(self, frame_descriptions: list) -> list:
        """
        Segment the frame descriptions into coherent scenes
        
        Args:
            frame_descriptions: List of frame descriptions
            
        Returns:
            List of scene descriptions with timestamps
        """
        # If we have too few descriptions, each is its own scene
        if len(frame_descriptions) <= 3:
            return [
                {
                    "start_time": desc["timestamp"],
                    "end_time": desc["timestamp"],
                    "description": desc["description"]
                }
                for desc in frame_descriptions
            ]
        
        # Use OpenAI to identify scene boundaries
        descriptions_text = "\n".join([
            f"Frame {desc['frame_number']} ({desc['timestamp']:.2f}): {desc['description']}"
            for desc in frame_descriptions
        ])
        
        try:
            response = openai.ChatCompletion.create(
                model=self.text_model,
              messages = [
    {
        "role": "system",
        "content": (
            "You are a professional video scene segmentation expert. Your task is to analyze a sequence of frame descriptions and detect major scene changes. "
            "A 'scene' is defined as a continuous segment where the visual action, setting, or context remains consistent. "
            "Identify the start and end frame numbers for each distinct scene. Each scene should represent a clear transition in time, location, or activity. "
            "Be precise and avoid over-segmentation. Your output must be a well-structured JSON array, where each object includes: 'start_frame', 'end_frame', and a concise 'scene_description'."
        )
    },
    {
        "role": "user",
        "content": f"Analyze the following frame descriptions and return a list of distinct scenes:\n\n{descriptions_text}\n\nOutput a JSON array formatted as:\n[\n  {{\"start_frame\": int, \"end_frame\": int, \"scene_description\": string}},\n  ...\n]"
    }
]
            )
            
            scene_data = json.loads(response.choices[0].message.content)
            
            # Process scene data
            scenes = []
            for scene in scene_data.get("scenes", []):
                start_frame = max(0, min(scene.get("start_frame", 0), len(frame_descriptions) - 1))
                end_frame = max(0, min(scene.get("end_frame", len(frame_descriptions) - 1), len(frame_descriptions) - 1))
                
                scenes.append({
                    "start_time": frame_descriptions[start_frame]["timestamp"],
                    "end_time": frame_descriptions[end_frame]["timestamp"],
                    "description": scene.get("scene_description", "")
                })
            
            return scenes
            
        except Exception as e:
            logger.error(f"Error segmenting scenes: {str(e)}")
            # Fallback: simple scene segmentation
            scenes = []
            current_scene = {
                "start_time": frame_descriptions[0]["timestamp"],
                "end_time": frame_descriptions[0]["timestamp"],
                "description": frame_descriptions[0]["description"]
            }
            
            for i in range(1, len(frame_descriptions)):
                # Simple heuristic: if descriptions are very different, it might be a new scene
                current_scene["end_time"] = frame_descriptions[i]["timestamp"]
                
                # Every third frame, start a new scene (simple fallback)
                if i % 3 == 0:
                    scenes.append(current_scene)
                    current_scene = {
                        "start_time": frame_descriptions[i]["timestamp"],
                        "end_time": frame_descriptions[i]["timestamp"],
                        "description": frame_descriptions[i]["description"]
                    }
            
            # Add the last scene
            scenes.append(current_scene)
            return scenes
    
    def save_results(self, output_path: str, results: Dict[str, Any]) -> str:
        """
        Save the audio description results to a file
        
        Args:
            output_path: Path to save the results
            results: Audio description results
            
        Returns:
            Path to the saved file
        """
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        return output_path
    
    def handle_flutter_upload(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle video upload from Flutter frontend
        
        Args:
            video_data: Dictionary containing video file information
            
        Returns:
            Dictionary with audio description results
        """
        try:
            # Extract video from request
            video_file = video_data.get("file")
            if not video_file:
                return {"status": "error", "message": "No video file provided"}
            
            # Create a temporary file to process
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                temp_video_path = temp_video.name
                # Write the video data to the temporary file
                if isinstance(video_file, bytes):
                    temp_video.write(video_file)
                else:
                    # Assuming video_file is a path or file-like object
                    with open(video_file, 'rb') as f:
                        temp_video.write(f.read())
            
            # Process the video
            logger.info(f"Starting video processing: {temp_video_path}")
            frames = self.extract_frames(temp_video_path)
            logger.info(f"Frame extraction complete. Analyzing {len(frames)} frames")
            frame_descriptions = self.analyze_frames(frames)
            logger.info("Frame analysis complete. Generating audio description")
            audio_description = self.generate_audio_description(frame_descriptions)
            logger.info("Audio description generation complete")
            
            # Create output directory if it doesn't exist
            output_dir = os.path.join(os.path.dirname(temp_video_path), "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # Save results to file
            output_path = os.path.join(output_dir, f"{os.path.basename(temp_video_path)}_description.json")
            self.save_results(output_path, audio_description)
            logger.info(f"Results saved to {output_path}")
            
            # Clean up the temporary file
            os.unlink(temp_video_path)
            
            return {
                "status": "success",
                "description": audio_description["narrative"],
                "scenes": audio_description.get("scenes", []),
                "output_file": output_path
            }
        
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            logger.error(traceback.format_exc())
            return {"status": "error", "message": str(e)}