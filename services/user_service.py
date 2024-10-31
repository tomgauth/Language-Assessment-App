import streamlit as st
from services.coda_db import check_user_in_coda, get_prompt_from_coda

def get_user_and_prompt_data():
    username = st.text_input("Enter your username: (enter 'test' to try the app)")
    prompt_code = st.text_input("Enter the prompt code for your audio prompt: (enter 'TEST' to try the app with a French prompt)")
    st.session_state['prompt_code'] = prompt_code.upper().strip()

    if username and prompt_code:
        user_exists = check_user_in_coda(username)
        if not user_exists:
            st.error("Username not found. Please register.")
            return None

        prompt_data = get_prompt_from_coda(prompt_code)
        if prompt_data:
            st.session_state['username'] = username
            return prompt_data
        else:
            st.error("Invalid audio prompt code. No audio URL found. Please try again.")
            return None

    return None
