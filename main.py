import streamlit as st
import os
import datetime
import uuid
from dotenv import load_dotenv
from codaio import Coda, Document, Table, Cell
import pandas as pd
from services.transcription import transcribe_audio, get_audio_duration
from services.dynamic_skills_analysis import dynamic_skills_analysis
from frontend_elements import CircularProgress, get_color
from services.nlp_analysis import analyze_lemmas_and_frequency
import ast

# Load environment variables
load_dotenv()

# Initialize Coda client
coda = Coda(os.getenv("CODA_API_KEY"))
openai_api_key = os.getenv("OPENAI_API_KEY")

def get_prompts_table_rows(doc_id: str, table_id: str):
    doc = Document(doc_id, coda=coda)
    table = doc.get_table(table_id)
    rows = table.rows()
    # Each row is a codaio Row object; convert to dict for easier access
    return [row.to_dict() for row in rows]

def main():
    st.title("Language Assessment MVP")
    
    # Step 1: Get document and table IDs
    username = st.text_input("Enter your username")

    if username:
        # Fetch the user-specific document and table IDs from the central table
        central_doc_id = "jPJTMi7bJR"
        central_table_id = "grid-qqR8f6GhaA"
        central_rows = get_prompts_table_rows(central_doc_id, central_table_id)
        
        # Find the row matching the username
        user_row = next((row for row in central_rows if row['username'] == username), None)
        
        if user_row:
            doc_id = user_row['user_document_id']
            table_id = user_row['prompt_table_id']
            user_prompt_session_table = user_row['user_prompt_session_table']
            user_skill_session_table = user_row['user_skill_session_table']  # Get the skill session table ID
            user_skills_table = user_row['user_skills_table']
        else:
            st.warning("Username not found. Please check your username.")
            return
    else:
        st.warning("Please enter your username.")
        return
    
    if not doc_id or not table_id:
        st.warning("Please enter both Document ID and Table ID")
        return
    
    try:
        # Step 2: Display topics
        rows = get_prompts_table_rows(doc_id, table_id)
        
        # Extract unique topics
        topics = list(set(row['topic'] for row in rows))
        selected_topic = st.selectbox("Select a topic", topics)
        
        if selected_topic:
            # Filter prompts by selected topic
            topic_prompts = [row for row in rows if row['topic'] == selected_topic]
            
            # Check if we need to select a new prompt (only if topic changed or no prompt stored)
            topic_key = f"prompt_row_{selected_topic}"
            if topic_key not in st.session_state or st.session_state.get('current_topic') != selected_topic:
                # Select a random prompt from the filtered list
                import random
                st.session_state[topic_key] = random.choice(topic_prompts)
                st.session_state['current_topic'] = selected_topic
            
            # Use the stored prompt
            prompt_row = st.session_state[topic_key]
            
            # Display context
            st.subheader("🏘️ Context of the situation:")
            st.write(prompt_row['prompt_context'])
            
            # Add a button to get a new prompt
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("🔄 New Prompt", help="Get a different random prompt for this topic"):
                    # Clear the stored prompt for this topic to force a new selection
                    if topic_key in st.session_state:
                        del st.session_state[topic_key]
                    st.rerun()
            
            # Display audio if available            
            audio_url = prompt_row['prompt_audio_url_txt']            
            if audio_url and not pd.isna(audio_url):
                st.audio(audio_url)
            else:
                st.warning("No audio available for this prompt")
            
            # Step 5 & 6: Record user's voice
            st.subheader("🎤 Record Your Response")
            
            # Add instructional text
            st.info("💡 **Recording Tips:** Speak normally, as if this was a natural conversation. Don't read from any text or get help from reading materials. Try to listen to the audio only once and respond naturally. Avoid long silences at the beginning and end of your recording, as these are interpreted as drops in fluency.")
            
            audio_data = st.audio_input(
                label="Click to record",
                key=None,
                help=None,
                on_change=None,
                args=None,
                kwargs=None,
                disabled=False,
                label_visibility="visible"
            )
            
            
        if audio_data is not None:            
            # Save the recording (optional)
            if st.button("Confirm"):                
                # Generate a unique session ID for this prompt session
                session_id = str(uuid.uuid4())
                
                # Initialize progress bar
                progress_bar = st.progress(0)
                progress_text = st.empty()
                
                # Display the prompt text for reference
                st.subheader("📝 Original Prompt")
                st.write(prompt_row['prompt_text'])
                
                # Update progress - Starting transcription (10%)
                progress_text.text("🎙️ Transcribing your audio...")
                progress_bar.progress(10)
                
                # Transcribe the audio
                transcription = transcribe_audio(openai_api_key, audio_data)
                
                # Get audio duration
                duration = get_audio_duration(audio_data)  

                if transcription and duration:
                    # Update progress - Transcription complete (30%)
                    progress_text.text("✅ Transcription complete! Analyzing your response...")
                    progress_bar.progress(30)
                    
                    st.subheader("Transcription")
                    st.text_area("Transcription", transcription, height=200, help="This is the transcribed text from your audio input.")
                else:
                    st.error("Failed to transcribe or get audio duration")
                    return

                # Update progress - Starting WPM analysis (40%)
                progress_text.text("📊 Calculating speaking rate and vocabulary...")
                progress_bar.progress(40)

                # Calculate WPM                
                analysis_results = analyze_lemmas_and_frequency(transcription, duration)
                wpm = analysis_results['wpm']
                wpm_score = min(round(wpm), 100)
                fluency_score = analysis_results['fluency_score']
                vocabulary_score = analysis_results['vocabulary_score']
                total_lemmas = analysis_results['total_lemmas']
                unique_lemmas = analysis_results['unique_lemmas']
                
                # Update progress - WPM analysis complete (50%)
                progress_text.text("✅ Speaking rate calculated! Analyzing skills...")
                progress_bar.progress(50)
                
                # Now fetch the skills and display them
                skills_id_str = prompt_row['conversation_skills_id']
                
                # Create a default comprehension prompt
                comprehension_prompt = {
                    'skill_name': 'comprehension',
                    'skill_ai_prompt': 'evaluate the relevancy of the answer provided given the question was: '
                }
                comprehension_prompt['skill_ai_prompt'] += "Question: " + prompt_row['prompt_text'] + ". And context: " + prompt_row['prompt_context']

                # Get skills from the Skills table
                skills_list = []
                if skills_id_str:
                    # Get the skills table
                    user_doc = Document(doc_id, coda=coda)
                    skills_table = user_doc.get_table(user_skills_table)
                    
                    # Split the IDs and fetch each skill
                    skill_ids = [id_str.strip() for id_str in skills_id_str.split(',') if id_str.strip()]
                    
                    # Fetch each skill from the table
                    for skill_id in skill_ids:
                        try:
                            # Find the row with matching skill_id
                            skill_row = next((row for row in skills_table.rows() 
                                           if str(row.to_dict().get('skill_id')) == skill_id), None)
                            if skill_row:
                                skill_data = skill_row.to_dict()
                                skills_list.append({
                                    'skill_name': skill_data['skill_name'],
                                    'skill_ai_prompt': skill_data['skill_ai_prompt']
                                })
                            else:
                                st.warning(f"Skill ID {skill_id} not found in skills table")
                        except Exception as e:
                            st.error(f"Error fetching skill {skill_id}: {e}")

                # Add the comprehension prompt to the list of skills
                skills_list.append(comprehension_prompt)

                # Update progress - Skills fetched (60%)
                progress_text.text("🎯 Evaluating your skills...")
                progress_bar.progress(60)

                # Analyze the skills
                if skills_list:
                    skills_analysis_results = dynamic_skills_analysis(
                        text=transcription,
                        skills=[{'name': skill['skill_name'], 'prompt': skill['skill_ai_prompt']} for skill in skills_list],
                        audio_duration=duration,
                        question=prompt_row['prompt_text'],
                        context=prompt_row['prompt_context'],
                        openai_api_key=openai_api_key
                    )

                # Update progress - Skills analyzed (80%)
                progress_text.text("💾 Saving your results...")
                progress_bar.progress(80)

                st.write("## Analysis Scores")

                # Display scores in columns
                num_skills = len(skills_analysis_results)
                total_columns = num_skills + 1  # +1 for the WPM
                columns = st.columns(total_columns)

                # Display WPM
                with columns[0]:
                    fluency_progress = CircularProgress(
                        label="Fluency (words per minute score)",
                        value=wpm_score,
                        key="fluency_progress",
                        size="medium",
                        color=get_color(wpm_score),
                        track_color="lightgray"
                    )
                    fluency_progress.st_circular_progress()
                    st.write(f"{wpm_score} WPM Score")

                # Display skill scores
                for idx, result in enumerate(skills_analysis_results):
                    with columns[idx + 1]:
                        skill_progress = CircularProgress(
                            label=result['skill'][:50],
                            value=result['score'],
                            key=f"skill_progress_{idx}",
                            size="medium",
                            color=get_color(result['score']),
                            track_color="lightgray"
                        )
                        skill_progress.st_circular_progress()
                        st.write(f"Score: {result['score']}")
                        st.write(f"Feedback: {result['feedback']}")
                else:
                    st.info("No skills found or failed to parse skills.")

                # Prepare data for saving
                current_time = datetime.datetime.now().strftime("%Y-%m-%d, %I:%M:%S %p")
                prompt = prompt_row['prompt_text']
                user_transcription = transcription
                answer_duration = duration

                try:
                    # Save Prompt Session
                    user_doc = Document(doc_id, coda=coda)
                    prompt_table = user_doc.get_table(user_prompt_session_table)
                    
                    # Create the prompt session row
                    prompt_session_row = {
                        "session_id": session_id,
                        "date_time": current_time,
                        "prompt": prompt,
                        "user_transcription": user_transcription,
                        "answer_duration": answer_duration
                    }
                    
                    # Insert the prompt session
                    prompt_table.upsert_row([Cell(column=key, value_storage=value) for key, value in prompt_session_row.items()])
                    
                    # Save Skill Sessions
                    skill_table = user_doc.get_table(user_skill_session_table)
                    
                    # Add WPM as a skill session
                    wpm_skill_row = {
                        "PromptSession": session_id,
                        "date_time": current_time,
                        "Skill": "Fluency (WPM)",
                        "skill_score": wpm_score,
                        "skill_feedback": f"User spoke at {wpm} words per minute"
                    }
                    
                    skill_table.upsert_row([Cell(column=key, value_storage=value) for key, value in wpm_skill_row.items()])
                    
                    # Add other skill sessions
                    for result in skills_analysis_results:
                        if result['skill'] != 'comprehension':  # Skip comprehension as it's already added
                            skill_row = {
                                "PromptSession": session_id,
                                "date_time": current_time,
                                "Skill": result['skill'],
                                "skill_score": result['score'],
                                "skill_feedback": result['feedback']
                            }
                            
                            skill_table.upsert_row([Cell(column=key, value_storage=value) for key, value in skill_row.items()])
                    
                    st.success(f"Results successfully saved! Session ID: {session_id}")
                    
                    # Update progress - Complete (100%)
                    progress_text.text("✨ Analysis complete!")
                    progress_bar.progress(100)
                    
                    # Show balloons to celebrate completion
                    st.balloons()
                    
                    # Clear session state to allow for a fresh start with a new prompt
                    if topic_key in st.session_state:
                        del st.session_state[topic_key]
                    if 'current_topic' in st.session_state:
                        del st.session_state['current_topic']
                    
                except Exception as e:
                    st.error(f"Error saving results: {str(e)}")
    
    except Exception as e:
        import traceback
        tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        st.error(f"An error occurred: {str(e)}")
        st.error("Traceback details:")
        st.error(tb_str)

if __name__ == "__main__":
    main() 