from io import BytesIO
import numpy as np
import os
from openai import OpenAI

def process_audio(audio_frames):
    # Check if there is any audio data
    if not audio_frames:
        return "No audio data captured", 0

    # Convert the audio frames to a NumPy array and save it to a BytesIO object
    audio_data = np.concatenate([np.array(frame.to_ndarray()) for frame in audio_frames if frame is not None])
    audio_bytes = BytesIO(audio_data.tobytes())

    # Transcribe the audio using OpenAI Whisper API
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    result = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_bytes,
        language=None
    )
    transcription = result.text
    audio_duration = 0  # You may need to calculate this separately if needed

    return transcription, audio_duration