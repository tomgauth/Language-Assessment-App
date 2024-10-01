from streamlit_mic_recorder import mic_recorder
import streamlit as st
import io
from pydub import AudioSegment
from openai import OpenAI
import dotenv
import os


def get_audio_duration(audio_bytes):
    # Use pydub to figure out the audio format
    try:
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        duration_in_minutes = len(audio_segment) / (1000 * 60)  # Convert milliseconds to minutes
        return duration_in_minutes
    except Exception as e:
        print(f"Error decoding audio: {e}")
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
    audio = mic_recorder(start_prompt=start_prompt, stop_prompt=stop_prompt, just_once=just_once,
                         use_container_width=use_container_width, key=key)
    new_output = False
    if audio is None:
        output = None, None
    else:
        id = audio['id']
        new_output = (id > st.session_state._last_speech_to_text_transcript_id)
        if new_output:
            output = None
            st.session_state._last_speech_to_text_transcript_id = id
            audio_bio = io.BytesIO(audio['bytes'])
            audio_bio.name = 'audio.mp3'
            audio_bytes = audio["bytes"]
             # Try calculating the duration
            try:
                duration_in_minutes = get_audio_duration(audio_bytes)
            except Exception as e:
                print(f"Error calculating duration: {e}")

            print(f"Duration in minutes: {duration_in_minutes}")

            success = False
            err = 0
            while not success and err < 3:  # Retry up to 3 times in case of OpenAI server error.
                try:
                    transcript = st.session_state.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_bio,
                        language=language
                    )
                except Exception as e:
                    print(str(e))  # log the exception in the terminal
                    err += 1
                else:
                    success = True
                    output = transcript.text
                    st.session_state._last_speech_to_text_transcript = output
        elif not just_once:
            output = st.session_state._last_speech_to_text_transcript
        else:
            output = None

    if key:
        st.session_state[key + '_output'] = output
    if new_output and callback:
        callback(*args, **(kwargs or {}))
    return output, duration_in_minutes