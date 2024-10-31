import streamlit as st
import pandas as pd
from codaio import Coda, Table, Document, Cell
import os
from dotenv import load_dotenv
from services.tts_generator import generate_audio  # Import the TTS generator


# Load environment variables from .env file
load_dotenv()

# Retrieve the Coda API key
CODA_API_KEY = os.getenv("CODA_API_KEY")

# Coda API credentials
DOC_ID = 'jPJTMi7bJR'
TABLE_ID = 'grid-vBrJKADk0W'

# Initialize Coda client
# TODO - change the api key to the environment


coda = Coda(CODA_API_KEY)

# Initialize Coda client and document
doc = Document(DOC_ID, coda=coda)

# Step 2: Get the table using the table ID
table = doc.get_table(TABLE_ID)

# Step 3: Convert the table to a pandas DataFrame
df = pd.DataFrame(table.to_dict())

# Function to check if a user exists in the 'Users' table
def check_user_in_coda(username):
    users_table = doc.get_table('Users')  # Assuming 'Users' is the table name
    df = pd.DataFrame(users_table.to_dict())
    matching_row = df[df['Username'] == username]
    st.session_state['username'] = username
    return not matching_row.empty


# Function to save test results to Coda
def save_results_to_coda(username, 
                         prompt_code, 
                         transcription, 
                         duration_in_minutes, 
                         fluency_score, 
                         vocabulary_score, 
                         syntax_score, 
                         communication_score, 
                         total_lemmas, unique_lemmas, wpm, 
                         syntax_eval, 
                         communication_eval, 
                         naturalness_eval
                         ):
    
    # Fetch the results table
    test_sessions_table = doc.get_table('TestSessions')  # Make sure the table ID is correct. https://www.youtube.com/watch?v=PF2ad6pt5k0
    
    # Define the cells with corresponding column IDs and values 
    cells = [
        Cell(column='username', value_storage=username),
        Cell(column='prompt_code', value_storage=prompt_code),
        Cell(column='Test Date', value_storage=pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')),
        Cell(column='Transcription', value_storage=transcription),
        Cell(column='Duration', value_storage=duration_in_minutes),
        Cell(column='Fluency Score', value_storage=int(fluency_score)),
        Cell(column='wpm', value_storage=int(wpm)),
        Cell(column='Vocabulary Score', value_storage=int(vocabulary_score)),
        Cell(column='Syntax Score', value_storage=int(syntax_score)),
        Cell(column='Communication Score', value_storage=int(communication_score)),
        Cell(column='Total Lemmas', value_storage=int(total_lemmas)),
        Cell(column='Unique Lemmas', value_storage=int(unique_lemmas)),
        Cell(column='syntax_eval', value_storage=syntax_eval),
        Cell(column='communication_eval', value_storage=communication_eval),
        Cell(column='naturalness_eval', value_storage=naturalness_eval)
    ]
    
    # Insert the new row into the 'TestSessions' table using upsert_row
    test_sessions_table.upsert_row(cells)

# Step 4: Function to fetch a random row from Coda based on the entered prompt_code, ensuring audio_url exists
def get_prompt_from_coda(prompt_code):
    """
    Fetch a random row from Coda based on the entered prompt_code.
    If audio_url is missing, generate a new audio URL.
    """
    # Search for rows where 'prompt_code' matches the input
    matching_rows = df[df['prompt_code'] == prompt_code]
    
    # If there are matching rows, select a random row
    if not matching_rows.empty:
        random_row = matching_rows.sample(n=1).iloc[0]  # Select one random row
        
        # Extract the required data from the selected row
        audio_url = random_row.get('audio_url')
        text = random_row['text']
        context = random_row['context']
        language_code = random_row['language_code']
        flag = random_row['flag']
        
        # Check if audio_url is None, NaN, or an empty string
        if not audio_url or pd.isna(audio_url) or audio_url.strip() == "":
            # Generate audio if audio_url is missing or empty
            audio_url = generate_audio(text)  # Assuming this returns a valid file path or URL
            st.write("Debug: ", audio_url)
            if not audio_url:
                raise ValueError("Failed to generate audio.")  # Handle generation failure

        return {
            'audio_url': audio_url,
            'text': text,
            'context': context,
            'language_code': language_code,
            'flag': flag
        }

    else:
        return None