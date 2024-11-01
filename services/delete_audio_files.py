import os
import time

def delete_old_audio_files(directory=".streamlit/static/generated_audio", age_minutes=10):
    """
    Deletes all audio files in the specified directory that were created more than `age_minutes` ago.
    
    Args:
    - directory (str): The path to the directory where audio files are stored.
    - age_minutes (int): The age in minutes after which files should be deleted.
    """
    # Define the time threshold in seconds
    age_threshold = age_minutes * 60
    current_time = time.time()

    # Ensure the directory exists
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return

    # Iterate over files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Check if the file is an audio file and is older than the threshold
        if os.path.isfile(file_path) and filename.endswith(".mp3"):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > age_threshold:
                os.remove(file_path)
                print(f"Deleted old audio file: {filename}")