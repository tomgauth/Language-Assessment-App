import streamlit as st
import pandas as pd
from codaio import Coda, Table, Document, Cell
import os
from dotenv import load_dotenv

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
def save_results_to_coda(username, prompt_code, transcription, fluency_score, vocabulary_score, 
            syntax_score, communication_score, total_lemmas, unique_lemmas, wpm):
    
    # Fetch the results table
    test_sessions_table = doc.get_table('TestSessions')  # Make sure the table ID is correct. https://www.youtube.com/watch?v=PF2ad6pt5k0
    
    # Define the cells with corresponding column IDs and values 
    cells = [
        Cell(column='username', value_storage=username),
        Cell(column='prompt_code', value_storage=prompt_code),
        Cell(column='Test Date', value_storage=pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')),
        Cell(column='Transcription', value_storage=transcription),
        Cell(column='Fluency Score', value_storage=int(fluency_score)),
        Cell(column='Vocabulary Score', value_storage=int(vocabulary_score)),
        Cell(column='Syntax Score', value_storage=int(syntax_score)),
        Cell(column='Communication Score', value_storage=int(communication_score)),
        Cell(column='Total Lemmas', value_storage=int(total_lemmas)),
        Cell(column='Unique Lemmas', value_storage=int(unique_lemmas)),
        Cell(column='wpm', value_storage=int(wpm))
    ]
    
    # Insert the new row into the 'TestSessions' table using upsert_row
    test_sessions_table.upsert_row(cells)

# Step 4: Function to fetch a random row from Coda based on the entered prompt_code, ensuring audio_url exists
def get_prompt_from_coda(prompt_code):
    # Search for rows where the 'prompt_code' column matches the input prompt_code and 'audio_url' is not empty
    matching_rows = df[(df['prompt_code'] == prompt_code) & df['audio_url'].notna() & (df['audio_url'].str.strip() != '')]
    
    # If there are matching rows with a valid audio_url, select a random row
    if not matching_rows.empty:
        random_row = matching_rows.sample(n=1).iloc[0]  # Select one random row
        
        # Extract the required data from the selected row
        audio_url = random_row['audio_url']
        text = random_row['text']
        context = random_row['context']
        language_code = random_row['language_code']
        flag = random_row['flag']

        return {
            'audio_url': audio_url,
            'text': text,
            'context': context,
            'language_code': language_code,
            'flag': flag
        }

    else:
        return None