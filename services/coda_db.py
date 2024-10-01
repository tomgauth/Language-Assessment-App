import streamlit as st
import pandas as pd
from codaio import Coda, Table, Document

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

# Step 4: Function to fetch the correct row from Coda based on the entered code
def get_audio_prompt_from_coda(code):
    # Search for the row where the 'Code' column matches the input code
    matching_row = df[df['code'] == code]

    # If a matching row is found, return the audio prompt
    if not matching_row.empty:
        audio_url = matching_row.iloc[0]['audio_url']  # get audio file
        text = matching_row.iloc[0]['text'] # get text file
        # print(audio_url)
        # print(text)
        return audio_url, text
    
    else:
        return None
