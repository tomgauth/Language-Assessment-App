import requests
import random
import os
import uuid
from elevenlabs import VoiceSettings
from elevenlabs import play
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
load_dotenv() 


# Define the Eleven Labs API Key
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")

client = ElevenLabs(api_key=ELEVEN_LABS_API_KEY)

# TODO: gender and age specific voices

# List of Voice IDs to choose from
VOICE_IDS = [
    "F1toM6PcP54s45kOOAyV", # Mademoiselle French
    "70QakWcpr1EAWDdnypvd", # 35 yo North East Parisian smoker "Meuf"
    "ufWL6S7fryuQBD3Y5J3I", # Jeremy Conversational
    "5Qfm4RqcAer0xoyWtoHC", # Maxime - French Young male
    "TQaDhGYcKI0vrQueAmVO", # Lucien
    "ohItIVrXTBI80RrUECOD" # Guillaume - Narration
    # Add as many as you want
]

selected_voice_id = random.choice(VOICE_IDS)

def generate_audio(text):
    # Generate a unique filename with the .mp3 extension
    filename = f"{uuid.uuid4()}.mp3"
    save_dir = ".streamlit/static/generated_audio"
    os.makedirs(save_dir, exist_ok=True)  # Ensure the directory exists
    file_path = os.path.join(save_dir, filename)


    # Call the Eleven Labs API for text-to-speech conversion
    response = client.text_to_speech.convert(
        voice_id=selected_voice_id,
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",  # Use turbo model for low latency
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )

    with open(file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    # Return a URL path that Streamlit can serve
    return f".streamlit/static/generated_audio/{filename}"