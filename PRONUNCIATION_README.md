# Pronunciation Evaluator App

A simple Streamlit-based pronunciation assessment tool that uses SpeechSuper API to evaluate pronunciation accuracy for French and Russian languages.

## Features

- **Simple Interface**: Clean, minimal UI with text input and audio recording
- **Language Support**: French and Russian pronunciation assessment
- **AI-Powered Assessment**: SpeechSuper API provides detailed pronunciation analysis
- **JSON Results**: Raw API response displayed for easy integration
- **Real-time Feedback**: Immediate pronunciation scoring and feedback

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements_pronunciation.txt
```

### 2. Run the App

```bash
streamlit run pronunciation_app.py
```

## How to Use

1. **Select Language**: Choose between French or Russian
2. **Enter Text**: Type or paste the text you want to read aloud
3. **Record Audio**: Click the microphone button and read the text
4. **Get Assessment**: Click "Assess Pronunciation" to get your results
5. **View Results**: See your score and detailed JSON response

## API Integration

The app uses SpeechSuper API with the following endpoints:
- **French**: `para.eval.fr` - French scripted paragraph pronunciation assessment
- **Russian**: `para.eval.ru` - Russian scripted paragraph pronunciation assessment

### Audio Requirements

- **Formats**: wav, mp3, opus, ogg, amr
- **Channels**: Mono (1 channel)
- **Sampling Rate**: 16000 Hz
- **Bitrate**: At least 96 kbps

### API Response Format

The app returns the complete JSON response from SpeechSuper API, including:
- Overall pronunciation score
- Word-level scores (if requested)
- Detailed feedback and analysis

## Example Usage

```python
# The app will display results like this:
{
  "result": {
    "overall_score": 85.5,
    "word_score": [...],
    "feedback": "Excellent pronunciation overall..."
  }
}
```

## Troubleshooting

- **Audio Issues**: Ensure your microphone is working and browser permissions are granted
- **API Errors**: Check that the SpeechSuper credentials are correct
- **Language Mismatch**: Make sure the selected language matches the text you're reading

## Development

This is a simplified version focused on core functionality. The app can be easily extended to:
- Add more languages
- Integrate with databases
- Add user authentication
- Implement result storage 