import streamlit as st
from services.audio_service import process_audio
from services.transcription import whisper_stt  # Import the transcription service
from services.nlp_analysis import analyze_lemmas_and_frequency  # Import existing functions
from services.ai_analysis import evaluate_naturalness, evaluate_syntax, evaluate_communication  # Import the AI evaluation functions
from services.coda_db import get_audio_prompt_from_coda, check_user_in_coda, save_results_to_coda
from services.export_csv import export_results_to_csv
from st_circular_progress import CircularProgress
import openai
from streamlit_mic_recorder import mic_recorder
from io import BytesIO
import io
from pydub import AudioSegment


st.write("hzeofihzeof")

# Step 1: Initialize session state variables
if 'transcription' not in st.session_state:
    st.session_state['transcription'] = ""
if 'prompt_text' not in st.session_state:
    st.session_state['prompt_text'] = ""
if 'duration_in_minutes' not in st.session_state:
    st.session_state['duration_in_minutes'] = 0.1  # Default value

# Step 1: User enters a code
st.title("Audio Prompt Response App")
code = st.text_input("Enter the code for your audio prompt:")
st.write("Use code TEST to test the app")

if code:
    # Step 2: Fetch and play the audio prompt
    audio_url, prompt_text = get_audio_prompt_from_coda(code)
    st.session_state['prompt_text'] = prompt_text

    if audio_url:
        st.write("Here is your audio prompt (You can only play it once):")
        st.audio(audio_url, format="audio/wav")        
        # Allow the user to start recording after the audio is played
        transcription, duration_in_minutes = whisper_stt()

        if transcription:
            st.session_state['transcription'] = transcription
            st.session_state['duration_in_minutes'] = duration_in_minutes
        else:
            st.write("No audio prompt found for this code.")
                
    else:
        st.write("No audio prompt found for this code.")

# Step 4: Display the transcription and duration (if available)
if st.session_state['transcription']:
    st.write("Transcription:")
    st.write(st.session_state['transcription'])

if st.session_state['duration_in_minutes']:
    st.write(f"Duration in minutes: {st.session_state['duration_in_minutes']}")



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
    
    # Round all numeric values to integers
    data = {
        "Metric": ["Vocabulary Score", "Total Lemmas", "Unique Lemmas", "Median Frequency", "Fluency Score (WPM)", "Words per Minute"],
        "Value": [
            round(vocabulary_score), 
            round(total_lemmas), 
            round(unique_lemmas), 
            median_frequency, 
            round(fluency_score), 
            round(wpm)
        ]
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
if st.session_state['transcription']:
    transcription = st.session_state['transcription']
    if st.button("Analyze"):
        # Appeler la fonction d'analyse qui renvoie un dictionnaire
        analysis_result = analyze_lemmas_and_frequency(
            transcription, duration_in_minutes=st.session_state['duration_in_minutes'])

        # Unpacker les valeurs du dictionnaire
        total_lemmas = analysis_result['total_lemmas']
        unique_lemmas = analysis_result['unique_lemmas']
        median_frequency = analysis_result['median_frequency']
        fluency_score = analysis_result['fluency_score']
        vocabulary_score = analysis_result['vocabulary_score']
        wpm = analysis_result['wpm']

        # AI Syntax Feedback
        syntax_score = evaluate_syntax(transcription)
        st.write(f"Syntax score: {syntax_score}")

        # AI Communication Feedback
        communication_score = evaluate_communication(transcription)
        st.write(f"▶️ Communication score: {communication_score}")

        # Display the circular progress bars
        display_circular_progress(fluency_score, int(syntax_score), vocabulary_score, int(communication_score))

        # Display the gathered data in a table
        display_data_table(vocabulary_score, total_lemmas, unique_lemmas, median_frequency, fluency_score, wpm)

        # Export results as CSV, including timestamp
        export_results_to_csv(
            transcription, vocabulary_score, total_lemmas, unique_lemmas, median_frequency, 
            fluency_score, wpm, syntax_score, communication_score, 
            st.session_state['prompt_text'], code, audio_url
        )

        # Frontend: Add input field for username
username = st.text_input("Enter your username to save results:")

if username:
    # Check if the user exists in the Coda 'Users' table
    user_exists = check_user_in_coda(username)
    
    if user_exists:
        if st.button("Save Results"):
            # Assume these are stored in session state after analysis
            transcription = st.session_state['transcription']
            vocabulary_score = st.session_state['vocabulary_score']
            fluency_score = st.session_state['fluency_score']             
            syntax_score = st.session_state['syntax_score']
            communication_score = st.session_state['communication_score']
            
            # Save the results to Coda
            save_results_to_coda(username, transcription, fluency_score, vocabulary_score, syntax_score, communication_score)
    else:
        st.error("User not found. Please register before saving results.")