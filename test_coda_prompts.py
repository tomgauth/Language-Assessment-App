import streamlit as st
from dotenv import load_dotenv
import os
from codaio import Coda
from models.prompt import Prompt
import pandas as pd

# Load environment variables
load_dotenv()
CODA_API_KEY = os.getenv("CODA_API_KEY")
CODA_DOC_ID = os.getenv("CODA_DOC_ID")

# Initialize Coda
coda = Coda(CODA_API_KEY)

st.title("Prompt Management")

# Sidebar for search filters
st.sidebar.header("Search Filters")

# Get all prompts for initial filtering
all_prompts = Prompt.get_all(coda, CODA_DOC_ID)

# Get unique values for filters
languages = sorted(list(set(p.language_name for p in all_prompts)))
levels = sorted(list(set(p.level for p in all_prompts)))
users = sorted(list(set(p.prompt_user for p in all_prompts)))
topics = sorted(list(set(p.topics for p in all_prompts)))

# Create filter widgets
selected_language = st.sidebar.selectbox("Language", ["All"] + languages)
selected_level = st.sidebar.selectbox("Level", ["All"] + levels)
selected_user = st.sidebar.selectbox("User", ["All"] + users)
selected_topic = st.sidebar.selectbox("Topic", ["All"] + topics)

# Text search
search_text = st.sidebar.text_input("Search in description or text")

# Apply filters
filtered_prompts = all_prompts

if selected_language != "All":
    filtered_prompts = [p for p in filtered_prompts if p.language_name == selected_language]
if selected_level != "All":
    filtered_prompts = [p for p in filtered_prompts if p.level == selected_level]
if selected_user != "All":
    filtered_prompts = [p for p in filtered_prompts if p.prompt_user == selected_user]
if selected_topic != "All":
    filtered_prompts = [p for p in filtered_prompts if p.topics == selected_topic]
if search_text:
    filtered_prompts = [
        p for p in filtered_prompts 
        if search_text.lower() in p.prompt_description.lower() 
        or search_text.lower() in p.text.lower()
    ]

# Display results
st.header(f"Found {len(filtered_prompts)} prompts")

# Create a DataFrame for better display
if filtered_prompts:
    df = pd.DataFrame([
        {
            "Description": p.prompt_description,
            "User": p.prompt_user,
            "Language": p.language_name,
            "Level": p.level,
            "Topic": p.topics,
            "Text": p.text[:100] + "..." if len(p.text) > 100 else p.text,
            "ID": p._row_id
        }
        for p in filtered_prompts
    ])
    
    # Display the DataFrame
    st.dataframe(
        df,
        column_config={
            "Description": st.column_config.TextColumn("Description", width="medium"),
            "User": st.column_config.TextColumn("User", width="small"),
            "Language": st.column_config.TextColumn("Language", width="small"),
            "Level": st.column_config.TextColumn("Level", width="small"),
            "Topic": st.column_config.TextColumn("Topic", width="medium"),
            "Text": st.column_config.TextColumn("Text", width="large"),
            "ID": st.column_config.TextColumn("ID", width="small")
        },
        hide_index=True
    )

    # Add expandable details for each prompt
    for prompt in filtered_prompts:
        with st.expander(f"Details: {prompt.prompt_description}"):
            st.write("**Full Text:**")
            st.write(prompt.text)
            st.write("**Context:**")
            st.write(prompt.context)
            st.write("**Audio URL:**")
            st.write(prompt.audio_url)
else:
    st.info("No prompts found matching the selected criteria.")