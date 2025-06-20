# Pronunciation Evaluator App

A Streamlit-based pronunciation assessment tool that uses SpeechSuper API to evaluate pronunciation accuracy for French and Russian languages.

## Features

- **User Authentication**: Enter username to access personalized content
- **Random Paragraph Selection**: Get practice paragraphs from user's database
- **Audio Recording**: Record pronunciation using browser microphone
- **AI-Powered Assessment**: SpeechSuper API provides detailed pronunciation analysis
- **Score Display**: Overall score and word-level feedback
- **Result Storage**: Save assessment results to user's database
- **Dashboard Integration**: Results appear on user's main dashboard

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements_pronunciation.txt
```

### 2. Environment Variables

Create a `.env` file in the project root with:

```env
CODA_API_KEY=your_coda_api_key_here
```

### 3. SpeechSuper API Credentials

The app is pre-configured with the provided SpeechSuper credentials:
- App Key: `17473823180004c9`
- Secret Key: `e2f7f083346cc5a6ebdf8069dfe57398`

## Usage

### Running the App

```bash
streamlit run pronunciation_app.py
```

### User Flow

1. **Enter Username**: Input your username to access personalized content
2. **Select Language**: Choose between French or Russian assessment
3. **Read Paragraph**: A random paragraph from your database will be displayed
4. **Record Pronunciation**: Click to record yourself reading the paragraph
5. **Get Assessment**: Click "Assess Pronunciation" to receive AI feedback
6. **View Results**: See overall score, word-level feedback, and detailed analysis
7. **Save Results**: Assessment is automatically saved to your database

## API Integration

### SpeechSuper API

The app integrates with SpeechSuper's pronunciation assessment API:

- **French Assessment**: Uses `para.eval.fr` coreType
- **Russian Assessment**: Uses `para.eval.ru` coreType
- **Audio Requirements**: 
  - Format: wav, mp3, opus, ogg, amr
  - Channel: Mono (1 channel)
  - Sampling rate: 16000 Hz
  - Bitrate: At least 96 kbps

### Score Interpretation

- **80-100**: Excellent pronunciation 🎉
- **60-79**: Good pronunciation with room for improvement 📈
- **40-59**: Fair pronunciation - keep practicing 💪
- **0-39**: Pronunciation needs work - don't give up! 🔄

## Database Integration

### Coda Tables Used

- **Demo Users Table**: User authentication and data
- **Demo Prompts Table**: Source of practice paragraphs
- **Pronunciation Results**: Assessment results storage

### Data Structure

Each pronunciation assessment saves:
- Username
- Session ID
- Date/Time
- Prompt ID
- Paragraph text
- Overall score
- Detailed feedback
- Word-level scores (JSON)

## Technical Details

### Audio Processing

1. **Recording**: Browser-based audio recording
2. **Conversion**: Audio converted to base64 format
3. **API Call**: Sent to SpeechSuper with paragraph text
4. **Response Parsing**: Extracts scores and feedback
5. **Display**: Formatted results with color coding

### Error Handling

- User validation
- Audio format validation
- API error handling
- Database error handling
- Graceful fallbacks

## Customization

### Adding New Languages

To add support for additional languages:

1. Update the language selection dropdown
2. Add new coreType mapping
3. Update language-specific prompts
4. Test with SpeechSuper API

### Modifying Scoring

To customize score interpretation:

1. Update the `display_pronunciation_results` function
2. Modify score thresholds
3. Adjust feedback messages
4. Update color coding

## Troubleshooting

### Common Issues

1. **Audio Recording Fails**
   - Check browser microphone permissions
   - Ensure HTTPS connection (required for audio)
   - Try refreshing the page

2. **API Errors**
   - Verify SpeechSuper credentials
   - Check audio format requirements
   - Ensure paragraph text is valid

3. **Database Errors**
   - Verify Coda API key
   - Check table permissions
   - Ensure user exists in database

### Debug Mode

Enable debug output by uncommenting debug sections in the code:

```python
# DEBUG: Log API response
st.write("API Response:", api_response)
```

## Future Enhancements

- **Real-time Feedback**: Live pronunciation assessment
- **Progress Tracking**: Historical score analysis
- **Custom Paragraphs**: User-uploaded content
- **Multiple Accents**: Regional pronunciation variants
- **Mobile Optimization**: Better mobile experience
- **Offline Mode**: Local pronunciation assessment

## Support

For technical support or questions:
- Check the SpeechSuper API documentation
- Review the main app documentation
- Contact the development team

## License

This app is part of the Language Assessment MVP project. 