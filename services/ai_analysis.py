import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
print(openai.api_key)



def evaluate_syntax(transcription):
    messages = [
        {"role": "system", "content": "You are a language expert evaluating the transcription of a person learning a language and answering to a simple question."},
        {"role": "user", "content": f"Evaluate the syntactic coherence of the following text and rate it from 0 to 100. You are looking at sentence construction, level of speech (long sentences with conjonctions and connectors make more sense): '{transcription}'. Only provide the score."}
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use 'gpt-3.5-turbo' if needed
            messages=messages,
            temperature=0.5
        )
        syntax_score = response['choices'][0]['message']['content']
        return syntax_score

    except openai.OpenAIError as e:
        return f"An error occurred: {str(e)}"

def evaluate_communication(transcription):
    messages = [
        {"role": "system", "content": "You are a language expert evaluating the transcription of a person learning a language and answering to a simple question."},
        {"role": "user", "content": f"""You are a language expert evaluating the conversational communication of a person learning a language. Please rate their communication skills from 0 to 100. Specifically, assess:

1. Use of fillers (e.g., "uh", "you know", "like"), which indicate natural speech.
2. Ability to ask follow-up questions or ask for clarification, showing active engagement.
3. Rephrasing of the question to ensure understanding.
4. Use of slang, idioms, and natural-sounding expressions that are typical of native speakers.
5. Overall ability to sound fluent and natural in a conversation.

Evaluate these points and provide a single score from 0 to 100 based on how well they communicate. Only provide the score and no additional explanation. Here is the text: '{transcription}'."""}
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use 'gpt-3.5-turbo' if needed
            messages=messages,
            temperature=0.5
        )
        communication = response['choices'][0]['message']['content']
        return communication

    except openai.OpenAIError as e:
        return f"An error occurred: {str(e)}"
    


def evaluate_naturalness(transcription):
    messages = [
        {"role": "system", "content": "You are a language expert evaluating conversational text."},
        {"role": "user", "content": f"Evaluate this text for naturalness and native-like quality: '{transcription}'. Provide a score and feedback."}
    ]
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use 'gpt-3.5-turbo' if needed
            messages=messages,
            temperature=0.5
        )
        feedback = response['choices'][0]['message']['content']
        return feedback

    except openai.OpenAIError as e:
        return f"An error occurred: {str(e)}"