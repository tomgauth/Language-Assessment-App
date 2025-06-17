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
from services.learning_plan import analyze_user_progress, format_progress_data
from services.learning_plan_service import generate_learning_plan_data, format_learning_plan_for_display, generate_90_day_progress_data
import ast
import random
from typing import List, Dict, Any

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

def get_prompts_table_rows(doc_id: str, table_id: str):
    doc = Document(doc_id, coda=coda)
    table = doc.get_table(table_id)
    rows = table.rows()
    # Each row is a codaio Row object; convert to dict for easier access
    return [row.to_dict() for row in rows]

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

def user_in_demo_user(demo_user_field, username):
    if not demo_user_field:
        return False
    users = [u.strip() for u in str(demo_user_field).split(',')]
    return username in users

def run_main_app():
    """Main app functionality"""
    st.title("Language Assessment MVP")
    
    # Get username from query params if present
    query_params = st.query_params
    default_username = query_params.get('username', '')

    # Step 1: Get document and table IDs
    username = st.text_input("Enter your username", value=default_username)

    if username:
        # Show spinner while loading user data
        with st.spinner("Loading user data..."):
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
            # --- Display conversation, topics, and skills at the top ---
            col1, col2 = st.columns(2)
            # Show spinner while loading prompt rows
            with st.spinner("Loading prompts and skills..."):
                rows = get_prompts_table_rows(doc_id, table_id)
            with col1:
                st.info("**Topics You're Working On:**")
                
                # Extract unique topics
                topics = list(set(row['topic'] for row in rows))
                for topic in topics:
                    st.write(f"• {topic}")
            with col2:
                st.info("**Skills You're Developing:**")
                skills = ', '.join(set(row['conversation_skills'] for row in rows))
                for skill in [s.strip() for s in skills.split(',') if s.strip()]:
                    st.write(f"• {skill}")
            st.markdown("---")
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
        # Show spinner while loading prompt rows
        with st.spinner("Loading topics..."):
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

def run_demo_app():
    """Demo app functionality"""
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

    # Show spinner while loading user data
    with st.spinner("Loading user data..."):
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
    
    # Show spinner while loading prompts and skills
    with st.spinner("Loading prompts and skills..."):
        # Get all prompts for the user
        all_prompts = get_table_rows(DEMO_DOC_ID, DEMO_PROMPTS_TABLE)
        user_prompts = [row for row in all_prompts if user_in_demo_user(row.get('demo_user', ''), username)]

        # Pick a random prompt
        prompt_row = random.choice(user_prompts) if user_prompts else None

        # Get all skills for the user
        all_skills = get_table_rows(DEMO_DOC_ID, DEMO_SKILLS_TABLE)
        user_skills = [row for row in all_skills if user_in_demo_user(row.get('demo_user', ''), username)]

    # Step 2: Get and display a random prompt
    st.subheader("🎯 Your Practice Prompt")
    if not prompt_row:
        st.error("No prompts available for this user. Please check the demo_user column in your data.")
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
        if st.button("Confirm"):
            session_id = str(uuid.uuid4())
            progress_bar = st.progress(0)
            progress_text = st.empty()
            st.subheader("📝 Original Prompt")
            st.write(prompt_row.get('prompt_text', 'No prompt text available'))
            progress_text.text("🎙️ Transcribing your audio...")
            progress_bar.progress(10)
            transcription = transcribe_audio(openai_api_key, audio_data)
            duration = get_audio_duration(audio_data)
            if transcription and duration:
                progress_text.text("✅ Transcription complete! Analyzing your response...")
                progress_bar.progress(30)
                st.subheader("Transcription")
                st.text_area("Transcription", transcription, height=200, help="This is the transcribed text from your audio input.")
            else:
                st.error("Failed to transcribe or get audio duration")
                return
            progress_text.text("📊 Calculating speaking rate and vocabulary...")
            progress_bar.progress(40)
            analysis_results = analyze_lemmas_and_frequency(transcription, duration)
            wpm = analysis_results['wpm']
            wpm_score = min(round(wpm), 100)
            fluency_score = analysis_results['fluency_score']
            vocabulary_score = analysis_results['vocabulary_score']
            total_lemmas = analysis_results['total_lemmas']
            unique_lemmas = analysis_results['unique_lemmas']
            progress_text.text("✅ Speaking rate calculated! Analyzing skills...")
            progress_bar.progress(50)
            # Prepare skills list for analysis
            skills_list = []
            for skill_row in user_skills:
                skill_prompt = skill_row.get('skill_ai_prompt', '')
                # Ensure feedback is in English
                if 'Respond in English' not in skill_prompt and 'Provide feedback in English' not in skill_prompt:
                    skill_prompt += '\n\nProvide feedback in English.'
                skills_list.append({
                    'skill_name': skill_row.get('skill_name', ''),
                    'skill_ai_prompt': skill_prompt
                })
            # Add the comprehension prompt
            comprehension_prompt = {
                'skill_name': 'comprehension',
                'skill_ai_prompt': 'evaluate the relevancy of the answer provided given the question was: '
            }
            comprehension_prompt['skill_ai_prompt'] += "Question: " + prompt_row.get('prompt_text', '') + ". And context: " + prompt_row.get('prompt_context', '')
            comprehension_prompt['skill_ai_prompt'] += "\n\nProvide feedback in English."
            skills_list.append(comprehension_prompt)
            progress_text.text("🎯 Evaluating your skills...")
            progress_bar.progress(60)
            if skills_list:
                skills_analysis_results = dynamic_skills_analysis(
                    text=transcription,
                    skills=[{'name': skill['skill_name'], 'prompt': skill['skill_ai_prompt']} for skill in skills_list],
                    audio_duration=duration,
                    question=prompt_row.get('prompt_text', ''),
                    context=prompt_row.get('prompt_context', ''),
                    openai_api_key=openai_api_key
                )
            progress_text.text("💾 Saving your results...")
            progress_bar.progress(80)
            st.write("## Analysis Scores")
            all_scores = []
            all_scores.append({
                'name': 'Fluency (WPM)',
                'score': wpm_score,
                'feedback': f"User spoke at {wpm} words per minute",
                'color': get_color(wpm_score)
            })
            for result in skills_analysis_results:
                all_scores.append({
                    'name': result['skill'],
                    'score': result['score'],
                    'feedback': result['feedback'],
                    'color': get_color(result['score'])
                })
            max_per_row = 4
            for i in range(0, len(all_scores), max_per_row):
                row_scores = all_scores[i:i + max_per_row]
                cols = st.columns(len(row_scores))
                for j, score_data in enumerate(row_scores):
                    with cols[j]:
                        st.markdown("---")
                        progress = CircularProgress(
                            label=score_data['name'][:30] + ("..." if len(score_data['name']) > 30 else ""),
                            value=score_data['score'],
                            key=f"score_progress_{i}_{j}",
                            size="medium",
                            color=score_data['color'],
                            track_color="lightgray"
                        )
                        progress.st_circular_progress()
                        st.markdown(f"**Score: {score_data['score']}**")
                        with st.expander("📝 View Feedback", expanded=False):
                            st.write(score_data['feedback'])
                        st.markdown("---")
            if not all_scores:
                st.info("No skills found or failed to parse skills.")
            current_time = datetime.datetime.now().strftime("%Y-%m-%d, %I:%M:%S %p")
            prompt = prompt_row.get('prompt_text', '')
            user_transcription = transcription
            answer_duration = duration
            try:
                doc = Document(DEMO_DOC_ID, coda=coda)
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
                conversation_table = doc.get_table(DEMO_CONVERSATIONS_TABLE)
                conversation_table.upsert_row([Cell(column=key, value_storage=value) for key, value in conversation_row.items()])
                skill_table = doc.get_table(DEMO_SKILL_SESSIONS_TABLE)
                wpm_skill_row = {
                    "username": username,
                    "session_id": session_id,
                    "date_time": current_time,
                    "skill_name": "Fluency (WPM)",
                    "skill_score": wpm_score,
                    "skill_feedback": f"User spoke at {wpm} words per minute"
                }
                skill_table.upsert_row([Cell(column=key, value_storage=value) for key, value in wpm_skill_row.items()])
                for result in skills_analysis_results:
                    if result['skill'] != 'comprehension':
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
                progress_text.text("✨ Analysis complete!")
                progress_bar.progress(100)
                st.balloons()
            except Exception as e:
                st.error(f"Error saving results: {str(e)}")
                import traceback
                tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
                st.error("Traceback details:")
                st.error(tb_str)

def run_my_progress_app():
    """My Progress app functionality"""
    st.title("📊 My Progress")
    st.markdown("**Track your progress and get personalized learning recommendations.**")
    
    # Get username from query params if present
    query_params = st.query_params
    default_username = query_params.get('username', '')

    # Step 1: Get username and validate
    username = st.text_input("Enter your username", value=default_username)

    if not username:
        st.warning("Please enter your username.")
        return

    try:
        # Show spinner while loading user data
        with st.spinner("Loading your learning data..."):
            # Fetch the user-specific document and table IDs from the central table
            central_doc_id = "jPJTMi7bJR"
            central_table_id = "grid-qqR8f6GhaA"
            central_rows = get_prompts_table_rows(central_doc_id, central_table_id)
            
            # Find the row matching the username
            user_row = next((row for row in central_rows if row['username'] == username), None)
            
            if not user_row:
                st.warning("Username not found. Please check your username.")
                return
            
            # Get user's table IDs
            doc_id = user_row['user_document_id']
            user_prompt_session_table = user_row['user_prompt_session_table']
            user_skill_session_table = user_row['user_skill_session_table']
            
            # Fetch user's session data
            user_doc = Document(doc_id, coda=coda)
            
            # Get prompt sessions
            prompt_table = user_doc.get_table(user_prompt_session_table)
            prompt_sessions = [row.to_dict() for row in prompt_table.rows()]
            
            # Get skill sessions
            skill_table = user_doc.get_table(user_skill_session_table)
            skill_sessions = [row.to_dict() for row in skill_table.rows()]

        # Analyze user progress
        progress_data = analyze_user_progress(skill_sessions, prompt_sessions)
        formatted_data = format_progress_data(progress_data)

        # Display welcome message
        st.success(f"Welcome back, {username}! Here's your learning progress.")

        # Summary Cards
        st.subheader("📊 Your Progress Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Sessions",
                value=formatted_data['summary']['total_sessions'],
                help="Number of practice sessions completed"
            )
        
        with col2:
            st.metric(
                label="Average Score",
                value=f"{formatted_data['summary']['average_score']}%",
                help="Overall average score across all skills"
            )
        
        with col3:
            trend_icon = "📈" if formatted_data['summary']['trend'] == 'improving' else "📉" if formatted_data['summary']['trend'] == 'declining' else "➡️"
            st.metric(
                label="Trend",
                value=f"{trend_icon} {formatted_data['summary']['trend'].title()}",
                help="Your recent performance trend"
            )

        # Skills Progress
        if formatted_data['skills']:
            st.subheader("🎯 Skills Progress")
            
            # Create columns for skills display
            skill_cols = st.columns(min(3, len(formatted_data['skills'])))
            
            for i, skill in enumerate(formatted_data['skills']):
                with skill_cols[i % 3]:
                    # Create a card-like container
                    st.markdown("---")
                    
                    # Skill name and score
                    st.markdown(f"**{skill['name']}**")
                    
                    # Progress circle
                    progress = CircularProgress(
                        label=f"{skill['average_score']}%",
                        value=skill['average_score'],
                        key=f"skill_progress_{i}",
                        size="small",
                        color=get_color(skill['average_score']),
                        track_color="lightgray"
                    )
                    progress.st_circular_progress()
                    
                    # Additional info
                    st.markdown(f"**Attempts:** {skill['total_attempts']}")
                    if skill['improvement'] != 0:
                        improvement_text = f"+{skill['improvement']}" if skill['improvement'] > 0 else f"{skill['improvement']}"
                        st.markdown(f"**Change:** {improvement_text}")
                    
                    # Status indicator
                    status_emoji = "🟢" if skill['status'] == 'improving' else "🟡" if skill['status'] == 'stable' else "🔴"
                    st.markdown(f"{status_emoji} {skill['status'].replace('_', ' ').title()}")
                    
                    st.markdown("---")
        else:
            st.info("No skill data available yet. Complete some practice sessions to see your progress!")

        # Progress Charts
        if skill_sessions:
            st.subheader("📈 Progress Over Time")
            
            # Add toggle for grouping
            group_by_week = st.checkbox("📅 Group by week (for datasets with >10 sessions)", value=False)
            
            # Get chart data
            chart_data = get_progress_chart_data(skill_sessions, group_by_week)
            
            if chart_data:
                # Create tabs for different chart types
                tab1, tab2 = st.tabs(["📊 Line Chart", "📊 Bar Chart"])
                
                with tab1:
                    display_line_chart(chart_data)
                
                with tab2:
                    display_bar_chart(chart_data)

        # Learning Goals
        if formatted_data['goals']:
            st.subheader("🎯 Your Learning Goals")
            
            for goal in formatted_data['goals']:
                with st.expander(f"📋 {goal['skill']} - {goal['timeframe']}", expanded=True):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**{goal['description']}**")
                        
                        # Progress bar for goal
                        if goal['target'] > goal['current']:
                            progress_percent = min((goal['current'] / goal['target']) * 100, 100)
                            st.progress(progress_percent / 100)
                            st.markdown(f"Progress: {goal['current']:.0f} → {goal['target']:.0f}")
                        else:
                            st.success("🎉 Goal achieved!")
                    
                    with col2:
                        st.markdown(f"**Current:** {goal['current']:.0f}")
                        st.markdown(f"**Target:** {goal['target']:.0f}")

        # Recommendations
        if formatted_data['recommendations']:
            st.subheader("💡 Personalized Recommendations")
            
            for i, recommendation in enumerate(formatted_data['recommendations']):
                st.markdown(f"{i+1}. {recommendation}")

        # Recent Activity
        if prompt_sessions:
            st.subheader("📅 Recent Activity")
            
            # Show last 5 sessions
            recent_sessions = prompt_sessions[-5:]
            
            for session in reversed(recent_sessions):
                with st.expander(f"Session on {session.get('date_time', 'Unknown date')}", expanded=False):
                    st.markdown(f"**Prompt:** {session.get('prompt', 'No prompt available')[:100]}...")
                    st.markdown(f"**Duration:** {session.get('answer_duration', 'Unknown')} seconds")
                    
                    # Find corresponding skill scores for this session
                    session_id = session.get('session_id')
                    if session_id:
                        session_skills = [s for s in skill_sessions if s.get('PromptSession') == session_id]
                        if session_skills:
                            st.markdown("**Skills assessed:**")
                            for skill in session_skills:
                                st.markdown(f"- {skill.get('Skill', 'Unknown')}: {skill.get('skill_score', 'N/A')}")

    except Exception as e:
        st.error(f"Error loading progress data: {str(e)}")
        st.info("This might be because you haven't completed any practice sessions yet, or there was an issue loading your data.")
        import traceback
        tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        st.error("Technical details:")
        st.error(tb_str)

def get_progress_chart_data(skill_sessions: List[Dict], group_by_week: bool = False) -> Dict[str, Any]:
    """Prepare data for progress charts"""
    if not skill_sessions:
        return None
    
    # Convert to DataFrame and clean data
    df = pd.DataFrame(skill_sessions)
    
    # Clean and convert data
    if 'skill_score' in df.columns:
        df['skill_score'] = pd.to_numeric(df['skill_score'], errors='coerce')
        df = df.dropna(subset=['skill_score'])
    
    if 'date_time' in df.columns:
        df['date_time'] = pd.to_datetime(df['date_time'], errors='coerce')
        df = df.dropna(subset=['date_time'])
    
    if df.empty or 'Skill' not in df.columns:
        return None
    
    # Group by skill and prepare chart data
    chart_data = {}
    
    for skill in df['Skill'].unique():
        skill_data = df[df['Skill'] == skill].copy()
        skill_data = skill_data.sort_values('date_time')
        
        # Apply grouping based on user preference and data size
        should_group = group_by_week and len(skill_data) > 10
        
        if should_group:
            skill_data['week'] = skill_data['date_time'].dt.to_period('W')
            weekly_data = skill_data.groupby('week')['skill_score'].mean().reset_index()
            weekly_data['week'] = weekly_data['week'].astype(str)
            
            chart_data[skill] = {
                'dates': weekly_data['week'].tolist(),
                'scores': weekly_data['skill_score'].tolist(),
                'aggregated': True,
                'data_points': len(weekly_data)
            }
        else:
            chart_data[skill] = {
                'dates': skill_data['date_time'].dt.strftime('%Y-%m-%d %H:%M').tolist(),
                'scores': skill_data['skill_score'].tolist(),
                'aggregated': False,
                'data_points': len(skill_data)
            }
    
    return chart_data

def display_line_chart(chart_data: Dict[str, Any]):
    """Display line chart for progress over time"""
    import plotly.express as px
    import plotly.graph_objects as go
    
    # Prepare data for plotly
    all_data = []
    for skill, data in chart_data.items():
        for i, (date, score) in enumerate(zip(data['dates'], data['scores'])):
            all_data.append({
                'Skill': skill,
                'Date': date,
                'Score': score,
                'Order': i
            })
    
    if not all_data:
        st.info("No chart data available.")
        return
    
    df_chart = pd.DataFrame(all_data)
    
    # Create line chart
    fig = px.line(
        df_chart, 
        x='Date', 
        y='Score', 
        color='Skill',
        title='Skill Progress Over Time',
        labels={'Score': 'Score (%)', 'Date': 'Date'},
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Score (%)",
        hovermode='x unified',
        height=500
    )
    
    # Add data point count info
    total_points = sum(data['data_points'] for data in chart_data.values())
    aggregated_count = sum(1 for data in chart_data.values() if data['aggregated'])
    
    if aggregated_count > 0:
        st.info(f"📊 Showing {total_points} data points across {len(chart_data)} skills. {aggregated_count} skill(s) are grouped by week.")
    else:
        st.info(f"📊 Showing {total_points} individual sessions across {len(chart_data)} skills.")
    
    st.plotly_chart(fig, use_container_width=True)

def display_bar_chart(chart_data: Dict[str, Any]):
    """Display bar chart for progress over time"""
    import plotly.express as px
    
    # Prepare data for plotly
    all_data = []
    for skill, data in chart_data.items():
        for i, (date, score) in enumerate(zip(data['dates'], data['scores'])):
            all_data.append({
                'Skill': skill,
                'Date': date,
                'Score': score,
                'Order': i
            })
    
    if not all_data:
        st.info("No chart data available.")
        return
    
    df_chart = pd.DataFrame(all_data)
    
    # Create bar chart
    fig = px.bar(
        df_chart, 
        x='Date', 
        y='Score', 
        color='Skill',
        title='Skill Progress Over Time',
        labels={'Score': 'Score (%)', 'Date': 'Date'},
        barmode='group'
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Score (%)",
        height=500
    )
    
    # Add data point count info
    total_points = sum(data['data_points'] for data in chart_data.values())
    aggregated_count = sum(1 for data in chart_data.values() if data['aggregated'])
    
    if aggregated_count > 0:
        st.info(f"📊 Showing {total_points} data points across {len(chart_data)} skills. {aggregated_count} skill(s) are grouped by week.")
    else:
        st.info(f"📊 Showing {total_points} individual sessions across {len(chart_data)} skills.")
    
    st.plotly_chart(fig, use_container_width=True)

def run_learning_plan_app():
    """Learning Plan app functionality"""
    st.title("📚 Learning Plan")
    st.markdown("**Your personalized language learning roadmap with FSRS methodology.**")
    
    # Get username from query params if present
    query_params = st.query_params
    default_username = query_params.get('username', '')

    # Step 1: Get username and validate
    username = st.text_input("Enter your username", value=default_username)

    if not username:
        st.warning("Please enter your username.")
        return

    try:
        # Show spinner while generating learning plan
        with st.spinner("Generating your personalized learning plan..."):
            # Generate learning plan data
            plan_data = generate_learning_plan_data(username)
            formatted_plan = format_learning_plan_for_display(plan_data)

        # Display welcome message
        st.success(f"🎯 Personalized Learning Plan Generated for {username}!")

        # User Information Section
        st.subheader("👤 Learner Profile")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Current Level",
                value=formatted_plan['user_info']['current_level'],
                help="Your current language proficiency level"
            )
        
        with col2:
            st.metric(
                label="Current Fluency",
                value=f"{formatted_plan['user_info']['current_wpm']} WPM",
                help="Your current speaking rate"
            )
        
        with col3:
            st.metric(
                label="Program Duration",
                value=f"{formatted_plan['user_info']['total_days']} days",
                help="Total program length"
            )
        
        with col4:
            st.metric(
                label="Target Fluency",
                value=f"{formatted_plan['learning_data']['expected_final_wpm']} WPM",
                help="Expected fluency by program end"
            )

        # Methodology Comparison Charts
        st.subheader("📊 Our Methodology vs Traditional Methods")
        
        # Create comparison charts
        display_methodology_comparison_charts(formatted_plan['methodology_comparison'])

        # 90-Day Progress Projection
        st.subheader("📈 90-Day Learning Journey Projection")
        
        # Generate progress data
        progress_data = generate_90_day_progress_data(formatted_plan['learning_data'])
        display_90_day_progress_chart(progress_data)

        # Learning Overview
        st.subheader("📊 Learning Overview")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("**Sentences to Master**")
            st.metric("Recall", f"{formatted_plan['learning_data']['sentences_to_recall']}")
            st.metric("Recognition", f"{formatted_plan['learning_data']['sentences_to_recognize']}")
            st.metric("Total", f"{formatted_plan['learning_data']['total_sentences']}")
        
        with col2:
            st.info("**Learning Speed Comparison**")
            st.metric("Traditional", f"{formatted_plan['learning_data']['traditional_speed']}/day")
            st.metric("FSRS Method", f"{formatted_plan['learning_data']['fsrs_speed']}/day")
            st.metric("Improvement", f"+{formatted_plan['methodology_comparison']['learning_speed']['improvement']}x")
        
        with col3:
            st.info("**Expected Outcomes**")
            st.metric("Sentences Known", f"{formatted_plan['learning_data']['expected_sentences_known']}")
            st.metric("Daily Learning", f"{formatted_plan['learning_data']['new_sentences_per_day']}/day")
            st.metric("Fluency Gain", f"+{formatted_plan['learning_data']['expected_final_wpm'] - formatted_plan['user_info']['current_wpm']} WPM")

        # Conversation Module
        st.subheader(f"🗣️ {formatted_plan['user_info']['conversation_type']} Module")
        
        with st.expander(f"📚 {formatted_plan['user_info']['conversation_type']} ({formatted_plan['learning_data']['difficulty']})", expanded=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Module Overview:**")
                st.markdown(f"- **Duration:** {formatted_plan['learning_data']['learning_days']} days")
                st.markdown(f"- **Sentences to Recall:** {formatted_plan['learning_data']['sentences_to_recall']}")
                st.markdown(f"- **Sentences to Recognize:** {formatted_plan['learning_data']['sentences_to_recognize']}")
                st.markdown(f"- **Total Sentences:** {formatted_plan['learning_data']['total_sentences']}")
                st.markdown(f"- **Expected Fluency:** {formatted_plan['learning_data']['expected_final_wpm']} WPM")
            
            with col2:
                st.markdown(f"**Learning Speed:**")
                st.metric("Traditional", f"{formatted_plan['learning_data']['traditional_speed']}/day")
                st.metric("FSRS", f"{formatted_plan['learning_data']['fsrs_speed']}/day")
                st.metric("New/Day", f"{formatted_plan['learning_data']['new_sentences_per_day']}")
            
            with col3:
                st.markdown(f"**Topics to Cover:**")
                for topic in formatted_plan['content']['topics']:
                    st.markdown(f"• {topic}")

        # Skills Development
        st.subheader("💪 Skills You'll Develop")
        
        # Display skills with sentence breakdown
        if formatted_plan['content']['skill_sentences']:
            for skill, sentences in formatted_plan['content']['skill_sentences'].items():
                with st.expander(f"✅ {skill}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Recall Sentences", sentences['recall_sentences'])
                    
                    with col2:
                        st.metric("Recognize Sentences", sentences['recognize_sentences'])
                    
                    with col3:
                        st.metric("Total Sentences", sentences['total_sentences'])
        else:
            # Display skills in a grid (fallback)
            skills_per_row = 3
            for i in range(0, len(formatted_plan['content']['skills']), skills_per_row):
                row_skills = formatted_plan['content']['skills'][i:i + skills_per_row]
                cols = st.columns(len(row_skills))
                
                for j, skill in enumerate(row_skills):
                    with cols[j]:
                        st.markdown(f"✅ {skill}")

        # Topics Breakdown
        st.subheader("📚 Topics You'll Cover")
        
        # Display topics with sentence breakdown
        if formatted_plan['content']['topic_sentences']:
            for topic, sentences in formatted_plan['content']['topic_sentences'].items():
                with st.expander(f"📖 {topic}", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Recall Sentences", sentences['recall_sentences'])
                    
                    with col2:
                        st.metric("Recognize Sentences", sentences['recognize_sentences'])
                    
                    with col3:
                        st.metric("Total Sentences", sentences['total_sentences'])
        else:
            # Display topics in a grid (fallback)
            topics_per_row = 3
            for i in range(0, len(formatted_plan['content']['topics']), topics_per_row):
                row_topics = formatted_plan['content']['topics'][i:i + topics_per_row]
                cols = st.columns(len(row_topics))
                
                for j, topic in enumerate(row_topics):
                    with cols[j]:
                        st.markdown(f"📖 {topic}")

        # Practice Prompts
        if formatted_plan['content']['prompts']:
            st.subheader("🎯 Practice Prompts")
            
            for i, prompt in enumerate(formatted_plan['content']['prompts'], 1):
                st.markdown(f"**{i}.** {prompt}")

        # Learning Milestones
        st.subheader("🎯 Learning Milestones")
        
        # Create a timeline-like display
        for i, milestone in enumerate(formatted_plan['milestones']):
            col1, col2 = st.columns([1, 4])
            
            with col1:
                # Progress indicator
                progress_percent = (i + 1) / len(formatted_plan['milestones']) * 100
                st.progress(progress_percent / 100)
                st.markdown(f"**{milestone['date'].strftime('%b %d')}**")
            
            with col2:
                st.markdown(f"**{milestone['milestone']}**")
                st.markdown(f"*{milestone['description']}*")

        # Learning Plan Summary
        st.subheader("📋 Learning Plan Summary")
        st.markdown(formatted_plan['learning_summary'])

        # Action Items
        st.subheader("🚀 Next Steps")
        st.markdown("""
        **To get started with your learning plan:**
        
        1. **Complete your first practice session** in the Main App or Demo App
        2. **Review your progress** regularly in the My Progress section
        3. **Follow the FSRS schedule** for optimal retention
        4. **Track your milestones** and celebrate your achievements
        
        **Remember:** Consistency is key! Even 15-20 minutes of daily practice will help you achieve your goals.
        """)

    except Exception as e:
        st.error(f"Error generating learning plan: {str(e)}")
        st.info("This might be because there was an issue generating your personalized plan.")
        import traceback
        tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        st.error("Technical details:")
        st.error(tb_str)

def display_methodology_comparison_charts(methodology_data: Dict[str, Any]):
    """Display comparison charts showing our methodology vs traditional methods"""
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Create subplots for different comparisons
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Learning Speed (Sentences/Day)', 'Learning Volume Reduction', 'Fluency Impact (WPM)', 'Comprehension Impact'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Learning Speed Comparison
    fig.add_trace(
        go.Bar(
            x=['Traditional', 'Our Method'],
            y=[methodology_data['learning_speed']['traditional'], methodology_data['learning_speed']['our_method']],
            name='Learning Speed',
            marker_color=['#ff7f0e', '#1f77b4'],
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Learning Volume Reduction
    fig.add_trace(
        go.Bar(
            x=['Traditional', 'Our Method'],
            y=[methodology_data['learning_volume']['traditional'], methodology_data['learning_volume']['our_method']],
            name='Learning Volume',
            marker_color=['#ff7f0e', '#1f77b4'],
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Fluency Impact
    fig.add_trace(
        go.Bar(
            x=['Traditional', 'Our Method'],
            y=[methodology_data['fluency_impact']['traditional'], methodology_data['fluency_impact']['our_method']],
            name='Fluency Impact',
            marker_color=['#ff7f0e', '#1f77b4'],
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Comprehension Impact (using numeric values for visualization)
    comprehension_values = [1, methodology_data['comprehension_impact']['improvement']]
    fig.add_trace(
        go.Bar(
            x=['Traditional', 'Our Method'],
            y=comprehension_values,
            name='Comprehension Impact',
            marker_color=['#ff7f0e', '#1f77b4'],
            showlegend=False
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600,
        title_text="Methodology Comparison: Our Advanced System vs Traditional Methods",
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add detailed explanations
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**🚀 FSRS Algorithm**")
        st.markdown("""
        **Machine learning algorithm increases learning speed by 3.5x** compared to conventional methods.
        
        Our spaced repetition system adapts to your learning patterns, optimizing review intervals for maximum retention.
        """)
        
        st.info("**🎧 Audio Comprehension**")
        st.markdown("""
        **Incredible impact on comprehension and practice speed.**
        
        Interactive audio exercises enhance listening skills and pronunciation simultaneously.
        """)
    
    with col2:
        st.info("**📊 Fluency Analyzer**")
        st.markdown("""
        **2x impact on fluency** - typically 50 WPM at A2 to 120 WPM after a few weeks of practice.
        
        Real-time feedback on speaking rate, pauses, and pronunciation patterns.
        """)
        
        st.info("**👨‍🏫 DIRECT Method**")
        st.markdown("""
        **High impact on communication and confidence** with our trained teachers.
        
        Immersive conversation practice focusing on natural language acquisition.
        """)

def display_90_day_progress_chart(progress_data: Dict[str, Any]):
    """Display 90-day progress projection chart with S-curves"""
    import plotly.graph_objects as go
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add traces for each metric
    fig.add_trace(go.Scatter(
        x=progress_data['days'],
        y=progress_data['recall_sentences'],
        mode='lines+markers',
        name='Recall Sentences',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=4),
        hovertemplate='Day %{x}<br>Recall: %{y:.0f} sentences<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=progress_data['days'],
        y=progress_data['recognize_sentences'],
        mode='lines+markers',
        name='Recognize Sentences',
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=4),
        hovertemplate='Day %{x}<br>Recognize: %{y:.0f} sentences<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=progress_data['days'],
        y=progress_data['fluency_wpm'],
        mode='lines+markers',
        name='Fluency (WPM)',
        line=dict(color='#2ca02c', width=3),
        marker=dict(size=4),
        yaxis='y2',
        hovertemplate='Day %{x}<br>Fluency: %{y:.0f} WPM<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=progress_data['days'],
        y=progress_data['communication_skills'],
        mode='lines+markers',
        name='Communication Skills',
        line=dict(color='#d62728', width=3),
        marker=dict(size=4),
        yaxis='y2',
        hovertemplate='Day %{x}<br>Communication: %{y:.0f}%<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Your 90-Day Learning Journey: Expected Progress Over Time',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="Days",
        yaxis_title="Number of Sentences",
        yaxis2=dict(
            title="Fluency (WPM) / Communication Skills (%)",
            overlaying="y",
            side="right",
            range=[0, max(progress_data['targets']['fluency'], progress_data['targets']['communication']) * 1.1]
        ),
        height=600,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add explanation
    st.info("""
    **📊 Understanding Your Learning Journey:**
    
    - **🔵 Recall Sentences:** Active vocabulary you can produce (starts slow, accelerates with practice)
    - **🟠 Recognize Sentences:** Passive vocabulary you can understand (larger volume, steady growth)
    - **🟢 Fluency (WPM):** Speaking speed improvement (60 WPM → 100 WPM with our methodology)
    - **🔴 Communication Skills:** Overall communication confidence and effectiveness
    
    **🎯 Learning Phases:**
    - **Foundation (Days 1-30):** Building basic skills and confidence
    - **Acceleration (Days 31-60):** Rapid improvement through intensive practice
    - **Mastery (Days 61-90):** Fine-tuning and achieving excellence
    """)

def main():
    # Set page config to centered layout with visible sidebar
    st.set_page_config(
        page_title="Language Assessment",
        page_icon="🎯",
        layout="centered",
        initial_sidebar_state="expanded"  # Make sidebar visible by default
    )
    
    # Add sidebar navigation to switch between App and Demo using radio buttons
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Select App Mode:", ["Main App", "Demo App", "My Progress", "Learning Plan"], index=0)
    
    # Run the appropriate app based on selection
    if app_mode == "Main App":
        run_main_app()
    elif app_mode == "Demo App":
        run_demo_app()
    elif app_mode == "My Progress":
        run_my_progress_app()
    else:
        run_learning_plan_app()

if __name__ == "__main__":
    main() 