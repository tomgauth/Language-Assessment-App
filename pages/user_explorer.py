import streamlit as st
import os
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from models.coda_service import CodaService
import pandas as pd

# Load environment variables
load_dotenv()
api_key = os.getenv('CODA_API_KEY')
doc_id = os.getenv('CODA_DOC_ID')

# Initialize CodaService
coda_service = CodaService(api_key, doc_id)

# Page config
st.set_page_config(page_title="User Explorer", layout="wide")
st.title("User Data Explorer (Relational)")

# Debug logging
st.sidebar.title("Debug Info")
debug_mode = st.sidebar.checkbox("Show Debug Info")

def log_debug(message):
    """Log to both terminal and Streamlit if debug mode is enabled"""
    logger.debug(message)
    if debug_mode:
        st.sidebar.write(f"DEBUG: {message}")

# Table IDs
USERS_TABLE_ID = "grid-qqR8f6GhaA"
CHALLENGES_TABLE_ID = "grid-frCt4QLI3B"
CONV_TABLE_ID = "grid-nCqNTa30ig"
TOPICS_TABLE_ID = "grid-iG8u3niYDD"
SKILLS_TABLE_ID = "grid-VZpWaIP27c"
PROMPTS_TABLE_ID = "grid-vBrJKADk0W"
RESULTS_TABLE_ID = "grid-YourResultsTableID"  # Replace with your actual Results table ID

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

# User selection
st.sidebar.title("User Selection")
username = st.sidebar.text_input("Enter Username")

if username:
    try:
        # --- USERS ---
        users_mapping = get_table_mapping(USERS_TABLE_ID)
        users = coda_service.get_rows(USERS_TABLE_ID)
        users_data = map_rows(users, users_mapping)
        user = next((u for u in users_data if u.get('username') == username), None)
        log_debug(f"User search: {username}, found: {user}")
        if not user:
            st.error(f"No user found with username: {username}")
            log_debug(f"User search failed for username: {username}")
            st.stop()
        st.sidebar.success(f"Found user: {user.get('user_first_name')} {user.get('user_last_name')}")
        user_id = user['_row_id']

        # --- CHALLENGES ---
        challenges_mapping = get_table_mapping(CHALLENGES_TABLE_ID)
        challenges = coda_service.get_rows(CHALLENGES_TABLE_ID)
        challenges_data = map_rows(challenges, challenges_mapping)
        user_challenges = [c for c in challenges_data if c.get('user_id') == user_id]
        log_debug(f"User challenges: {user_challenges}")

        # --- CONVERSATIONS ---
        conv_mapping = get_table_mapping(CONV_TABLE_ID)
        conversations = coda_service.get_rows(CONV_TABLE_ID)
        conversations_data = map_rows(conversations, conv_mapping)
        # For all user challenges, get conversations by challenge_id
        challenge_ids = [c['_row_id'] for c in user_challenges]
        user_conversations = [c for c in conversations_data if c.get('challenge_id') in challenge_ids]
        log_debug(f"User conversations: {user_conversations}")

        # --- SKILLS ---
        skills_mapping = get_table_mapping(SKILLS_TABLE_ID)
        skills = coda_service.get_rows(SKILLS_TABLE_ID)
        skills_data = map_rows(skills, skills_mapping)
        # For all user conversations, get skills by conversation_id
        conversation_ids = [c['_row_id'] for c in user_conversations]
        user_skills = [s for s in skills_data if s.get('conversation_id') in conversation_ids]
        log_debug(f"User skills: {user_skills}")

        # --- TOPICS ---
        topics_mapping = get_table_mapping(TOPICS_TABLE_ID)
        topics = coda_service.get_rows(TOPICS_TABLE_ID)
        topics_data = map_rows(topics, topics_mapping)
        # For all user conversations, get topics by conversation_id
        user_topics = [t for t in topics_data if t.get('conversation_id') in conversation_ids]
        log_debug(f"User topics: {user_topics}")

        # --- PROMPTS ---
        prompts_mapping = get_table_mapping(PROMPTS_TABLE_ID)
        prompts = coda_service.get_rows(PROMPTS_TABLE_ID)
        prompts_data = map_rows(prompts, prompts_mapping)
        # For all user topics, get prompts by topic_id
        topic_ids = [t['_row_id'] for t in user_topics]
        user_prompts = [p for p in prompts_data if p.get('topic_id') in topic_ids]
        log_debug(f"User prompts: {user_prompts}")

        # --- RESULTS ---
        # Only if you have a results table
        if RESULTS_TABLE_ID != "grid-YourResultsTableID":
            results_mapping = get_table_mapping(RESULTS_TABLE_ID)
            results = coda_service.get_rows(RESULTS_TABLE_ID)
            results_data = map_rows(results, results_mapping)
            # For all user prompts, get results by prompt_id
            prompt_ids = [p['_row_id'] for p in user_prompts]
            user_results = [r for r in results_data if r.get('prompt_id') in prompt_ids]
            log_debug(f"User results: {user_results}")
        else:
            user_results = []

        # --- Display ---
        st.header(f"User: {user.get('user_first_name')} {user.get('user_last_name')}")
        st.subheader("Challenges")
        st.dataframe(pd.DataFrame(user_challenges) if user_challenges else pd.DataFrame())
        st.subheader("Conversations")
        st.dataframe(pd.DataFrame(user_conversations) if user_conversations else pd.DataFrame())
        st.subheader("Skills")
        st.dataframe(pd.DataFrame(user_skills) if user_skills else pd.DataFrame())
        st.subheader("Topics")
        st.dataframe(pd.DataFrame(user_topics) if user_topics else pd.DataFrame())
        st.subheader("Prompts")
        st.dataframe(pd.DataFrame(user_prompts) if user_prompts else pd.DataFrame())
        if RESULTS_TABLE_ID != "grid-YourResultsTableID":
            st.subheader("Results")
            st.dataframe(pd.DataFrame(user_results) if user_results else pd.DataFrame())

    except Exception as e:
        st.error(f"Error: {str(e)}")
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        st.write("Debug Information:")
        st.write(f"Username searched: {username}")
        if debug_mode:
            import traceback
            st.sidebar.write("Full traceback:")
            st.sidebar.write(traceback.format_exc())
else:
    st.info("Please enter a username in the sidebar to explore user data") 