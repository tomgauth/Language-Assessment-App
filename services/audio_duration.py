from pydub import AudioSegment
import io


def get_audio_duration_in_minutes(audio_bytes):
    audio_bio = io.BytesIO(audio_bytes)
    audio_bio.name = 'audio.mp3'

    # Load audio file using pydub
    audio_segment = AudioSegment.from_file(audio_bio, format="mp3")

    # Get duration in milliseconds and convert to minutes
    duration_in_minutes = audio_segment.duration_seconds / 60

    return duration_in_minutes