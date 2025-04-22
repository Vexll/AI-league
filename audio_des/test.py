from processor import AudioDescriptionProcessor  # Replace with actual module if needed

# Path to your sample video
video_path = "sample_video.mp4"  # Make sure this file exists in the same directory or provide full path

# Initialize processor
processor = AudioDescriptionProcessor()

# Step 1: Extract frames
frames = processor.extract_frames(video_path)

# Optional: limit to first few frames to reduce cost & speed up test
test_frames = frames[:5] if len(frames) > 5 else frames

# Step 2: Analyze frames with Vision model
descriptions = processor.analyze_frames(test_frames)

print("\n=== Frame Descriptions ===")
for desc in descriptions:
    print(f"Frame {desc['frame_number']}: {desc['description']}")

# Step 3: Generate audio description narrative
result = processor.generate_audio_description(descriptions)

# Print narrative
print("\n=== Narrative ===")
print(result.get("narrative"))
