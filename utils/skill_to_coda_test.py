# INSERT_YOUR_REWRITE_HERE
import streamlit as st
import json
import os
from codaio import Coda, Document, Cell

# Set the title of the Streamlit app
st.title("Coda Test Interface")

# Retrieve the Coda API key and document/table IDs from environment variables
api_key = os.getenv("CODA_API_KEY", "")
doc_id = "f9nBX8nNCW"
prompt_table_id = "grid--bw_j0NnuB"  # Table ID for PromptSessions
skill_table_id = "grid-Gqr5m0Dmei"   # Table ID for SkillSessions (update this to the correct ID)

# Create two tabs for different types of entries
tab1, tab2 = st.tabs(["Prompt Sessions", "Skill Sessions"])

with tab1:
    st.subheader("Add New Prompt Session")
    
    # Add a text area for Prompt Session JSON input with a template
    prompt_template = '''{
        "date_time": "2024-03-21, 10:30:00 AM",
        "prompt": "Sample prompt text",
        "user_transcription": "User's response text",
        "skill_name": "Fluency (WPM)",
        "skill_score": 120,
        "answer_duration": 0.5
    }'''

    prompt_input = st.text_area("Enter prompt session data as JSON:", value=prompt_template, height=200)

    if st.button("Add Prompt Session to Coda Table", key="prompt_button"):
        try:
            # Parse the JSON input
            prompt_dict = json.loads(prompt_input)
            
            # Convert the dictionary to cells
            cells = [Cell(column=key, value_storage=value) for key, value in prompt_dict.items()]
            
            # Display the parsed prompt session
            st.write("Parsed prompt session:", prompt_dict)

            # Connect to Coda
            coda = Coda(api_key)
            doc = Document(doc_id, coda=coda)
            table = doc.get_table(prompt_table_id)

            # Insert the parsed prompt session
            table.upsert_row(cells)
            st.success("Prompt session added to Coda table!")
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {e}")
        except Exception as e:
            st.error(f"Error: {e}")
            st.error("Debug Information:")
            st.error(f"API Key: {'Provided' if api_key else 'Not Provided'}")
            st.error(f"Document ID: {doc_id}")
            st.error(f"Table ID: {prompt_table_id}")
            import traceback
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            st.error("Traceback details:")
            st.error(tb_str)

with tab2:
    st.subheader("Add New Skill Session")
    
    # Add a text area for Skill Session JSON input with a template
    skill_template = '''{
        "date_time": "2024-03-21, 10:30:00 AM",
        "PromptSession": "2025-05-21, 10:23:15 AM",
        "Skill": "Use Fillers",
        "skill_feedback": "The user used many fillers, but not that many. Keep up the great work!",
        "skill_score": 40
    }'''

    skill_input = st.text_area("Enter skill session data as JSON:", value=skill_template, height=200)

    # Add a note about the PromptSession field
    st.info("Note: The 'PromptSession' field should match the date_time of the corresponding prompt session. In the future, this will be replaced with a unique ID.")

    if st.button("Add Skill Session to Coda Table", key="skill_button"):
        try:
            # Parse the JSON input
            skill_dict = json.loads(skill_input)
            
            # Validate required fields
            required_fields = ["date_time", "PromptSession", "Skill", "skill_feedback", "skill_score"]
            missing_fields = [field for field in required_fields if field not in skill_dict]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Convert the dictionary to cells
            cells = [Cell(column=key, value_storage=value) for key, value in skill_dict.items()]
            
            # Display the parsed skill session
            st.write("Parsed skill session:", skill_dict)

            # Connect to Coda
            coda = Coda(api_key)
            doc = Document(doc_id, coda=coda)
            table = doc.get_table(skill_table_id)

            # Insert the parsed skill session
            table.upsert_row(cells)
            st.success("Skill session added to Coda table!")
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON format: {e}")
        except ValueError as e:
            st.error(f"Validation error: {e}")
        except Exception as e:
            st.error(f"Error: {e}")
            st.error("Debug Information:")
            st.error(f"API Key: {'Provided' if api_key else 'Not Provided'}")
            st.error(f"Document ID: {doc_id}")
            st.error(f"Table ID: {skill_table_id}")
            import traceback
            tb_str = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
            st.error("Traceback details:")
            st.error(tb_str)

# Provide general instructions at the bottom of the page
st.info("Use the tabs above to add either Prompt Sessions or Skill Sessions to your Coda tables. Make sure to use the correct JSON format for each type of entry.")