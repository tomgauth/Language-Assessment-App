from io import BytesIO
import numpy as np
import whisper

# Load Whisper model
model = whisper.load_model("base")

def process_audio(audio_frames):
    # Check if there is any audio data
    if not audio_frames:
        return "No audio data captured", 0

    # Convert the audio frames to a NumPy array and save it to a BytesIO object
    audio_data = np.concatenate([np.array(frame.to_ndarray()) for frame in audio_frames if frame is not None])
    audio_bytes = BytesIO(audio_data.tobytes())

    # Transcribe the audio using Whisper
    result = model.transcribe(audio_bytes, fp16=False)
    transcription = result["text"]
    audio_duration = result["duration"]

    return transcription, audio_duration