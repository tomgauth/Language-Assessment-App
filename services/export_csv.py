import pandas as pd
import streamlit as st
from io import StringIO
from datetime import datetime



def export_results_to_csv(username, transcription, vocabulary_score, total_lemmas, unique_lemmas, median_frequency, 
                          fluency_score, wpm, syntax_score, communication_score, prompt_text, code, audio_url):
    # Generate the current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create a dictionary to store the data
    results_data = {
        "User Name": [username],
        "Timestamp": [timestamp],  # Add the timestamp
        "Question Code": [code],
        "Prompt Text": [prompt_text],
        "Audio URL": [audio_url],
        "Transcription": [transcription],
        "Vocabulary Score": [vocabulary_score],
        "Total Lemmas": [total_lemmas],
        "Unique Lemmas": [unique_lemmas],
        "Median Frequency": [median_frequency],
        "Fluency Score (WPM)": [fluency_score],
        "Words per Minute (WPM)": [wpm],
        "Syntax Score": [syntax_score],
        "Communication Score": [communication_score]
    }

    # Convert the dictionary to a DataFrame
    results_df = pd.DataFrame(results_data)
    
    # Create a CSV buffer
    csv_buffer = StringIO()
    
    # Write the DataFrame to the CSV buffer
    results_df.to_csv(csv_buffer, index=False)
    
    # Get the CSV as a string
    csv_string = csv_buffer.getvalue()

    # Provide a download button for the CSV file
    st.download_button(
        label="Download Results as CSV",
        data=csv_string,
        file_name="language_assessment_results.csv",
        mime="text/csv"
    )
