# Language Assessment App

A Streamlit-based application for language assessment and practice. This app helps users improve their language skills through audio prompts and provides detailed analysis of their responses.

## Features

- 🎤 Audio recording and transcription
- 📊 Real-time analysis of speaking skills
- 🎯 Multiple skill assessments (fluency, vocabulary, syntax, etc.)
- 📈 Progress tracking
- 🎧 Audio prompts with context
- 📝 Detailed feedback and scoring

## Setup

1. Clone the repository:
```bash
git clone https://github.com/tomgauth/Language-Assessment-App.git
cd Language-Assessment-App
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
CODA_API_KEY=your_coda_api_key
CODA_MAIN_DOC_ID=your_coda_doc_id
CODA_MAIN_USERS_TABLE_ID=your_coda_users_table_id
```

## Running the App

To run the app locally:
```bash
streamlit run mvp.py
```

## Deployment

The app is configured for deployment on Streamlit Cloud. To deploy:

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Set up your environment variables in the Streamlit Cloud dashboard
5. Deploy!

## Project Structure

- `mvp.py` - Main application file
- `services/` - Backend services (transcription, analysis, etc.)
- `models/` - Data models
- `pages/` - Additional Streamlit pages
- `frontend_elements.py` - UI components
- `requirements.txt` - Python dependencies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, contact tom@hackfrenchwithtom.com
