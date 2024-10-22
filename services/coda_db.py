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
CODA_API_KEY = "d3068a73-dcbf-4dc1-949c-7b8c733d76e6"
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

# Step 4: Function to fetch the correct row from Coda based on the entered prompt_code
def get_prompt_from_coda(prompt_code):
    # Search for the row where the 'Code' column matches the input prompt_code
    matching_row = df[df['prompt_code'] == prompt_code]
    

    # If a matching row is found, return the audio prompt
    if not matching_row.empty:
        audio_url = matching_row.iloc[0]['audio_url']  # get audio file
        text = matching_row.iloc[0]['text'] # get text file
        context = matching_row.iloc[0]['context'] # get the context
        language_code = matching_row.iloc[0]['language_code'] # get the language_code
        flag = matching_row.iloc[0]['flag'] # get the flag
        # print(audio_url)
        # print(text)

        return {
            'audio_url': audio_url,
            'text': text,
            'context': context,
            'language_code': language_code,
            'flag': flag
        }

    else:
        return None
