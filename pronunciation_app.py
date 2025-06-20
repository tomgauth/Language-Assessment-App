import streamlit as st
import requests
import json
import base64
import io

# SpeechSuper API credentials
SPEECHSUPER_APP_KEY = "17473823180004c9"
SPEECHSUPER_SECRET_KEY = "e2f7f083346cc5a6ebdf8069dfe57398"
SPEECHSUPER_BASE_URL = "https://api.speechsuper.com/"

def convert_audio_to_speechsuper_format(audio_data):
    """Convert Streamlit audio data to SpeechSuper format"""
    try:
        # Convert audio data to base64
        audio_bytes = audio_data.read()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        return audio_base64
    except Exception as e:
        st.error(f"Error converting audio: {str(e)}")
        return None

def call_speechsuper_api(audio_base64: str, paragraph: str, language: str = "fr"):
    """Call SpeechSuper API for pronunciation assessment"""
    try:
        # Determine coreType based on language
        core_type = "para.eval.fr" if language == "fr" else "para.eval.ru"
        
        # Prepare request payload
        payload = {
            "appKey": SPEECHSUPER_APP_KEY,
            "secretKey": SPEECHSUPER_SECRET_KEY,
            "coreType": core_type,
            "audio": audio_base64,
            "text": paragraph,
            "paragraph_need_word_score": 1  # Get word-level scores
        }
        
        # Make API request
        response = requests.post(
            SPEECHSUPER_BASE_URL + "para.eval",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error calling SpeechSuper API: {str(e)}")
        return None

def main():
    """Simple pronunciation evaluator app"""
    st.set_page_config(
        page_title="Pronunciation Evaluator",
        page_icon="🎤",
        layout="centered"
    )
    
    st.title("🎤 Pronunciation Evaluator")
    st.markdown("**Simple pronunciation assessment using SpeechSuper API**")
    
    # Language selection
    language = st.selectbox(
        "Select language:",
        ["French", "Russian"],
        format_func=lambda x: "🇫🇷 French" if x == "French" else "🇷🇺 Russian"
    )
    
    # Get language code for API
    lang_code = "fr" if language == "French" else "ru"
    
    st.markdown("---")
    
    # Text input for paragraph
    st.subheader("📝 Enter the text to read:")
    paragraph = st.text_area(
        "Paragraph text:",
        height=200,
        placeholder="Enter the text you want to read for pronunciation assessment...",
        help="Type or paste the text you want to read aloud"
    )
    
    if not paragraph.strip():
        st.warning("Please enter some text to read.")
        return
    
    st.markdown("---")
    
    # Audio recording
    st.subheader("🎤 Record your pronunciation:")
    st.info("💡 **Recording Tips:** Speak clearly and naturally. Read the text exactly as written.")
    
    audio_data = st.audio_input(
        label="Click to record your pronunciation",
        key="pronunciation_recorder",
        help="Record yourself reading the text above"
    )
    
    if audio_data is not None:
        if st.button("🎯 Assess Pronunciation", type="primary"):
            # Show progress
            with st.spinner("Processing pronunciation assessment..."):
                
                # Convert audio to SpeechSuper format
                audio_base64 = convert_audio_to_speechsuper_format(audio_data)
                
                if not audio_base64:
                    st.error("Failed to convert audio format")
                    return
                
                # Call SpeechSuper API
                api_response = call_speechsuper_api(
                    audio_base64=audio_base64,
                    paragraph=paragraph,
                    language=lang_code
                )
                
                if not api_response:
                    st.error("Failed to get pronunciation assessment")
                    return
                
                # Display results
                st.success("✅ Assessment complete!")
                
                # Show results as JSON
                st.subheader("📊 Assessment Results:")
                st.json(api_response)
                
                # Also show a simple summary if available
                if 'result' in api_response:
                    result = api_response['result']
                    overall_score = result.get('overall_score', 0)
                    
                    st.subheader("🎯 Summary:")
                    st.metric(
                        label="Overall Score",
                        value=f"{overall_score:.1f}/100"
                    )
                    
                    # Simple feedback based on score
                    if overall_score >= 80:
                        st.success("Excellent pronunciation! 🎉")
                    elif overall_score >= 60:
                        st.info("Good pronunciation with room for improvement! 📈")
                    elif overall_score >= 40:
                        st.warning("Fair pronunciation - keep practicing! 💪")
                    else:
                        st.error("Pronunciation needs work - don't give up! 🔄")

if __name__ == "__main__":
    main() 