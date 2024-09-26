import whisper
import tempfile
import os
from pydub import AudioSegment


# Load Whisper model
model = whisper.load_model("base")  # You can switch between "tiny", "base", "small", etc.

def transcribe_audio(audio_file):
    # Save the uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(audio_file.read())
        temp_audio_path = tmp_file.name

    # Transcribe the audio using Whisper
    result = model.transcribe(temp_audio_path)

    # Get the duration of the audio using pydub
    audio = AudioSegment.from_file(temp_audio_path)
    audio_duration = len(audio) / 1000  # Duration in seconds
    
    # Clean up the temporary file
    os.remove(temp_audio_path)

    # Return the transcription and duration
    return result['text'], audio_duration


#from faster_whisper import WhisperModel
#import tempfile
#import os
#
## Load Whisper model
#model = WhisperModel("base", device="cpu", compute_type="int8")
#
#def transcribe_audio(audio_file):
#    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
#        tmp_file.write(audio_file.read())
#        temp_audio_path = tmp_file.name
#
#    segments, info = model.transcribe(temp_audio_path)
#    transcription = " ".join([segment.text for segment in segments])
#    
#    os.remove(temp_audio_path)
#
#    return transcription, info.duration  # Return the transcription and audio duration

