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
import random

# Load environment variables
load_dotenv()

# Initialize Coda client
coda = Coda(os.getenv("CODA_API_KEY"))
openai_api_key = os.getenv("OPENAI_API_KEY")

# Demo document and table IDs (single document for all users)
DEMO_DOC_ID = "jPJTMi7bJR"  # Replace with your demo document ID
DEMO_USERS_TABLE = "grid-LJUorNwMyd"  # Demo Users table
DEMO_TOPICS_TABLE = "grid--uaem04-hg"  # Demo Topics table  
DEMO_PROMPTS_TABLE = "grid-ZDdr3ovgSx"  # Demo Prompts table
DEMO_SKILLS_TABLE = "grid-65LBjWjbiz"  # Demo Skills table
DEMO_CONVERSATIONS_TABLE = "grid-orpcEMrGPD"  # Demo Conversation Sessions table
DEMO_SKILL_SESSIONS_TABLE = "grid-orpcEMrGPD"  # Demo Skill Sessions table

def get_table_rows(doc_id: str, table_id: str):
    """Get all rows from a Coda table"""
    doc = Document(doc_id, coda=coda)
    table = doc.get_table(table_id)
    rows = table.rows()
    return [row.to_dict() for row in rows]

def get_user_data(username: str):
    """Get user data from demo users table"""
    rows = get_table_rows(DEMO_DOC_ID, DEMO_USERS_TABLE)
    user_row = next((row for row in rows if row.get('username') == username), None)
    
    if user_row:
        return {
            'username': username,
            'demo_conversation': user_row.get('demo_conversation', 'General Conversation'),
            'demo_topics': user_row.get('demo_topics', ''),
            'demo_skills': user_row.get('demo_skills', ''),
            'prompts': user_row.get('prompts', ''),
            'user_document_id': DEMO_DOC_ID,
            'prompt_table_id': DEMO_PROMPTS_TABLE
        }
    return None

def get_random_prompt(user_data):
    """Get a random prompt from the user's specific prompts"""
    if not user_data or not user_data.get('prompts'):
        return None
    
    # Parse the prompts string (comma-separated)
    user_prompts = [prompt.strip() for prompt in user_data['prompts'].split(',') if prompt.strip()]
    
    if not user_prompts:
        return None
    
    # Get a random prompt from the user's list
    selected_prompt_text = random.choice(user_prompts)
    
    # Now find this prompt in the demo prompts table to get full details
    rows = get_table_rows(DEMO_DOC_ID, DEMO_PROMPTS_TABLE)
    prompt_row = next((row for row in rows if row.get('prompt_text') == selected_prompt_text), None)
    
    return prompt_row

def get_skills_for_user(user_data):
    """Get skills for the user (for display purposes)"""
    if not user_data or not user_data.get('demo_skills'):
        return []
    
    # Parse the skills string (comma-separated)
    skill_names = [skill.strip() for skill in user_data['demo_skills'].split(',') if skill.strip()]
    return skill_names

def get_topics_for_user(user_data):
    """Get topics for the user (for display purposes)"""
    if not user_data or not user_data.get('demo_topics'):
        return []
    
    # Parse the topics string (comma-separated)
    topic_names = [topic.strip() for topic in user_data['demo_topics'].split(',') if topic.strip()]
    return topic_names

def main():
    # Set page config to centered layout
    st.set_page_config(
        page_title="Language Assessment Demo",
        page_icon="��",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    st.title("Language Assessment Demo")
    st.markdown("**Welcome to the demo version!** This version uses simplified data management with shared tables.")
    
    # Get username from query params if present
    query_params = st.query_params
    default_username = query_params.get('username', '')

    # Step 1: Get username and validate
    username = st.text_input("Enter your username", value=default_username)

    if not username:
        st.warning("Please enter your username.")
        return

    # Get user data
    user_data = get_user_data(username)
    
    if not user_data:
        st.warning("Username not found. Please check your username.")
        return

    # Display user information
    st.success(f"Welcome, {username}!")
    
    # Display user's conversation type, topics, and skills (for information only)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**Conversation Type:**")
        st.write(user_data.get('demo_conversation', 'Not specified'))
    
    with col2:
        st.info("**Topics You're Working On:**")
        topics = get_topics_for_user(user_data)
        for topic in topics:
            st.write(f"• {topic}")
    
    with col3:
        st.info("**Skills You're Developing:**")
        skills = get_skills_for_user(user_data)
        for skill in skills:
            st.write(f"• {skill}")
    
    st.markdown("---")
    
    # Step 2: Get and display a random prompt
    st.subheader("🎯 Your Practice Prompt")
    
    # Get a random prompt
    prompt_row = get_random_prompt(user_data)
    
    if not prompt_row:
        st.error("No prompts available. Please contact support.")
        return
    
    # Display context
    st.subheader("🏘️ Context of the situation:")
    st.write(prompt_row.get('prompt_context', 'No context available'))
    
    # Add a button to get a new prompt
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 New Prompt", help="Get a different random prompt"):
            st.rerun()
    
    # Display audio if available            
    audio_url = prompt_row.get('prompt_audio_url_txt', '')            
    if audio_url and not pd.isna(audio_url):
        st.audio(audio_url)
    else:
        st.warning("No audio available for this prompt")
    
    # Step 3: Record user's voice
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
            st.write(prompt_row.get('prompt_text', 'No prompt text available'))
            
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
            
            # Get user's specific skills from the demo skills table
            user_skills_text = user_data.get('demo_skills', '')
            skills_list = []
            
            if user_skills_text:
                # Parse the skills string (comma-separated)
                user_skill_names = [skill.strip() for skill in user_skills_text.split(',') if skill.strip()]
                
                # Get all skills from the demo skills table
                skills_rows = get_table_rows(DEMO_DOC_ID, DEMO_SKILLS_TABLE)
                
                # Filter skills to only include the user's specific skills
                for skill_row in skills_rows:
                    skill_name = skill_row.get('skill_name', '')
                    if skill_name in user_skill_names:
                        skills_list.append({
                            'skill_name': skill_name,
                            'skill_ai_prompt': skill_row.get('skill_ai_prompt', '')
                        })
            
            # If no user-specific skills found, use all skills as fallback
            if not skills_list:
                skills_rows = get_table_rows(DEMO_DOC_ID, DEMO_SKILLS_TABLE)
                for skill_row in skills_rows:
                    skills_list.append({
                        'skill_name': skill_row.get('skill_name', ''),
                        'skill_ai_prompt': skill_row.get('skill_ai_prompt', '')
                    })

            # Create a default comprehension prompt
            comprehension_prompt = {
                'skill_name': 'comprehension',
                'skill_ai_prompt': 'evaluate the relevancy of the answer provided given the question was: '
            }
            comprehension_prompt['skill_ai_prompt'] += "Question: " + prompt_row.get('prompt_text', '') + ". And context: " + prompt_row.get('prompt_context', '')

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
                    question=prompt_row.get('prompt_text', ''),
                    context=prompt_row.get('prompt_context', ''),
                    openai_api_key=openai_api_key
                )

            # Update progress - Skills analyzed (80%)
            progress_text.text("💾 Saving your results...")
            progress_bar.progress(80)

            st.write("## Analysis Scores")

            # Create a list of all scores to display (WPM + skills)
            all_scores = []
            
            # Add WPM score
            all_scores.append({
                'name': 'Fluency (WPM)',
                'score': wpm_score,
                'feedback': f"User spoke at {wpm} words per minute",
                'color': get_color(wpm_score)
            })
            
            # Add skill scores
            for result in skills_analysis_results:
                all_scores.append({
                    'name': result['skill'],
                    'score': result['score'],
                    'feedback': result['feedback'],
                    'color': get_color(result['score'])
                })

            # Display scores in rows of max 4
            max_per_row = 4
            for i in range(0, len(all_scores), max_per_row):
                row_scores = all_scores[i:i + max_per_row]
                cols = st.columns(len(row_scores))
                
                for j, score_data in enumerate(row_scores):
                    with cols[j]:
                        # Create a card-like container
                        st.markdown("---")
                        
                        # Display the circular progress
                        progress = CircularProgress(
                            label=score_data['name'][:30] + ("..." if len(score_data['name']) > 30 else ""),
                            value=score_data['score'],
                            key=f"score_progress_{i}_{j}",
                            size="medium",
                            color=score_data['color'],
                            track_color="lightgray"
                        )
                        progress.st_circular_progress()
                        
                        # Display score
                        st.markdown(f"**Score: {score_data['score']}**")
                        
                        # Display collapsible feedback
                        with st.expander("📝 View Feedback", expanded=False):
                            st.write(score_data['feedback'])
                        
                        st.markdown("---")
            
            if not all_scores:
                st.info("No skills found or failed to parse skills.")

            # Prepare data for saving
            current_time = datetime.datetime.now().strftime("%Y-%m-%d, %I:%M:%S %p")
            prompt = prompt_row.get('prompt_text', '')
            user_transcription = transcription
            answer_duration = duration

            try:
                # For demo version, we'll save to a simpler structure
                # You can create these tables manually in Coda or use existing ones
                
                # Option 1: Save to existing tables (if they exist)
                try:
                    doc = Document(DEMO_DOC_ID, coda=coda)
                    
                    # Try to save to demo conversation sessions table
                    conversation_table = doc.get_table(DEMO_CONVERSATIONS_TABLE)
                    
                    # Create the conversation session row
                    conversation_row = {
                        "username": username,
                        "session_id": session_id,
                        "date_time": current_time,
                        "prompt": prompt,
                        "user_transcription": user_transcription,
                        "answer_duration": answer_duration,
                        "wpm_score": wpm_score,
                        "fluency_score": fluency_score,
                        "vocabulary_score": vocabulary_score
                    }
                    
                    # Insert the conversation session
                    conversation_table.upsert_row([Cell(column=key, value_storage=value) for key, value in conversation_row.items()])
                    
                    # Try to save skill sessions
                    skill_table = doc.get_table(DEMO_SKILL_SESSIONS_TABLE)
                    
                    # Add WPM as a skill session
                    wpm_skill_row = {
                        "username": username,
                        "session_id": session_id,
                        "date_time": current_time,
                        "skill_name": "Fluency (WPM)",
                        "skill_score": wpm_score,
                        "skill_feedback": f"User spoke at {wpm} words per minute"
                    }
                    
                    skill_table.upsert_row([Cell(column=key, value_storage=value) for key, value in wpm_skill_row.items()])
                    
                    # Add other skill sessions
                    for result in skills_analysis_results:
                        if result['skill'] != 'comprehension':  # Skip comprehension as it's already added
                            skill_row = {
                                "username": username,
                                "session_id": session_id,
                                "date_time": current_time,
                                "skill_name": result['skill'],
                                "skill_score": result['score'],
                                "skill_feedback": result['feedback']
                            }
                            
                            skill_table.upsert_row([Cell(column=key, value_storage=value) for key, value in skill_row.items()])
                    
                    st.success(f"Results successfully saved! Session ID: {session_id}")
                    
                except Exception as table_error:
                    # If tables don't exist, just log the results
                    st.warning("Demo session tables not found. Results logged below:")
                    st.json({
                        "session_id": session_id,
                        "username": username,
                        "date_time": current_time,
                        "prompt": prompt,
                        "transcription": user_transcription,
                        "duration": answer_duration,
                        "scores": {
                            "wpm_score": wpm_score,
                            "fluency_score": fluency_score,
                            "vocabulary_score": vocabulary_score,
                            "skills": [{"skill": result['skill'], "score": result['score']} for result in skills_analysis_results]
                        }
                    })
                
                # Update progress - Complete (100%)
                progress_text.text("✨ Analysis complete!")
                progress_bar.progress(100)
                
                # Show balloons to celebrate completion
                st.balloons()
                
            except Exception as e:
                st.error(f"Error saving results: {str(e)}")
                import traceback
                tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
                st.error("Traceback details:")
                st.error(tb_str)

if __name__ == "__main__":
    main() 