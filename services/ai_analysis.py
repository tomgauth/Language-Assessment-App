import openai
import os
from dotenv import load_dotenv
import streamlit as st


# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
print(openai.api_key)


def evaluate_score(prompts, transcription):
    """
    Evaluates a language score based on the provided prompts and transcription,
    returning a number between 0 and 100.
    
    Parameters:
    - prompts: The prompt or system/user prompts to be evaluated.
    - transcription: The text transcription to be evaluated.

    Returns:
    - score: A number between 0 and 100.
    """

    # Check if transcription is valid and print it for debugging
    if not transcription:
        st.write("Error: Transcription is empty or None.")
        return 0
    
    # st.write(f"Debug: Received transcription: {transcription}")

    # Inject the transcription into the prompts and print the result
    for prompt in prompts:
        if '{transcription}' in prompt['content']:
            prompt['content'] = prompt['content'].format(transcription=transcription)
            # st.write(f"Debug: Prompt after injecting transcription: {prompt['content']}")
    
    # Verify if prompts have been correctly formatted
    # st.write(f"Debug: Final prompts passed to API: {prompts}")

    try:
        # Call the new OpenAI chat completion API
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=prompts
        )
        
        # st.write(f"Debug: API response received: {response}")
        
        # Extract the content from the response
        score = response.choices[0].message.content
        # st.write(f"Debug: Score extracted from API response: {score}")

        # Try converting to an integer and ensure it is between 0 and 100
        try:
            score = int(score)
            if not 0 <= score <= 100:
                st.write("Error: Score is not within the valid range (0-100). Setting it to 0.")
                score = 0
        except ValueError:
            # st.write("Error: Could not convert score to an integer. Setting score to 0.")
            score = 0

        # st.write(f"Debug: Score to send right before response: {score}, type is: {type(score)}")
        return score

    except openai.OpenAIError as e:
        st.error(f"An error occurred while communicating with OpenAI: {str(e)}")
        return 0

# Define your prompt templates with placeholders for transcription
syntax_score_template = [
    {"role": "system", "content": "You are a language expert evaluating the transcription of a person learning a language and answering to a simple question."},
    {"role": "user", "content": "Evaluate the syntactic coherence of the following text and rate it from 0 to 100. You are looking at sentence construction, level of speech (long sentences with conjunctions and connectors make more sense): '{transcription}'. Only provide the score."}
]

communication_score_template = [
    {"role": "system", "content": "You are a language expert evaluating the transcription of a person learning a language and answering to a simple question."},
    {"role": "user", "content": """Please rate their communication skills from 0 to 100. Specifically, assess:

1. Use of fillers, which indicate natural speech.
2. Use of slang, idioms, and natural-sounding expressions that are typical of native speakers.
3. Overall ability to sound fluent and natural in a conversation.

Evaluate these points and provide a single score from 0 to 100 based on how well they communicate. Only provide the score and no additional explanation. Here is the text: '{transcription}'."""}
]

naturalness_score_template = [
    {"role": "system", "content": "You are a language expert evaluating the transcription of a person learning a language. Your goal is to assess how naturally they speak the language, paying special attention to whether their language use resembles that of a native speaker in casual conversation."},
    {"role": "user", "content": """Evaluate the naturalness of the following transcription, focusing on the following elements:

1. **Use of idioms and natural-sounding expressions**: Does the speaker use idiomatic language or common phrases that native speakers often use?
2. **Sentence construction**: Does the speaker use varied sentence structures, including short, informal, and sometimes incomplete sentences?
3. **Use of fillers and hesitations**: Does the speaker include fillers (like "um", "uh", "you know") and natural pauses, which are typical in everyday conversation?
4. **Flow and rhythm of speech**: Does the transcription read like fluid, conversational speech, even if it includes minor errors or hesitations?
5. **Overall naturalness**: Does the speaker sound like a native speaker, even if there are small mistakes or hesitations? 

Based on these criteria, rate the naturalness of the transcription from 0 to 100. Here is the transcription: '{transcription}'. Only provide the score."""}
]

# TODO: create a prompt that takes the initial question and assess how accurate the answer is. It can be considered as a comprehension test
accuracy_score_template = []

def evaluate_syntax(transcription):
    syntax_score = evaluate_score(syntax_score_template, transcription)
    return syntax_score

def evaluate_communication(transcription):
    com_score = evaluate_score(communication_score_template, transcription)
    return com_score

def evaluate_naturalness(transcription):
    naturalness_score = evaluate_score(naturalness_score_template, transcription)
    return naturalness_score