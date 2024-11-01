import streamlit as st
from services.transcription import whisper_stt
from services.nlp_analysis import analyze_lemmas_and_frequency
from services.ai_analysis import evaluate_naturalness, evaluate_syntax, evaluate_communication
from services.coda_db import get_prompt_from_coda, check_user_in_coda, save_results_to_coda
from services.export_pdf import export_results_to_pdf
from frontend_elements import display_circular_progress, display_data_table, top_text, display_evaluations
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
    st.session_state['prompt_code'] = prompt_code.upper().strip()

    # Check if both username and code are provided
    if username and prompt_code:
        # Validate username in Coda
        user_exists = check_user_in_coda(username)
        if not user_exists:
            st.error("Username not found. Please register.")
            return None
        
        # Validate the audio prompt_code
        prompt_data = get_prompt_from_coda(prompt_code)        

        return prompt_data  # Return valid username and prompt_code
  

    
    # Return None if either username or prompt_code is missing
    return None

# Step 2: Fetch Audio and Display (with hidden HTML5 audio and play control)
def fetch_and_display_audio_once(prompt_data):
    audio_url = prompt_data['audio_url']
    prompt_text = prompt_data['text']
    context = prompt_data['context']

    if audio_url:
        st.session_state['prompt_text'] = prompt_text

        st.header("💡Context: ")
        st.write(context)
        # st.write("audio file: ", audio_url)
        # Show play button if audio has not been played
        st.audio(audio_url)
        ### PLAY ONLY ONCE BUTTON DOESN'T WORK WITH ELENVEN LABS GENERATED AUDIO ###
#        if not st.session_state['audio_played']:
#            if st.button("Play Audio"):
#                # HTML5 audio element without controls                
#                audio_html = f"""
#                <audio id="audio-player" autoplay>
#                    <source src="{audio_url}" type="audio/mp3">
#                    Your browser does not support the audio element.
#                </audio>
#                """
#                st.markdown(audio_html, unsafe_allow_html=True)
#                st.session_state['audio_played'] = True  # Mark audio as played
#        else:
#            st.write("You've already played the audio.")
        return True
    else:
        st.error("Invalid prompt code. No audio prompt found.")
        return False


def handle_transcription_and_analysis(username, transcription, duration_in_minutes):
    if transcription:
        # Store transcription and duration in session state
        st.session_state['transcription'] = transcription
        st.session_state['duration_in_minutes'] = duration_in_minutes
        
        # Display the transcription
        st.write("Transcription:")
        st.write(st.session_state['transcription'])
        st.write(f"Duration: {st.session_state['duration_in_minutes']} minutes")

        # Step 4: Show progress bar and analyze results
        progress_bar = st.progress(0)
        progress_text = st.empty()  # Placeholder for loading text updates

        # Step 4.1: Analyze lemmas and frequency (20%)
        progress_text.text("Analyzing lemmas and frequency...")
        analysis_result = analyze_lemmas_and_frequency(
            transcription, 
            duration_in_minutes=st.session_state['duration_in_minutes']
        )
        progress_bar.progress(20)
        
        total_lemmas = analysis_result['total_lemmas']
        unique_lemmas = analysis_result['unique_lemmas']        
        fluency_score = analysis_result['fluency_score']
        vocabulary_score = analysis_result['vocabulary_score']
        wpm = analysis_result['wpm']
        prompt_code = st.session_state['prompt_code']

        # Step 4.2: Syntax Evaluation (40%)
        progress_text.text("Evaluating syntax...")
        syntax_evaluation, syntax_score = evaluate_syntax(transcription)
        progress_bar.progress(40)

        # Step 4.3: Communication Evaluation (60%)
        progress_text.text("Evaluating communication...")
        communication_evaluation, communication_score = evaluate_communication(transcription)
        progress_bar.progress(60)

        # Step 4.4: Naturalness Evaluation (80%)
        progress_text.text("Evaluating naturalness...")
        naturalness_evaluation, naturalness_score = evaluate_naturalness(transcription)
        progress_bar.progress(80)

        # Step 4.5: Save Results to Database (100%)
        progress_text.text("Saving results...")
        save_results_to_coda(
            username, 
            prompt_code, 
            transcription, 
            duration_in_minutes, 
            fluency_score, 
            vocabulary_score, 
            syntax_score, 
            communication_score, 
            total_lemmas, 
            unique_lemmas, 
            wpm, 
            syntax_evaluation, 
            communication_evaluation, 
            naturalness_evaluation
        )
        progress_bar.progress(100)
        
        # Display success message and results
        st.success("Results saved successfully on the app")

        # Display results
        display_circular_progress(fluency_score, wpm, 
                                  int(syntax_score), 
                                  int(vocabulary_score),
                                  int(communication_score),
                                  int(naturalness_score)
                                  )
        display_evaluations(naturalness_evaluation, syntax_evaluation, communication_evaluation)
        
        display_data_table(vocabulary_score, total_lemmas, unique_lemmas, fluency_score, wpm)
        
        export_results_to_pdf(username, 
                              transcription, 
                              vocabulary_score, 
                              total_lemmas, 
                              unique_lemmas, 
                              fluency_score, 
                              wpm, 
                              syntax_score, 
                              communication_score, 
                              st.session_state['prompt_text'], 
                              prompt_code
                              )
        st.balloons()

def main():
    # Step 1: Test Mode Toggle
    # test_mode = st.checkbox("Enable Test Mode")
    test_mode = False
    
    if test_mode:
        # Test Mode: Input fields for transcription and duration
        st.write("Test Mode is active. Enter a transcription and duration manually.")
        # transcription = st.text_area("Enter the transcription:")
        transcription = "Oui, en fait, je suis complètement en vacances ici je n'ai pas du tout déménagé, en fait, j'habite toujours aux Etats-Unis je suis juste venu en vacances, faire un peu de tourisme je suis allé à Paris, je suis allé à Bordeaux et là, maintenant, je suis à L'Aigle parce que j'habite au Kansas, en fait et bon, c'est sympa, mais à part des fermes et des vaches, il n'y a pas grand chose"
        # duration_in_minutes = st.number_input("Enter the duration (in minutes):", min_value=0.1, step=0.1)
        duration_in_minutes = 1
        
        if st.button("Run Test"):
            # Store transcription and duration in session state
            st.session_state['transcription'] = transcription
            st.session_state['duration_in_minutes'] = duration_in_minutes
            
            # Directly proceed to the analysis step
            handle_transcription_and_analysis("test", transcription, duration_in_minutes)
    else:
        # Regular Mode: Validate User and Audio Code
        prompt_data = user_and_code_input()
        # st.write(prompt_data)
        # Check if the username and prompt data are valid
        if prompt_data is not None:
            # Store values in session state to avoid issues with variable scope
            st.session_state['prompt_code'] = st.session_state['prompt_code']
            st.session_state['username'] = st.session_state.get('username')
            st.session_state['language_code'] = prompt_data['language_code']
            st.session_state['flag'] = prompt_data['flag']
        
            if 'prompt_code' in st.session_state and 'username' in st.session_state:
                # Step 2: Fetch and display the audio prompt with hidden play once button
                if fetch_and_display_audio_once(prompt_data):
                    st.write("Please listen to the audio and then start recording your response.")
                    # Store relevant data from prompt_data
                    st.session_state['prompt_text'] = prompt_data['text']
                    st.session_state['prompt_language'] = prompt_data['language_code']
                    st.session_state['flag'] = prompt_data['flag']
                
                    # Step 3: Handle Transcription and Analysis
                    transcription, duration_in_minutes = whisper_stt()
                    handle_transcription_and_analysis(st.session_state['username'], transcription, duration_in_minutes)

if __name__ == "__main__":
    main()
