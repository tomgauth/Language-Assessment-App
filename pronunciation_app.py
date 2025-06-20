import streamlit as st
import os
import tempfile
import azure.cognitiveservices.speech as speechsdk
import json

# Azure Speech Services credentials
AZURE_SPEECH_KEY = "6Nk0XGWtuEsmRfGzBhJ2CGUseiZ9NKNCY8QIwukSxzZBkRq1a5CcJQQJ99BFAC5RqLJXJ3w3AAAYACOGUOFg"
AZURE_SPEECH_REGION = "westeurope"
AZURE_SPEECH_ENDPOINT = "https://westeurope.api.cognitive.microsoft.com/"

def convert_audio_to_wav(audio_data):
    """Convert Streamlit audio data to WAV format and save to temporary file"""
    try:
        # Read audio data
        audio_bytes = audio_data.read()
        
        # DEBUG: Log audio data info
        st.write("🔍 DEBUG: Audio data info:")
        st.write(f"  - Audio data type: {type(audio_data)}")
        st.write(f"  - Audio bytes length: {len(audio_bytes)}")
        st.write(f"  - Audio data name: {getattr(audio_data, 'name', 'No name')}")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        # DEBUG: Log file creation
        st.write(f"  - Temporary file created: {temp_file_path}")
        st.write(f"  - File size: {os.path.getsize(temp_file_path)} bytes")
        
        return temp_file_path
    except Exception as e:
        st.error(f"Error converting audio: {str(e)}")
        return None

def call_azure_speech_api(audio_file_path: str, reference_text: str = "", language: str = "en-US"):
    """Call Azure Speech Services for pronunciation assessment"""
    try:
        # DEBUG: Log basic parameters
        st.write("🔍 DEBUG: Azure Speech API parameters:")
        st.write(f"  - Language: {language}")
        st.write(f"  - Reference text: {'(unscripted assessment)' if not reference_text else reference_text[:100]}")
        st.write(f"  - Audio file path: {audio_file_path}")
        st.write(f"  - Azure Key: {AZURE_SPEECH_KEY[:10]}...")
        st.write(f"  - Azure Region: {AZURE_SPEECH_REGION}")
        
        # 1) Set up your subscription info
        speech_key = AZURE_SPEECH_KEY
        service_region = AZURE_SPEECH_REGION
        
        # 2) Configure speech
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
        
        # DEBUG: Log speech config
        st.write("🔍 DEBUG: Speech configuration:")
        st.write(f"  - Speech config created: {speech_config is not None}")
        st.write(f"  - Audio config created: {audio_config is not None}")
        
        # 3) Create speech recognizer with language specification
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config, 
            language=language, 
            audio_config=audio_config
        )
        
        # DEBUG: Log recognizer setup
        st.write("🔍 DEBUG: Recognizer setup:")
        st.write(f"  - Speech recognizer created: {speech_recognizer is not None}")
        st.write(f"  - Language set to: {language}")
        
        # 4) Set up Pronunciation Assessment
        if reference_text:
            # Scripted assessment (with reference text)
            pronunciation_config = speechsdk.PronunciationAssessmentConfig(
                reference_text=reference_text,
                grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
                granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
                enable_miscue=True
            )
            st.write("  - Assessment type: Scripted (with reference text)")
        else:
            # Unscripted assessment (no reference text)
            pronunciation_config = speechsdk.PronunciationAssessmentConfig(
                reference_text="",
                grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
                granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
                enable_miscue=False
            )
            st.write("  - Assessment type: Unscripted (free speech)")
        
        # Enable prosody assessment for en-US
        if language == "en-US":
            pronunciation_config.enable_prosody_assessment()
            st.write("  - Prosody assessment enabled for en-US")
        
        # DEBUG: Log pronunciation config
        st.write("🔍 DEBUG: Pronunciation configuration:")
        st.write(f"  - Pronunciation config created: {pronunciation_config is not None}")
        st.write(f"  - Grading system: HundredMark")
        st.write(f"  - Granularity: Phoneme")
        st.write(f"  - Enable miscue: {reference_text != ''}")
        
        # 5) Apply pronunciation config to recognizer
        pronunciation_config.apply_to(speech_recognizer)
        st.write("  - Pronunciation config applied to recognizer")
        
        # 6) Recognize once and get results
        st.write("🔍 DEBUG: Starting recognition...")
        speech_recognition_result = speech_recognizer.recognize_once()
        
        # DEBUG: Log recognition result
        st.write("🔍 DEBUG: Recognition result:")
        st.write(f"  - Result reason: {speech_recognition_result.reason}")
        st.write(f"  - Result text: {speech_recognition_result.text}")
        
        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # Get pronunciation assessment result as SDK object
            pronunciation_assessment_result = speechsdk.PronunciationAssessmentResult(speech_recognition_result)
            
            # Get pronunciation assessment result as JSON string
            pronunciation_assessment_result_json = speech_recognition_result.properties.get(
                speechsdk.PropertyId.SpeechServiceResponse_JsonResult
            )
            
            # DEBUG: Log pronunciation assessment
            st.write("🔍 DEBUG: Pronunciation assessment:")
            st.write(f"  - Accuracy score: {pronunciation_assessment_result.accuracy_score}")
            st.write(f"  - Fluency score: {pronunciation_assessment_result.fluency_score}")
            st.write(f"  - Completeness score: {pronunciation_assessment_result.completeness_score}")
            st.write(f"  - Pronunciation score: {pronunciation_assessment_result.pronunciation_score}")
            
            # Try to get prosody score if available
            prosody_score = None
            try:
                prosody_score = pronunciation_assessment_result.prosody_score
                st.write(f"  - Prosody score: {prosody_score}")
            except:
                st.write("  - Prosody score: Not available")
            
            # Prepare detailed results
            phoneme_details = []
            try:
                if hasattr(pronunciation_assessment_result, 'phoneme_details'):
                    for pd in pronunciation_assessment_result.phoneme_details:
                        phoneme_details.append({
                            "phoneme": pd.phoneme,
                            "accuracy_score": pd.accuracy_score,
                            "error_type": pd.error_type
                        })
                    st.write(f"  - Phoneme details: {len(phoneme_details)} phonemes found")
                else:
                    st.write("  - Phoneme details: Not available in this SDK version")
            except Exception as phoneme_error:
                st.write(f"  - Phoneme details error: {phoneme_error}")
            
            # Create comprehensive result structure
            api_response = {
                "success": True,
                "result": {
                    "accuracy_score": pronunciation_assessment_result.accuracy_score,
                    "fluency_score": pronunciation_assessment_result.fluency_score,
                    "completeness_score": pronunciation_assessment_result.completeness_score,
                    "pronunciation_score": pronunciation_assessment_result.pronunciation_score,
                    "prosody_score": prosody_score,
                    "recognized_text": speech_recognition_result.text,
                    "reference_text": reference_text,
                    "phoneme_details": phoneme_details,
                    "word_details": [],
                    "raw_json": pronunciation_assessment_result_json
                }
            }
            
            # Add word-level details if available
            try:
                if hasattr(pronunciation_assessment_result, 'word_details'):
                    for wd in pronunciation_assessment_result.word_details:
                        api_response["result"]["word_details"].append({
                            "word": wd.word,
                            "accuracy_score": wd.accuracy_score,
                            "error_type": wd.error_type
                        })
                    st.write(f"  - Word details: {len(api_response['result']['word_details'])} words found")
                else:
                    st.write("  - Word details: Not available in this SDK version")
            except Exception as word_error:
                st.write(f"  - Word details error: {word_error}")
            
            st.write("  - API response prepared successfully")
            return api_response
            
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancel = speechsdk.CancellationDetails(speech_recognition_result)
            st.error(f"Recognition canceled: {cancel.reason}")
            if cancel.reason == speechsdk.CancellationReason.Error:
                st.error(f"Error details: {cancel.error_details}")
            
            return {
                "success": False,
                "error": "Recognition canceled",
                "error_details": cancel.error_details if cancel.reason == speechsdk.CancellationReason.Error else None
            }
        else:
            st.error(f"Unexpected result reason: {speech_recognition_result.reason}")
            return {
                "success": False,
                "error": f"Unexpected result reason: {speech_recognition_result.reason}"
            }
            
    except Exception as e:
        st.error(f"Error calling Azure Speech API: {str(e)}")
        import traceback
        st.write("🔍 DEBUG: Full traceback:")
        st.write(traceback.format_exc())
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Simple pronunciation evaluator app using Azure Speech Services"""
    st.set_page_config(
        page_title="Pronunciation Evaluator",
        page_icon="🎤",
        layout="centered"
    )
    
    st.title("🎤 Free Speech Pronunciation Evaluator")
    st.markdown("**Simple pronunciation assessment using Microsoft Azure Speech Services - Just speak naturally!**")
    
    # Language selection
    language = st.selectbox(
        "Select language:",
        ["English", "French", "Russian"],
        format_func=lambda x: "🇺🇸 English" if x == "English" else "🇫🇷 French" if x == "French" else "🇷🇺 Russian"
    )
    
    # Get language code for Azure API
    lang_code = "en-US" if language == "English" else "fr-FR" if language == "French" else "ru-RU"
    
    st.markdown("---")
    
    # Audio recording
    st.subheader("🎤 Record your pronunciation:")
    st.info("💡 **Recording Tips:** Speak naturally in your chosen language. You can say anything - introduce yourself, describe your day, or just talk about any topic. The AI will assess your pronunciation, fluency, and overall speaking quality.")
    
    audio_data = st.audio_input(
        label="Click to record your pronunciation",
        key="pronunciation_recorder",
        help="Record yourself speaking naturally in your chosen language"
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
                
                # Call Azure Speech API
                api_response = call_azure_speech_api(
                    audio_file_path=audio_file_path,
                    reference_text="",
                    language=lang_code
                )
                
                # Clean up temporary file
                try:
                    os.unlink(audio_file_path)
                    st.write("  - Temporary file cleaned up successfully")
                except Exception as cleanup_error:
                    st.write(f"  - Cleanup error: {cleanup_error}")
                
                if not api_response or not api_response.get("success", False):
                    st.error("Failed to get pronunciation assessment")
                    if api_response and "error" in api_response:
                        st.error(f"Error: {api_response['error']}")
                    return
                
                # Display results
                st.success("✅ Assessment complete!")
                
                # Show detailed summary FIRST (above debugging)
                if 'result' in api_response:
                    result = api_response['result']
                    
                    st.subheader("🎯 Detailed Summary:")
                    
                    # Create columns for scores
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            label="Accuracy Score",
                            value=f"{result.get('accuracy_score', 0):.1f}/100"
                        )
                    
                    with col2:
                        st.metric(
                            label="Fluency",
                            value=f"{result.get('fluency_score', 0):.1f}/100"
                        )
                    
                    with col3:
                        st.metric(
                            label="Completeness",
                            value=f"{result.get('completeness_score', 0):.1f}/100"
                        )
                    
                    with col4:
                        st.metric(
                            label="Pronunciation",
                            value=f"{result.get('pronunciation_score', 0):.1f}/100"
                        )
                    
                    # Show prosody score if available
                    if result.get('prosody_score') is not None:
                        st.metric(
                            label="Prosody Score",
                            value=f"{result['prosody_score']:.1f}/100"
                        )
                    
                    # Show recognized text
                    st.subheader("📝 Recognized Text:")
                    st.write(result.get('recognized_text', ''))
                    
                    # Overall feedback
                    accuracy_score = result.get('accuracy_score', 0)
                    st.subheader("💡 Feedback:")
                    
                    if accuracy_score >= 80:
                        st.success("Excellent pronunciation! 🎉")
                    elif accuracy_score >= 60:
                        st.info("Good pronunciation with room for improvement! 📈")
                    elif accuracy_score >= 40:
                        st.warning("Fair pronunciation - keep practicing! 💪")
                    else:
                        st.error("Pronunciation needs work - don't give up! 🔄")
                
                # Show results as JSON (debugging info)
                st.subheader("📊 Assessment Results (Debug):")
                st.json(api_response)

if __name__ == "__main__":
    main()
