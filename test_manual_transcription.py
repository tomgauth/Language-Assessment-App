from services.ai_analysis import *


transcriptions = [
    "J'ai pas grand chose à raconter en fait, tout va bien, voilà, et toi ça va ?",
    "Ouais, mon week-end c'était super, je suis allé au musée et j'ai été me balader un petit peu aussi dans une forêt.",
    "L'apprentissage des langues améliore les fonctions cognitives et offre plus d'opportunités professionnelles.",
    None  # Edge case to check error handling with an empty transcription
]

# Function to run one test:
def run_test():
    print("Testing evaluate_syntax...")
    syntax_score = evaluate_syntax(transcriptions[0])
    print(f"Syntax Score: {syntax_score}")


# Function to run tests for each scoring function
def run_tests(transcriptions):
    print("Testing evaluate_syntax...")
    for idx, transcription in enumerate(transcriptions):
        print(f"Test {idx + 1}: {transcription}")
        syntax_score = evaluate_syntax(transcription)
        print(f"Syntax Score: {syntax_score}")

    print("\nTesting evaluate_communication...")
    for idx, transcription in enumerate(transcriptions):
        print(f"Test {idx + 1}: {transcription}")
        communication_score = evaluate_communication(transcription)
        print(f"Communication Score: {communication_score}")

    print("\nTesting evaluate_naturalness...")
    for idx, transcription in enumerate(transcriptions):
        print(f"Test {idx + 1}: {transcription}")
        naturalness_score = evaluate_naturalness(transcription)
        print(f"Naturalness Score: {naturalness_score}")


run_test()
#run_tests(transcriptions)
 