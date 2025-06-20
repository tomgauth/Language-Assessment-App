import streamlit as st
import requests
import json
import base64
import io
import time
import hashlib
import tempfile
import os

# SpeechSuper API credentials
SPEECHSUPER_APP_KEY = "17473823180004c9"
SPEECHSUPER_SECRET_KEY = "e2f7f083346cc5a6ebdf8069dfe57398"
SPEECHSUPER_BASE_URL = "https://api.speechsuper.com/"

def convert_audio_to_wav(audio_data):
    """Convert Streamlit audio data to WAV format and save to temporary file"""
    try:
        # Read audio data
        audio_bytes = audio_data.read()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        return temp_file_path
    except Exception as e:
        st.error(f"Error converting audio: {str(e)}")
        return None

def call_speechsuper_api(audio_file_path: str, ref_text: str, language: str = "fr"):
    """Call SpeechSuper API using the correct format with connect/start commands"""
    try:
        # Determine coreType based on language
        core_type = "para.eval.fr" if language == "fr" else "para.eval.ru"
        
        # Generate timestamp
        timestamp = str(int(time.time()))
        user_id = "guest"
        
        # Generate signatures
        connect_str = (SPEECHSUPER_APP_KEY + timestamp + SPEECHSUPER_SECRET_KEY).encode("utf-8")
        connect_sig = hashlib.sha1(connect_str).hexdigest()
        
        start_str = (SPEECHSUPER_APP_KEY + timestamp + user_id + SPEECHSUPER_SECRET_KEY).encode("utf-8")
        start_sig = hashlib.sha1(start_str).hexdigest()
        
        # Prepare parameters
        params = {
            "connect": {
                "cmd": "connect",
                "param": {
                    "sdk": {
                        "version": 16777472,
                        "source": 9,
                        "protocol": 2
                    },
                    "app": {
                        "applicationId": SPEECHSUPER_APP_KEY,
                        "sig": connect_sig,
                        "timestamp": timestamp
                    }
                }
            },
            "start": {
                "cmd": "start",
                "param": {
                    "app": {
                        "userId": user_id,
                        "applicationId": SPEECHSUPER_APP_KEY,
                        "timestamp": timestamp,
                        "sig": start_sig
                    },
                    "audio": {
                        "audioType": "wav",
                        "channel": 1,
                        "sampleBytes": 2,
                        "sampleRate": 16000
                    },
                    "request": {
                        "coreType": core_type,
                        "refText": ref_text,
                        "tokenId": "tokenId",
                        "paragraph_need_word_score": 1  # Get word-level scores
                    }
                }
            }
        }
        
        # Convert params to JSON string
        datas = json.dumps(params)
        
        # Prepare request data
        data = {'text': datas}
        headers = {"Request-Index": "0"}
        
        # Open audio file
        with open(audio_file_path, 'rb') as audio_file:
            files = {"audio": audio_file}
            
            # Make API request
            url = SPEECHSUPER_BASE_URL + core_type
            response = requests.post(url, data=data, headers=headers, files=files)
        
        # Clean up temporary file
        try:
            os.unlink(audio_file_path)
        except:
            pass
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error calling SpeechSuper API: {str(e)}")
        # Clean up temporary file on error
        try:
            if audio_file_path and os.path.exists(audio_file_path):
                os.unlink(audio_file_path)
        except:
            pass
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
                
                # Convert audio to WAV file
                audio_file_path = convert_audio_to_wav(audio_data)
                
                if not audio_file_path:
                    st.error("Failed to convert audio format")
                    return
                
                # Call SpeechSuper API
                api_response = call_speechsuper_api(
                    audio_file_path=audio_file_path,
                    ref_text=paragraph,
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