# Pronunciation Evaluator App

A simple Streamlit-based pronunciation assessment tool that uses Microsoft Azure Speech Services to evaluate pronunciation accuracy for French, Russian, and English languages.

## Features

- **Simple Interface**: Clean, minimal UI with text input and audio recording
- **Language Support**: French, Russian, and English pronunciation assessment
- **AI-Powered Assessment**: Azure Speech Services provides detailed pronunciation analysis
- **Multiple Scores**: Overall, fluency, completeness, and pronunciation scores
- **Detailed Analysis**: Phoneme-level and word-level feedback
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

1. **Select Language**: Choose between French, Russian, or English
2. **Enter Text**: Type or paste the text you want to read aloud
3. **Record Audio**: Click the microphone button and read the text
4. **Get Assessment**: Click "Assess Pronunciation" to get your results
5. **View Results**: See your scores and detailed analysis

## API Integration

The app uses Microsoft Azure Speech Services with the following features:
- **Pronunciation Assessment**: Detailed scoring of pronunciation accuracy
- **Multiple Metrics**: Overall, fluency, completeness, and pronunciation scores
- **Phoneme Analysis**: Individual phoneme-level feedback
- **Word Analysis**: Word-level accuracy assessment
- **Text Comparison**: Reference text vs recognized text

### Audio Requirements

- **Formats**: WAV (automatically converted from browser recording)
- **Channels**: Mono (1 channel)
- **Sampling Rate**: 16000 Hz (automatically handled)

### API Response Format

The app returns comprehensive results including:
- Overall accuracy score
- Fluency, completeness, and pronunciation scores
- Recognized vs reference text comparison
- Phoneme-level details with accuracy scores
- Word-level details with accuracy scores

## Example Usage

```python
# The app will display results like this:
{
  "success": true,
  "result": {
    "overall_score": 85.5,
    "fluency_score": 90.2,
    "completeness_score": 88.7,
    "pronunciation_score": 82.3,
    "recognized_text": "Bonjour, comment ça va ?",
    "reference_text": "Bonjour, comment ça va ?",
    "phoneme_details": [...],
    "word_details": [...]
  }
}
```

## Troubleshooting

- **Audio Issues**: Ensure your microphone is working and browser permissions are granted
- **API Errors**: Check that the Azure Speech Services credentials are correct
- **Language Mismatch**: Make sure the selected language matches the text you're reading
- **Dependencies**: Ensure all required packages are installed

## Development

This is a simplified version focused on core functionality. The app can be easily extended to:
- Add more languages
- Integrate with databases
- Add user authentication
- Implement result storage
- Add progress tracking

## Azure Speech Services Benefits

- **Reliable**: Microsoft's enterprise-grade speech recognition
- **Accurate**: State-of-the-art pronunciation assessment
- **Multilingual**: Support for 100+ languages
- **Detailed**: Phoneme and word-level analysis
- **Scalable**: Cloud-based service with high availability 