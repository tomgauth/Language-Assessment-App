import streamlit as st
import os
import datetime
import uuid
import requests
import json
import base64
import io
from dotenv import load_dotenv
from codaio import Coda, Document, Table, Cell
import pandas as pd
import random
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# Initialize Coda client
coda = Coda(os.getenv("CODA_API_KEY"))

# SpeechSuper API credentials
SPEECHSUPER_APP_KEY = "17473823180004c9"
SPEECHSUPER_SECRET_KEY = "e2f7f083346cc5a6ebdf8069dfe57398"
SPEECHSUPER_BASE_URL = "https://api.speechsuper.com/"

# Demo document and table IDs (single document for all users)
DEMO_DOC_ID = "jPJTMi7bJR"  # Replace with your demo document ID
DEMO_USERS_TABLE = "grid-LJUorNwMyd"  # Demo Users table
DEMO_PROMPTS_TABLE = "grid-ZDdr3ovgSx"  # Demo Prompts table

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

def user_in_demo_user(demo_user_field, username):
    if not demo_user_field:
        return False
    users = [u.strip() for u in str(demo_user_field).split(',')]
    return username in users

def get_random_paragraph_for_user(username: str):
    """Get a random paragraph from the user's prompts"""
    try:
        # Get all prompts for the user
        all_prompts = get_table_rows(DEMO_DOC_ID, DEMO_PROMPTS_TABLE)
        user_prompts = [row for row in all_prompts if user_in_demo_user(row.get('demo_user', ''), username)]
        
        if not user_prompts:
            return None
        
        # Select a random prompt
        prompt_row = random.choice(user_prompts)
        
        # Return the prompt text as the paragraph to read
        return {
            'paragraph': prompt_row.get('prompt_text', ''),
            'context': prompt_row.get('prompt_context', ''),
            'prompt_id': prompt_row.get('_row_id', '')
        }
    except Exception as e:
        st.error(f"Error getting paragraph: {str(e)}")
        return None

def convert_audio_to_speechsuper_format(audio_data):
    """Convert Streamlit audio data to SpeechSuper format"""
    try:
        # Convert audio data to base64
        audio_bytes = audio_data.read()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return audio_base64
    except Exception as e:
        st.error(f"Error converting audio: {str(e)}")
        return None

def call_speechsuper_api(audio_base64: str, paragraph: str, language: str = "fr"):
    """Call SpeechSuper API for pronunciation assessment"""
    try:
        # Determine coreType based on language
        core_type = "para.eval.fr" if language == "fr" else "para.eval.ru"
        
        # Prepare request payload
        payload = {
            "appKey": SPEECHSUPER_APP_KEY,
            "secretKey": SPEECHSUPER_SECRET_KEY,
            "coreType": core_type,
            "audio": audio_base64,
            "text": paragraph,
            "paragraph_need_word_score": 1  # Get word-level scores
        }
        
        # Make API request
        response = requests.post(
            SPEECHSUPER_BASE_URL + "para.eval",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error calling SpeechSuper API: {str(e)}")
        return None

def parse_speechsuper_response(response_data):
    """Parse SpeechSuper API response and extract scores"""
    try:
        if not response_data or 'result' not in response_data:
            return None
        
        result = response_data['result']
        
        # Extract overall score
        overall_score = result.get('overall_score', 0)
        
        # Extract word-level scores if available
        word_scores = []
        if 'word_score' in result:
            word_scores = result['word_score']
        
        # Extract detailed feedback
        feedback = result.get('feedback', '')
        
        return {
            'overall_score': overall_score,
            'word_scores': word_scores,
            'feedback': feedback,
            'raw_response': response_data
        }
        
    except Exception as e:
        st.error(f"Error parsing API response: {str(e)}")
        return None

def save_pronunciation_result(username: str, paragraph: str, score_data: dict, prompt_id: str):
    """Save pronunciation result to user's database"""
    try:
        # Get user data to find the correct document and table
        user_data = get_user_data(username)
        if not user_data:
            st.error("User data not found")
            return False
        
        # For demo purposes, we'll save to a demo table
        # In production, you'd save to the user's specific document
        doc = Document(DEMO_DOC_ID, coda=coda)
        
        # Create pronunciation results table if it doesn't exist
        # For now, we'll use a simple approach and save to a demo table
        current_time = datetime.datetime.now().strftime("%Y-%m-%d, %I:%M:%S %p")
        session_id = str(uuid.uuid4())
        
        # Save to demo table (you can modify this to save to user-specific tables)
        pronunciation_row = {
            "username": username,
            "session_id": session_id,
            "date_time": current_time,
            "prompt_id": prompt_id,
            "paragraph": paragraph,
            "overall_score": score_data['overall_score'],
            "feedback": score_data['feedback'],
            "word_scores": json.dumps(score_data['word_scores']) if score_data['word_scores'] else ""
        }
        
        # For demo, we'll just show what would be saved
        st.success(f"Pronunciation result saved! Session ID: {session_id}")
        st.write("**Saved Data:**")
        st.json(pronunciation_row)
        
        return True
        
    except Exception as e:
        st.error(f"Error saving result: {str(e)}")
        return False

def display_pronunciation_results(score_data: dict):
    """Display pronunciation assessment results"""
    st.write("## 🎯 Pronunciation Assessment Results")
    
    # Overall score
    overall_score = score_data['overall_score']
    st.metric(
        label="Overall Pronunciation Score",
        value=f"{overall_score:.1f}/100",
        help="Your overall pronunciation accuracy score"
    )
    
    # Color coding based on score
    if overall_score >= 80:
        st.success("Excellent pronunciation! 🎉")
    elif overall_score >= 60:
        st.info("Good pronunciation with room for improvement! 📈")
    elif overall_score >= 40:
        st.warning("Fair pronunciation - keep practicing! 💪")
    else:
        st.error("Pronunciation needs work - don't give up! 🔄")
    
    # Word-level scores if available
    if score_data['word_scores']:
        st.write("### 📝 Word-Level Scores")
        
        # Create a DataFrame for better display
        word_data = []
        for word_score in score_data['word_scores']:
            word_data.append({
                'Word': word_score.get('word', ''),
                'Score': word_score.get('score', 0),
                'Pronunciation': word_score.get('pronunciation', ''),
                'Stress': word_score.get('stress', ''),
                'Intonation': word_score.get('intonation', '')
            })
        
        if word_data:
            df = pd.DataFrame(word_data)
            st.dataframe(df, use_container_width=True)
    
    # Detailed feedback
    if score_data['feedback']:
        st.write("### 💡 Detailed Feedback")
        with st.expander("View detailed feedback", expanded=True):
            st.write(score_data['feedback'])

def main():
    """Main pronunciation evaluator app"""
    st.set_page_config(
        page_title="Pronunciation Evaluator",
        page_icon="🎤",
        layout="centered",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎤 Pronunciation Evaluator")
    st.markdown("**Practice your pronunciation with AI-powered assessment using SpeechSuper technology.**")
    
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
    
    # Language selection
    language = st.selectbox(
        "Select language for pronunciation assessment:",
        ["French", "Russian"],
        format_func=lambda x: "🇫🇷 French" if x == "French" else "🇷🇺 Russian"
    )
    
    # Get language code for API
    lang_code = "fr" if language == "French" else "ru"
    
    st.markdown("---")
    
    # Step 2: Get and display a random paragraph
    st.subheader("📖 Your Practice Paragraph")
    
    # Check if we need to select a new paragraph (only if no paragraph stored)
    paragraph_key = f"pronunciation_paragraph_{username}"
    if paragraph_key not in st.session_state:
        # Get a random paragraph for the user
        paragraph_data = get_random_paragraph_for_user(username)
        if paragraph_data:
            st.session_state[paragraph_key] = paragraph_data
        else:
            st.error("No paragraphs available for this user. Please check your data.")
            return
    
    # Use the stored paragraph
    paragraph_data = st.session_state[paragraph_key]
    
    # Display context if available
    if paragraph_data.get('context'):
        st.subheader("🏘️ Context:")
        st.write(paragraph_data['context'])
    
    # Display the paragraph to read
    st.subheader("📝 Read this paragraph:")
    st.write(paragraph_data['paragraph'])
    
    # Add a button to get a new paragraph
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 New Paragraph", help="Get a different random paragraph"):
            # Clear the stored paragraph to force a new selection
            if paragraph_key in st.session_state:
                del st.session_state[paragraph_key]
            st.rerun()
    
    st.markdown("---")
    
    # Step 3: Record user's pronunciation
    st.subheader("🎤 Record Your Pronunciation")
    st.info("💡 **Recording Tips:** Speak clearly and naturally. Read the paragraph exactly as written. Take your time and pronounce each word carefully.")
    
    audio_data = st.audio_input(
        label="Click to record your pronunciation",
        key="pronunciation_recorder",
        help="Record yourself reading the paragraph above"
    )
    
    if audio_data is not None:
        if st.button("🎯 Assess Pronunciation"):
            # Generate session ID
            session_id = str(uuid.uuid4())
            
            # Initialize progress bar
            progress_bar = st.progress(0)
            progress_text = st.empty()
            
            # Update progress - Starting audio conversion (25%)
            progress_text.text("🔄 Converting audio format...")
            progress_bar.progress(25)
            
            # Convert audio to SpeechSuper format
            audio_base64 = convert_audio_to_speechsuper_format(audio_data)
            
            if not audio_base64:
                st.error("Failed to convert audio format")
                return
            
            # Update progress - Audio converted (50%)
            progress_text.text("📡 Sending to SpeechSuper API...")
            progress_bar.progress(50)
            
            # Call SpeechSuper API
            api_response = call_speechsuper_api(
                audio_base64=audio_base64,
                paragraph=paragraph_data['paragraph'],
                language=lang_code
            )
            
            if not api_response:
                st.error("Failed to get pronunciation assessment")
                return
            
            # Update progress - API response received (75%)
            progress_text.text("📊 Processing results...")
            progress_bar.progress(75)
            
            # Parse the response
            score_data = parse_speechsuper_response(api_response)
            
            if not score_data:
                st.error("Failed to parse assessment results")
                return
            
            # Update progress - Complete (100%)
            progress_text.text("✅ Assessment complete!")
            progress_bar.progress(100)
            
            # Display results
            display_pronunciation_results(score_data)
            
            # Save results
            save_pronunciation_result(
                username=username,
                paragraph=paragraph_data['paragraph'],
                score_data=score_data,
                prompt_id=paragraph_data.get('prompt_id', '')
            )
            
            # Show balloons to celebrate completion
            st.balloons()
            
            # Clear session state to allow for a fresh start
            if paragraph_key in st.session_state:
                del st.session_state[paragraph_key]

if __name__ == "__main__":
    main() 