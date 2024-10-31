import streamlit as st
from services.transcription import whisper_stt
from services.nlp_analysis import analyze_lemmas_and_frequency
from services.ai_analysis import evaluate_naturalness, evaluate_syntax, evaluate_communication
from services.coda_db import save_results_to_coda
from services.export_pdf import export_results_to_pdf
from frontend_elements import display_circular_progress, display_data_table, display_evaluations

def handle_transcription_and_analysis(username, transcription, duration_in_minutes):
    if transcription:
        st.session_state['transcription'] = transcription
        st.session_state['duration_in_minutes'] = duration_in_minutes

        # Display the transcription
        st.write("Transcription:")
        st.write(st.session_state['transcription'])
        st.write(f"Duration: {st.session_state['duration_in_minutes']} minutes")

        # Show progress bar and analyze results
        progress_bar = st.progress(0)
        progress_text = st.empty()  # Placeholder for loading text updates

        # Analyze lemmas and frequency (20%)
        progress_text.text("Analyzing lemmas and frequency...")
        analysis_result = analyze_lemmas_and_frequency(
            transcription, duration_in_minutes=st.session_state['duration_in_minutes']
        )
        progress_bar.progress(20)

        total_lemmas = analysis_result['total_lemmas']
        unique_lemmas = analysis_result['unique_lemmas']
        fluency_score = analysis_result['fluency_score']
        vocabulary_score = analysis_result['vocabulary_score']
        wpm = analysis_result['wpm']
        prompt_code = st.session_state['prompt_code']

        # Syntax Evaluation (40%)
        progress_text.text("Evaluating syntax...")
        syntax_evaluation, syntax_score = evaluate_syntax(transcription)
        progress_bar.progress(40)

        # Communication Evaluation (60%)
        progress_text.text("Evaluating communication...")
        communication_evaluation, communication_score = evaluate_communication(transcription)
        progress_bar.progress(60)

        # Naturalness Evaluation (80%)
        progress_text.text("Evaluating naturalness...")
        naturalness_evaluation, naturalness_score = evaluate_naturalness(transcription)
        progress_bar.progress(80)

        # Save Results to Database (100%)
        progress_text.text("Saving results...")
        save_results_to_coda(
            username, prompt_code, transcription, duration_in_minutes,
            fluency_score, vocabulary_score, syntax_score, communication_score,
            total_lemmas, unique_lemmas, wpm, syntax_evaluation, communication_evaluation,
            naturalness_evaluation
        )
        progress_bar.progress(100)

        # Display success message and results
        st.success("Results saved successfully on the app")
        display_circular_progress(fluency_score, wpm, int(syntax_score), int(vocabulary_score), int(communication_score), int(naturalness_score))
        display_evaluations(naturalness_evaluation, syntax_evaluation, communication_evaluation)
        display_data_table(vocabulary_score, total_lemmas, unique_lemmas, fluency_score, wpm)

        export_results_to_pdf(
            username, transcription, vocabulary_score, total_lemmas, unique_lemmas,
            fluency_score, wpm, syntax_score, communication_score,
            st.session_state['prompt_text'], prompt_code
        )
        st.balloons()
