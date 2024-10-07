import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from services.ai_analysis import evaluate_syntax, evaluate_communication
from services.nlp_analysis import analyze_lemmas_and_frequency

# Test transcriptions with metadata
test_transcriptions = [
    {
        "language": "French",
        "level": "Very Poor",
        "duration": 0.5,
        "text": "Je mange pomme. Elle voiture rouge. Aller parc. Soleil jaune. Amis jouer. Chien grand. Heureux jour."
    },
    {
        "language": "French",
        "level": "Okay",
        "duration": 0.5,
        "text": "Aujourd'hui, je suis allé au parc avec mes amis. Nous avons joué avec le ballon, et il faisait beau. Le soleil brillait et nous étions tous très contents de passer du temps ensemble."
    },
    {
        "language": "French",
        "level": "Native-like",
        "duration": 0.5,
        "text": "Ce matin, j'ai décidé de me promener dans le parc pour profiter du soleil. L'air était frais et les oiseaux chantaient. En chemin, j'ai rencontré des amis avec qui nous avons discuté longuement de sujets intéressants, tout en admirant la beauté de la nature autour de nous."
    },
    {
        "language": "French",
        "level": "Native",
        "duration": 0.82,
        "text": "Écoute, voilà, moi je m'appelle Tom, j'ai pas grand chose à te dire, je sais pas trop quoi dire. J'habite à Budapest et je viens pas de là à la base, à la base je viens du sud-est de la France, d'une petite ville très sympa qui s'appelle Gap. Y'a rien de spécial là-bas. Et puis j'ai décidé de partir parce que j'avais juste envie de travailler n'importe où, parce que je travaille sur Internet. Voilà, j'aime bien apprendre les langues, j'aime bien passer du temps avec mes amis. Et le week-end parfois je vais faire du bouldering, je vais grimper un peu. Je fais du sport parce que je passe beaucoup de temps assis à mon bureau, donc j'aime bien aller faire du sport à la salle de sport. Et puis c'est tout en fait, c'est tout ce que j'ai à dire. Aujourd'hui il fait super beau, y'a un peu de vent et c'est très joli de voir les nuages de ma fenêtre. Et puis voilà."
    },
    {
        "language": "French",
        "level": "A1",
        "duration": 1.258,
        "text": "Je m'appelle Brian, je suis d'États-Unis et je prends un petit français, je apprends français il y a pour deux mois, je travaille dans une entreprise et je voudrais apprendre le français pour voyager en France, spécifiquement le Paris."
    },
    {
        "language": "French",
        "level": "A2",
        "duration": 1.218,
        "text": "Salut, ça va? Moi, ça va. Mon week-end était bien. Aujourd'hui, c'est un peu froid, mais ça va. Je travaille beaucoup. Ma semaine était très occupée. Beaucoup de travail, beaucoup de réunions, beaucoup de petites choses, beaucoup de petites choses à faire, et voilà. Aujourd'hui, je travaille à la maison, à chez moi, en chez moi, et peut-être je vais marcher le chien plus tard, voilà."
    },
    {
        "language": "French",
        "level": "Native",
        "duration": 0.173,
        "text": "Oui, j'ai passé un très bon week-end, merci, c'était très sympa, je me suis bien amusé, je suis allé au cinéma, j'ai vu des amis, j'ai beaucoup aimé ton week-end. Et toi, comment ça s'est passé ? C'était bien ?"
    }

    # Add more test transcriptions with varying duration and complexity
]

# Test the model's performance by running the test multiple times
def run_test(paragraph, times=5, duration_in_minutes=0.5):
    syntax_scores = []
    communication_scores = []
    vocabulary_scores = []
    fluency_scores = []

    for i in range(times):
        # Evaluate AI-generated scores
        syntax_score = evaluate_syntax(paragraph)
        communication_score = evaluate_communication(paragraph)

        # Evaluate vocabulary and fluency (consistently calculated)
        analysis = analyze_lemmas_and_frequency(paragraph, duration_in_minutes)
        vocabulary_score = analysis['vocabulary_score']
        fluency_score = analysis['fluency_score']

        # Store results
        syntax_scores.append(syntax_score)
        communication_scores.append(communication_score)
        vocabulary_scores.append(vocabulary_score)
        fluency_scores.append(fluency_score)

    return {
        "syntax_scores": syntax_scores,
        "communication_scores": communication_scores,
        "vocabulary_scores": vocabulary_scores,
        "fluency_scores": fluency_scores
    }

# Function to display test results as a table and calculate median and ranges
def display_results(test_name, results):
    st.write(f"### Results for {test_name} transcription:")
    
    # Calculate statistics (range, median) for each score
    def calculate_statistics(scores):
        return {
            'Min': np.min(scores),
            'Max': np.max(scores),
            'Median': np.median(scores),
            'Range': np.ptp(scores)  # Max - Min
        }
    
    # Display results in a table
    data = {
        "Metric": ["Syntax Score", "Communication Score", "Vocabulary Score", "Fluency Score"],
        "Min": [
            calculate_statistics(results['syntax_scores'])['Min'],
            calculate_statistics(results['communication_scores'])['Min'],
            calculate_statistics(results['vocabulary_scores'])['Min'],
            calculate_statistics(results['fluency_scores'])['Min']
        ],
        "Max": [
            calculate_statistics(results['syntax_scores'])['Max'],
            calculate_statistics(results['communication_scores'])['Max'],
            calculate_statistics(results['vocabulary_scores'])['Max'],
            calculate_statistics(results['fluency_scores'])['Max']
        ],
        "Median": [
            calculate_statistics(results['syntax_scores'])['Median'],
            calculate_statistics(results['communication_scores'])['Median'],
            calculate_statistics(results['vocabulary_scores'])['Median'],
            calculate_statistics(results['fluency_scores'])['Median']
        ],
        "Range": [
            calculate_statistics(results['syntax_scores'])['Range'],
            calculate_statistics(results['communication_scores'])['Range'],
            calculate_statistics(results['vocabulary_scores'])['Range'],
            calculate_statistics(results['fluency_scores'])['Range']
        ]
    }

    df = pd.DataFrame(data)
    st.table(df)

    return df

# Function to plot error margins as boxplots
def plot_error_margins(results):
    st.write("### Error Margin Visualization")

    # Prepare data for plotting
    score_data = {
        "Syntax": results['syntax_scores'],
        "Communication": results['communication_scores'],
        "Vocabulary": results['vocabulary_scores'],
        "Fluency": results['fluency_scores']
    }

    df_plot = pd.DataFrame(score_data)

    # Create boxplots for each score
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df_plot, orient="h", palette="Set2")
    plt.title("Score Distributions (Error Margins)")
    plt.xlabel("Score")
    st.pyplot(plt)

# Run and display the tests
def run_all_tests():
    for test in test_transcriptions:
        st.write(f"Running test for {test['level']} transcription in {test['language']}...")
        results = run_test(test['text'], duration_in_minutes=test['duration'])
        df_results = display_results(test['level'], results)
        plot_error_margins(results)

if __name__ == "__main__":
    st.title("Language Transcription Test")
    run_all_tests()