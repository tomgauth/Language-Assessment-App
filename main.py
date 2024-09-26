import streamlit as st
from services.transcription import transcribe_audio  # Import the transcription service
from services.nlp_analysis import analyze_lemmas_and_frequency  # Import existing functions
from services.ai_analysis import evaluate_naturalness  # Import the AI evaluation function
from services.test_data import get_A2_sample_text  # Import the sample test text

# Page Title
st.title("Language Proficiency Assessment App")

# Explanation
st.write("""
    This app helps you assess your language proficiency through audio transcription and text analysis. 
    You can either upload an audio file to transcribe or input text directly for analysis.
""")

# Initialize session state for transcription if it's not already stored
if 'transcription' not in st.session_state:
    st.session_state['transcription'] = ""

# Audio Upload and Transcription
audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])
transcribed_text = ""

# Default value for duration_in_minutes in case there's no audio
duration_in_minutes = 1  # You can also allow the user to input this manually if needed

if audio_file:
    # If audio is uploaded, display the Transcribe button
    if st.button("Transcribe"):
        st.write("Transcribing audio...")
        transcription, audio_duration = transcribe_audio(audio_file)  # Get transcription and duration
        st.session_state['transcription'] = transcription
        duration_in_minutes = audio_duration / 60  # Convert duration to minutes

# Text Input (modifiable or prefilled with transcribed text)
if st.session_state['transcription']:
    paragraph = st.text_area("Transcription:", value=st.session_state['transcription'], height=200)
else:
    paragraph = st.text_area("Enter a paragraph (up to 300 words):", height=200)

# Analyze button (shown after audio or text input)
if paragraph:
    if st.button("Analyze"):
        # Call the analysis functions
        vocabulary_score, total_lemmas, unique_lemmas, median_frequency, fluency_score, wpm = analyze_lemmas_and_frequency(
            paragraph, duration_in_minutes)

        st.write("## Analysis Report")
        st.write(f"**Total Lemmas:** {total_lemmas}")
        st.write(f"**Unique Lemmas:** {unique_lemmas}")
        st.write(f"**Median Frequency of Words:** {median_frequency}")
        st.write(f"**Fluency Score (WPM):** {fluency_score}%")
        st.write(f"**Words Per Minute (WPM):** {wpm}")

        # AI Feedback
        feedback = evaluate_naturalness(paragraph)
        st.write("## AI Feedback")

        # Display the feedback in a visually distinct card
        st.markdown(f"""
        <div style="background-color: #f5f5f5; padding: 15px; border-radius: 10px; margin-top: 10px;">
            <h4>Feedback</h4>
            <p>{feedback}</p>
        </div>
        """, unsafe_allow_html=True)