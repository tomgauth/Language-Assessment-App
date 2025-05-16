from streamlit_mic_recorder import mic_recorder
import streamlit as st
import io
from pydub import AudioSegment
from openai import OpenAI
import dotenv
import os


def convert_audio_to_wav(audio_bytes):
    try:
        audio_bio = io.BytesIO(audio_bytes)
        audio_bio.name = 'audio.wav'  # Assign a name to the in-memory file
        return audio_bio
    except Exception as e:
        print(f"Error converting audio to WAV: {e}")
        return None

def get_audio_duration(audio_bytes):
    try:
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        duration_in_minutes = len(audio_segment) / (1000 * 60)  # Convert milliseconds to minutes
        return duration_in_minutes
    except Exception as e:
        print(f"Error calculating audio duration: {e}")
        return 0.1  # Default duration if error occurs


def transcribe_audio(openai_api_key, audio_bio, language=None):
    try:
        client = OpenAI(api_key=openai_api_key)
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_bio,
            language=language
        )
        return result
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None


def whisper_stt(openai_api_key=None, start_prompt="▶️ Start recording", stop_prompt="⏹️ Stop recording", just_once=False,
               use_container_width=False, language=None, callback=None, args=(), kwargs=None, key=None):
    if not 'openai_client' in st.session_state:
        dotenv.load_dotenv()
        st.session_state.openai_client = OpenAI(api_key=openai_api_key or os.getenv('OPENAI_API_KEY'))
    if not '_last_speech_to_text_transcript_id' in st.session_state:
        st.session_state._last_speech_to_text_transcript_id = 0
    if not '_last_speech_to_text_transcript' in st.session_state:
        st.session_state._last_speech_to_text_transcript = None
    if key and not key + '_output' in st.session_state:
        st.session_state[key + '_output'] = None

    # Record audio using mic_recorder
    audio = mic_recorder(start_prompt=start_prompt, stop_prompt=stop_prompt, just_once=just_once,
                         use_container_width=use_container_width, key=key)
    if audio is None:
        return None, 0.1  # Return a default duration if no audio recorded
    
    audio_bytes = audio["bytes"]
    
    # Convert audio to WAV format
    audio_bio = convert_audio_to_wav(audio_bytes)
    
    if audio_bio:
        # Measure audio duration
        duration_in_minutes = get_audio_duration(audio_bytes)
        
        # Transcribe audio using OpenAI Whisper API
        client = OpenAI(api_key=openai_api_key)
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_bio,
            language=None
        )
        transcription = result.text
        
        # Store the transcription in session state
        if transcription:
            st.session_state['_last_speech_to_text_transcript'] = transcription
            return transcription, duration_in_minutes
        else:
            return None, duration_in_minutes
    else:
        return None, 0.1  # Return a default duration if conversion fails