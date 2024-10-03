import streamlit as st
from services.transcription import whisper_stt
from services.nlp_analysis import analyze_lemmas_and_frequency
from services.ai_analysis import evaluate_naturalness, evaluate_syntax, evaluate_communication
from services.coda_db import get_audio_prompt_from_coda, check_user_in_coda, save_results_to_coda
from services.export_pdf import export_results_to_pdf
from st_circular_progress import CircularProgress
import io



st.title("Fluency Analyser")

st.write("""
1️⃣ **Enter your username** to get started.

2️⃣ **Input the code** given by your teacher.

🎧 You’ll hear an **audio prompt** – a question or something to discuss. Listen carefully because you’ll only hear it once!

🎤 Press the **recording button** and respond to the prompt. Try to speak fast and naturally, as if you're in a real-life conversation.

🗣️ The app will **analyze your speech** based on how many words you use, the complexity of your sentences, and your overall communication skills.

📊 Once done, your results will be **saved** for your teacher to track your progress over time.

❓ Have questions? Feel free to contact me at **tom@hackfrenchwithtom.com**. 😊
""")

# Step 1: Initialize session state variables
if 'transcription' not in st.session_state:
    st.session_state['transcription'] = ""
if 'prompt_text' not in st.session_state:
    st.session_state['prompt_text'] = ""
if 'duration_in_minutes' not in st.session_state:
    st.session_state['duration_in_minutes'] = 0.1  # Default value
if 'prompt_code' not in st.session_state:
    st.session_state['prompt_code'] = ""

# Step 1: Validate User and Audio Code
def user_and_code_input():
    # Get the username and code
    username = st.text_input("Enter your username: (enter 'test', to try the app)")
    prompt_code = st.text_input("Enter the prompt code for your audio prompt:   (enter 'TEST' to try the app with a French prompt)")
    st.session_state['prompt_code'] = prompt_code
    
    # Check if both username and code are provided
    if username and prompt_code:
        # Validate username in Coda
        user_exists = check_user_in_coda(username)
        if not user_exists:
            st.error("Username not found. Please register.")
            return None, None, None
        
        # Validate the audio prompt_code
        audio_url, prompt_text = get_audio_prompt_from_coda(prompt_code)
        if audio_url:
            return username, prompt_code, prompt_text  # Return valid username and prompt_code
        else:
            st.error("Invalid audio prompt_code. Please try again.")
            return None, None, None
    
    # Return None if either username or prompt_code is missing
    return None, None, None

# Step 2: Fetch Audio and Display
def fetch_and_display_audio(code):
    audio_url, prompt_text = get_audio_prompt_from_coda(code)
    if audio_url:
        st.session_state['prompt_text'] = prompt_text
        st.audio(audio_url, format="audio/wav")
        return audio_url, prompt_text
    else:
        st.error("Invalid code. No audio prompt found.")
        return False

# Step 3: Handle Transcription and Analysis
def handle_transcription_and_analysis(username):
    # Once the audio is played, allow the user to record their response
    transcription, duration_in_minutes = whisper_stt()

    if transcription:
        # Store transcription and duration in session state
        st.session_state['transcription'] = transcription
        st.session_state['duration_in_minutes'] = duration_in_minutes
        
        # Perform Analysis
        st.write("Transcription:")
        st.write(st.session_state['transcription'])
        st.write(st.session_state['duration_in_minutes'])

        # Step 4: Perform analysis and display results
        analysis_result = analyze_lemmas_and_frequency(
            transcription, duration_in_minutes=st.session_state['duration_in_minutes'])
        

        total_lemmas = analysis_result['total_lemmas']
        unique_lemmas = analysis_result['unique_lemmas']
        median_frequency = analysis_result['median_frequency']
        fluency_score = analysis_result['fluency_score']
        vocabulary_score = analysis_result['vocabulary_score']
        wpm = analysis_result['wpm']
        prompt_code = st.session_state['prompt_code']

        # AI Feedback
        syntax_score = evaluate_syntax(transcription)
        communication_score = evaluate_communication(transcription)

        # Save Results
        save_results_to_coda(
            username, prompt_code, transcription, fluency_score, vocabulary_score, 
            syntax_score, communication_score, total_lemmas, unique_lemmas, median_frequency, wpm
        )
        st.success("Results saved successfully on the app")

        # Display results
        display_circular_progress(fluency_score, int(syntax_score), vocabulary_score, int(communication_score))
        display_data_table(vocabulary_score, total_lemmas, unique_lemmas, median_frequency, fluency_score, wpm)
        
        export_results_to_pdf(username, transcription, vocabulary_score, total_lemmas, unique_lemmas, median_frequency, 
                          fluency_score, wpm, syntax_score, communication_score, st.session_state['prompt_text'], prompt_code)

#    else:
#        st.error("Transcription failed. Please try again.")

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


def main():
    # Step 1: Validate User and Audio Code
    username, prompt_code, prompt_text = user_and_code_input()
    
    if username and prompt_code:
        # Step 2: Fetch and display the audio prompt
        if fetch_and_display_audio(prompt_code):
            st.write("Please listen to the audio and then start recording your response.")
            st.session_state['prompt_text'] = prompt_text
            # Step 3: Handle Transcription and Analysis
            handle_transcription_and_analysis(username)

if __name__ == "__main__":
    main()