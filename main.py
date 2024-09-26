import streamlit as st
from services.transcription import transcribe_audio  # Import the transcription service
from services.nlp_analysis import analyze_lemmas_and_frequency  # Import existing functions
from services.ai_analysis import evaluate_naturalness, evaluate_syntax, evaluate_communication  # Import the AI evaluation functions
from st_circular_progress import CircularProgress
import openai

# Page Title
st.title("Language Proficiency Assessment App")

# Explanation
st.write("""
    This app helps you assess your language proficiency through audio transcription and text analysis. 
    You can either upload an audio file to transcribe or input text directly for analysis.
""")

st.write("Use this app to record your voice for about one minute, then upload it here")
st.link_button(label="record yourself", url="https://www.rev.com/onlinevoicerecorder")

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

# Function to determine color dynamically based on score
def get_color(score):
    if score <= 10:
        return "red"
    elif score <= 30:
        return "orange"
    elif score <= 50:
        return "yellow"
    elif score <= 70:
        return "lightgreen"
    else:
        return "green"


# Function to display the circular progress charts in a single row
def display_circular_progress(fluency_score, syntax_score, vocabulary_score, communication_score):
    st.write("## Analysis Scores")

    # Use Streamlit columns to display the circular progress charts in one row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        my_fluency_progress = CircularProgress(
            label="Fluency",
            value=fluency_score,
            key="fluency_progress",
            size="medium",
            color=get_color(fluency_score),
            track_color="lightgray"
        )
        my_fluency_progress.st_circular_progress()

    with col2:
        my_syntax_progress = CircularProgress(
            label="Syntax",
            value=syntax_score,
            key="syntax_progress",
            size="medium",
            color=get_color(syntax_score),
            track_color="lightgray"
        )
        my_syntax_progress.st_circular_progress()

    with col3:
        my_vocabulary_progress = CircularProgress(
            label="Vocabulary",
            value=vocabulary_score,
            key="vocabulary_progress",
            size="medium",
            color=get_color(vocabulary_score),
            track_color="lightgray"
        )
        my_vocabulary_progress.st_circular_progress()

    with col4:
        my_communication_progress = CircularProgress(
            label="Communication",
            value=communication_score,
            key="communication_progress",
            size="medium",
            color=get_color(communication_score),
            track_color="lightgray"
        )
        my_communication_progress.st_circular_progress()


# Function to display gathered data in a table
def display_data_table(vocabulary_score, total_lemmas, unique_lemmas, median_frequency, fluency_score, wpm):
    st.write("## Detailed Data Table")
    
    data = {
        "Metric": ["Vocabulary Score", "Total Lemmas", "Unique Lemmas", "Median Frequency", "Fluency Score (WPM)", "Words per Minute"],
        "Value": [vocabulary_score, total_lemmas, unique_lemmas, median_frequency, fluency_score, wpm]
    }
    
    st.table(data)
    
    # Paragraph explaining how the scores are calculated
    st.write("""
        **Explanation of the Metrics:**
        - **Fluency**: The number of words spoken per minute (WPM), with higher WPM indicating better fluency.
        - **Syntax**: Assessed by AI, this score reflects the coherence of sentence construction and use of connectors, with more complex and connected sentences earning higher scores.
        - **Vocabulary**: This score is based on the ratio of unique lemmas to total lemmas and the median frequency of words. A more diverse vocabulary with rarer words increases the score.
        - **Communication**: Evaluates the use of fillers, rephrasing, asking back questions, and the use of idioms or slang, making the speaker sound more natural in conversation.
    """)

# Analyze button (shown after audio or text input)
if paragraph:
    if st.button("Analyze"):
        # Call the analysis functions
        vocabulary_score, total_lemmas, unique_lemmas, median_frequency, fluency_score, wpm = analyze_lemmas_and_frequency(
            paragraph, duration_in_minutes)

        # AI Syntax Feedback
        syntax_score = evaluate_syntax(paragraph)

        # AI Communication Feedback
        communication_score = evaluate_communication(paragraph)

        # Display the circular progress bars
        display_circular_progress(fluency_score, int(syntax_score), vocabulary_score, int(communication_score))

        # Display the gathered data in a table
        display_data_table(vocabulary_score, total_lemmas, unique_lemmas, median_frequency, fluency_score, wpm)