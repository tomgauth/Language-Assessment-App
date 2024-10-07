import streamlit as st
from services.transcription import whisper_stt
from services.nlp_analysis import analyze_lemmas_and_frequency
from services.ai_analysis import evaluate_naturalness, evaluate_syntax, evaluate_communication
from services.coda_db import get_prompt_from_coda, check_user_in_coda, save_results_to_coda
from services.export_pdf import export_results_to_pdf
from frontend_elements import display_circular_progress, display_data_table, top_text
import time


st.title("Fluency Analyser")
top_text()

# Step 1: Initialize session state variables
if 'transcription' not in st.session_state:
    st.session_state['transcription'] = ""
if 'prompt_text' not in st.session_state:
    st.session_state['prompt_text'] = ""
if 'duration_in_minutes' not in st.session_state:
    st.session_state['duration_in_minutes'] = 0.1  # Default value
if 'prompt_code' not in st.session_state:
    st.session_state['prompt_code'] = ""
if 'language_code' not in st.session_state:
    st.session_state['language_code'] = ""
if 'flag' not in st.session_state:
    st.session_state['flag'] = ""
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'audio_played' not in st.session_state:
    st.session_state['audio_played'] = False  # Track if audio has been played

# Step 1: Validate User and Audio Prompt Code
def user_and_code_input():
    # Get the username and prompt_code
    username = st.text_input("Enter your username: (enter 'test', to try the app)")
    prompt_code = st.text_input("Enter the prompt code for your audio prompt:   (enter 'TEST' to try the app with a French prompt)")
    st.session_state['prompt_code'] = prompt_code

    # Check if both username and code are provided
    if username and prompt_code:
        # Validate username in Coda
        user_exists = check_user_in_coda(username)
        if not user_exists:
            st.error("Username not found. Please register.")
            return None
        
        # Validate the audio prompt_code
        prompt_data = get_prompt_from_coda(prompt_code)
        audio_url = prompt_data['audio_url']

        if audio_url:
            return prompt_data  # Return valid username and prompt_code
        else:
            st.error("Invalid audio prompt code. Please try again.")
            return None
    
    # Return None if either username or prompt_code is missing
    return None

# Step 2: Fetch Audio and Display (with hidden HTML5 audio and play control)
def fetch_and_display_audio_once(prompt_code):
    prompt_data = get_prompt_from_coda(prompt_code)
    audio_url = prompt_data['audio_url']
    prompt_text = prompt_data['text']

    if audio_url:
        st.session_state['prompt_text'] = prompt_text

        # Show play button if audio has not been played
        if not st.session_state['audio_played']:
            if st.button("Play Audio"):
                # HTML5 audio element without controls
                audio_html = f"""
                <audio id="audio-player" autoplay>
                    <source src="{audio_url}" type="audio/wav">
                    Your browser does not support the audio element.
                </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)
                st.session_state['audio_played'] = True  # Mark audio as played
        else:
            st.write("You've already played the audio.")
        return True
    else:
        st.error("Invalid prompt code. No audio prompt found.")
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
            transcription, 
            duration_in_minutes=st.session_state['duration_in_minutes']
        )
        
        total_lemmas = analysis_result['total_lemmas']
        unique_lemmas = analysis_result['unique_lemmas']        
        fluency_score = analysis_result['fluency_score']
        vocabulary_score = analysis_result['vocabulary_score']
        wpm = analysis_result['wpm']
        prompt_code = st.session_state['prompt_code']

        # AI Feedback
        syntax_score = evaluate_syntax(transcription)
        communication_score = evaluate_communication(transcription)
        naturalness_score = evaluate_naturalness(transcription)

        # Save Results
        save_results_to_coda(
            username, prompt_code, transcription, fluency_score, vocabulary_score, 
            syntax_score, communication_score, total_lemmas, unique_lemmas, wpm
        )
        st.success("Results saved successfully on the app")

        # Display results
        display_circular_progress(fluency_score, int(syntax_score), vocabulary_score, int(communication_score), int(naturalness_score))
        display_data_table(vocabulary_score, total_lemmas, unique_lemmas, fluency_score, wpm)
        
        export_results_to_pdf(username, transcription, vocabulary_score, total_lemmas, unique_lemmas, 
                          fluency_score, wpm, syntax_score, communication_score, st.session_state['prompt_text'], prompt_code)

# Main function
def main():
    # Step 1: Validate User and Audio Code
    prompt_data = user_and_code_input()
    
    # Check if the username and prompt data are valid
    if prompt_data is not None:
        # Store values in session state to avoid issues with variable scope
        st.session_state['prompt_code'] = st.session_state['prompt_code']
        st.session_state['username'] = st.session_state.get('username')  # Use session state for username
        st.session_state['language_code'] = prompt_data['language_code']
        st.session_state['flag'] = prompt_data['flag']
    
        if 'prompt_code' in st.session_state and 'username' in st.session_state:
            # Step 2: Fetch and display the audio prompt with hidden play once button
            if fetch_and_display_audio_once(st.session_state['prompt_code']):
                st.write("Please listen to the audio and then start recording your response.")
                # Store relevant data from prompt_data
                st.session_state['prompt_text'] = prompt_data['text']
                st.session_state['prompt_language'] = prompt_data['language_code']
                st.session_state['flag'] = prompt_data['flag']
                
                # Step 3: Handle Transcription and Analysis
                handle_transcription_and_analysis(st.session_state['username'])

if __name__ == "__main__":
    main()
