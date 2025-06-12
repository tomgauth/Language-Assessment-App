import streamlit as st
import sys
import os

# Ensure the parent directory is in the path so we can import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.transcription import get_audio_duration

st.title("Audio Duration Tester")

audio_data = st.audio_input("Upload or record audio")

if audio_data is not None:
    # Handle both BytesIO and bytes
    if hasattr(audio_data, "getvalue"):
        audio_bytes = audio_data.getvalue()
    else:
        audio_bytes = audio_data

    try:
        duration = get_audio_duration(audio_bytes)
        st.success(f"Audio duration: {duration:.2f} minutes")
    except Exception as e:
        st.error(f"Error calculating duration: {e}")
else:
    st.info("Please upload or record an audio file.")