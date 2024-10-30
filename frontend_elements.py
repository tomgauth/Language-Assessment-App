from st_circular_progress import CircularProgress
import streamlit as st


def top_text():

    st.write("""
    1️⃣ **Enter your username** to get started.

    2️⃣ **Input the code** given by your teacher.

    🎧 You’ll hear an **audio prompt** – a question or something to discuss. Listen carefully because you’ll only hear it once!

    🎤 Press the **recording button** and respond to the prompt. Try to speak fast and naturally, as if you're in a real-life conversation.

    🗣️ The app will **analyze your speech** based on how many words you use, the complexity of your sentences, and your overall communication skills.

    📊 Once done, your results will be **saved** for your teacher to track your progress over time.

    ❓ Have questions? Feel free to contact me at **tom@hackfrenchwithtom.com**. 😊
    """)


# Function to determine color dynamically based on score
def get_color(score):
    if score <= 10:
        return "red"
    elif score <= 30:
        return "orange"
    elif score <= 50:
        return "yellow"
    elif score <= 70:
        return "lightgreen"
    else:
        return "green"
    

def display_evaluations(naturalness_eval, syntax_eval, communication_eval):
    st.title("Feedback")
    st.subheader("Syntax")
    st.write(syntax_eval)
    st.subheader("Communication")
    st.write(communication_eval)
    st.subheader("Naturalness")
    st.write(naturalness_eval)


# Function to display the circular progress charts in a single row
def display_circular_progress(fluency_score, wpm,
                              syntax_score,
                              vocabulary_score,
                              communication_score,
                              naturalness_score
                              ):
    st.write("## Analysis Scores")

    # Use Streamlit columns to display the circular progress charts in one row
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        my_fluency_progress = CircularProgress(
            label="Fluency",
            value=fluency_score,
            key="fluency_progress",
            size="medium",
            color=get_color(fluency_score),
            track_color="lightgray"
        )
        my_fluency_progress.st_circular_progress()
        st.write(wpm)

    with col2:
        my_syntax_progress = CircularProgress(
            label="Syntax",
            value=syntax_score,
            key="syntax_progress",
            size="medium",
            color=get_color(syntax_score),
            track_color="lightgray"
        )
        my_syntax_progress.st_circular_progress()        

    with col3:
        my_vocabulary_progress = CircularProgress(
            label="Vocabulary",
            value=vocabulary_score,
            key="vocabulary_progress",
            size="medium",
            color=get_color(vocabulary_score),
            track_color="lightgray"
        )
        my_vocabulary_progress.st_circular_progress()        

    with col4:
        my_communication_progress = CircularProgress(
            label="Communication",
            value=communication_score,
            key="communication_progress",
            size="medium",
            color=get_color(communication_score),
            track_color="lightgray"
        )
        my_communication_progress.st_circular_progress()

        
    with col5:
        my_naturalness_progress = CircularProgress(
            label="Naturalness",
            value=naturalness_score,
            key="naturalness_progress",
            size="medium",
            color=get_color(naturalness_score),
            track_color="lightgray"
        )
        my_naturalness_progress.st_circular_progress()


# Function to display gathered data in a table
def display_data_table(vocabulary_score, total_lemmas, unique_lemmas, fluency_score, wpm):
    st.write("## Detailed Data Table")
    
    # Round all numeric values to integers
    data = {
        "Metric": ["Vocabulary Score", "Total Lemmas", "Unique Lemmas", "Fluency Score (WPM)", "Words per Minute"],
        "Value": [
            round(vocabulary_score), 
            round(total_lemmas), 
            round(unique_lemmas), 
            round(fluency_score), 
            round(wpm)
        ]
    }
    st.table(data)