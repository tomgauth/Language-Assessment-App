from faster_whisper import WhisperModel
import tempfile
import os

# Load Whisper model
model = WhisperModel("base", device="cpu", compute_type="int8")

def transcribe_audio(audio_file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(audio_file.read())
        temp_audio_path = tmp_file.name

    segments, info = model.transcribe(temp_audio_path)
    transcription = " ".join([segment.text for segment in segments])
    
    os.remove(temp_audio_path)

    return transcription, info.duration  # Return the transcription and audio duration
