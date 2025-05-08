import streamlit as st
from services.transcription import whisper_stt
from services.nlp_analysis import analyze_lemmas_and_frequency
from services.ai_analysis import evaluate_naturalness, evaluate_syntax, evaluate_communication
from services.coda_db import save_results_to_coda
from services.export_pdf import export_results_to_pdf
from services.delete_audio_files import delete_old_audio_files
from frontend_elements import display_circular_progress, display_data_table, top_text, display_evaluations
from models.coda_service import CodaService
from dotenv import load_dotenv
import os
import time
import random
import pandas as pd

# Load environment variables
load_dotenv()
CODA_API_KEY = os.getenv("CODA_API_KEY")
CODA_DOC_ID = os.getenv("CODA_DOC_ID")

# Initialize Coda Service
coda_service = CodaService(CODA_API_KEY, CODA_DOC_ID)

# Table IDs for relational traversal
USERS_TABLE_ID = "grid-qqR8f6GhaA"
CHALLENGES_TABLE_ID = "grid-frCt4QLI3B"
CONV_TABLE_ID = "grid-nCqNTa30ig"
TOPICS_TABLE_ID = "grid-iG8u3niYDD"
PROMPTS_TABLE_ID = "grid-vBrJKADk0W"

# Helper: get column mapping for a table
schema_cache = {}
def get_table_mapping(table_id):
    if table_id not in schema_cache:
        schema = coda_service.get_table_schema(table_id)
        schema_cache[table_id] = {col['id']: col['name'] for col in schema['columns']}
    return schema_cache[table_id]

def map_rows(rows, mapping):
    return [
        {mapping.get(k, k): v for k, v in dict(row.values).items()} | {"_row_id": row.id} for row in rows
    ]

# --- Step 1: Username input and validation ---
if 'username_validated' not in st.session_state:
    st.session_state['username_validated'] = False
if 'selected_conversation' not in st.session_state:
    st.session_state['selected_conversation'] = None
if 'conversation_validated' not in st.session_state:
    st.session_state['conversation_validated'] = False

st.set_page_config(
    page_title="Fluency Analyzer",
    page_icon="🎯",
    layout="wide"
)
st.title("🎯 Fluency Analyzer")

# Step 1: Username
if not st.session_state['username_validated']:
    username = st.text_input("Entrez votre nom d'utilisateur :", key="username_input")
    if st.button("Valider le nom d'utilisateur"):
        users_mapping = get_table_mapping(USERS_TABLE_ID)
        users = coda_service.get_rows(USERS_TABLE_ID)
        users_data = map_rows(users, users_mapping)
        user = next((u for u in users_data if u.get('username') == username), None)
        if not user:
            st.error("Nom d'utilisateur introuvable. Veuillez vérifier ou vous inscrire.")
            st.stop()
        st.session_state['username'] = username
        st.session_state['user_id'] = user['_row_id']
        st.session_state['username_validated'] = True
        st.rerun()
    st.stop()

# Step 2: Conversation selection
user_id = st.session_state['user_id']
challenges_mapping = get_table_mapping(CHALLENGES_TABLE_ID)
challenges = coda_service.get_rows(CHALLENGES_TABLE_ID)
challenges_data = map_rows(challenges, challenges_mapping)
user_challenges = [c for c in challenges_data if c.get('user_id') == user_id]

conv_mapping = get_table_mapping(CONV_TABLE_ID)
conversations = coda_service.get_rows(CONV_TABLE_ID)
conversations_data = map_rows(conversations, conv_mapping)
challenge_ids = [c['_row_id'] for c in user_challenges]
user_conversations = [c for c in conversations_data if c.get('challenge_id') in challenge_ids]

if not st.session_state['conversation_validated']:
    if not user_conversations:
        st.error("Aucune conversation trouvée pour cet utilisateur.")
        st.stop()
    conversation_options = {c.get('conversation_name', f"Conversation {i}"): c for i, c in enumerate(user_conversations)}
    selected_conversation_name = st.selectbox("Choisissez une conversation à pratiquer :", list(conversation_options.keys()), key="conversation_select")
    if st.button("Valider la conversation"):
        st.session_state['selected_conversation'] = conversation_options[selected_conversation_name]
        st.session_state['conversation_validated'] = True
        st.rerun()
    st.stop()

# Step 3: Prompt selection and fluency analyzer interface
selected_conversation = st.session_state['selected_conversation']
conversation_id = selected_conversation['_row_id']

# Topics for this conversation
topics_mapping = get_table_mapping(TOPICS_TABLE_ID)
topics = coda_service.get_rows(TOPICS_TABLE_ID)
topics_data = map_rows(topics, topics_mapping)
conversation_topics = [t for t in topics_data if t.get('conversation_id') == conversation_id]

if not conversation_topics:
    st.error("Aucun sujet trouvé pour cette conversation.")
    st.stop()

# Select a topic (if multiple)
topic_options = {t.get('topic_name', f"Sujet {i}"): t for i, t in enumerate(conversation_topics)}
selected_topic_name = st.selectbox("Choisissez un sujet à pratiquer :", list(topic_options.keys()), key="topic_select")
selected_topic = topic_options[selected_topic_name]
topic_id = selected_topic['_row_id']

# Get a random prompt for the selected topic
def get_random_prompt_for_topic(topic_id):
    prompts_mapping = get_table_mapping(PROMPTS_TABLE_ID)
    prompts = coda_service.get_rows(PROMPTS_TABLE_ID)
    prompts_data = map_rows(prompts, prompts_mapping)
    topic_prompts = [p for p in prompts_data if p.get('topic_id') == topic_id]
    if not topic_prompts:
        return None
    return random.choice(topic_prompts)

prompt = get_random_prompt_for_topic(topic_id)
if not prompt:
    st.error("Aucun prompt trouvé pour ce sujet.")
    st.stop()

# Display prompt and context
st.header("💡 Prompt")
st.write(f"**Prompt:** {prompt.get('text', 'No prompt text available')}")
st.write(f"**Context:** {prompt.get('context', 'No context available')}")
if prompt.get('audio_url'):
    st.audio(prompt['audio_url'])

# Record audio
st.header("🎤 Enregistrez votre réponse")
audio_bytes = st.audio_input("Enregistrez votre réponse ici :")
if audio_bytes:
    # Save the audio file
    audio_file = "temp_audio.wav"
    with open(audio_file, "wb") as f:
        f.write(audio_bytes)
    # Transcribe the audio
    transcription = whisper_stt(audio_file)
    # Calculate duration
    duration_in_minutes = len(audio_bytes) / (16000 * 2) / 60  # Approximate duration in minutes
    # Handle transcription and analysis
    st.write("Transcription:")
    st.write(transcription)
    # (The rest of the analysis and saving logic remains unchanged)
    # Analyze lemmas and frequency (20%)
    analysis_result = analyze_lemmas_and_frequency(
        transcription, 
        duration_in_minutes=duration_in_minutes
    )
    total_lemmas = analysis_result['total_lemmas']
    unique_lemmas = analysis_result['unique_lemmas']        
    fluency_score = analysis_result['fluency_score']
    vocabulary_score = analysis_result['vocabulary_score']
    wpm = analysis_result['wpm']
    # Syntax Evaluation
    syntax_evaluation, syntax_score = evaluate_syntax(transcription)
    # Communication Evaluation
    communication_evaluation, communication_score = evaluate_communication(transcription)
    # Naturalness Evaluation
    naturalness_evaluation, naturalness_score = evaluate_naturalness(transcription)
    # Save Results to Database
    save_results_to_coda(
        st.session_state['username'], 
        prompt.get('prompt_code', ''), 
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
    st.success("Résultats enregistrés avec succès dans l'application")
    # Display results
    display_circular_progress(fluency_score, wpm, 
                            int(syntax_score), 
                            int(vocabulary_score),
                            int(communication_score),
                            int(naturalness_score)
                            )
    display_evaluations(naturalness_evaluation, syntax_evaluation, communication_evaluation)
    display_data_table(vocabulary_score, total_lemmas, unique_lemmas, fluency_score, wpm)
    export_results_to_pdf(st.session_state['username'], 
                        transcription, 
                        vocabulary_score, 
                        total_lemmas, 
                        unique_lemmas, 
                        fluency_score, 
                        wpm, 
                        syntax_score, 
                        communication_score, 
                        prompt.get('text', ''), 
                        naturalness_evaluation, 
                        syntax_evaluation, 
                        communication_evaluation)
    delete_old_audio_files()

if __name__ == "__main__":
    main()
