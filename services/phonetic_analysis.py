import azure.cognitiveservices.speech as speechsdk
import json
from typing import Dict, List, Any
import wave
import io
import tempfile
import os

# Azure Speech Services credentials (replace with your secure method in production)
AZURE_SPEECH_KEY = "6Nk0XGWtuEsmRfGzBhJ2CGUseiZ9NKNCY8QIwukSxzZBkRq1a5CcJQQJ99BFAC5RqLJXJ3w3AAAYACOGUOFg"
AZURE_SPEECH_REGION = "westeurope"

def validate_and_convert_audio(audio_file_path: str) -> str:
    """
    Validate and convert audio file to proper format for Azure Speech Services.
    Azure requires: 16kHz, 16-bit, mono PCM WAV format.
    """
    try:
        # Read the original file
        with open(audio_file_path, 'rb') as f:
            audio_data = f.read()
        
        # Create a properly formatted WAV file using pydub
        import pydub
        from pydub import AudioSegment
        
        # Try to load audio from the raw data
        try:
            # First, try to load as if it's already a WAV file
            audio = AudioSegment.from_wav(io.BytesIO(audio_data))
        except:
            try:
                # If that fails, try loading as raw audio data
                # Streamlit audio input might be raw PCM data
                audio = AudioSegment(
                    data=audio_data,
                    sample_width=2,  # 16-bit
                    frame_rate=16000,  # 16kHz
                    channels=1  # mono
                )
            except:
                # If that also fails, try loading from file path with format detection
                audio = AudioSegment.from_file(audio_file_path)
        
        # Convert to proper format: mono, 16kHz, 16-bit
        audio = audio.set_channels(1)  # Convert to mono
        audio = audio.set_frame_rate(16000)  # Set to 16kHz
        audio = audio.set_sample_width(2)  # Set to 16-bit
        
        # Create temporary file with correct format
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        audio.export(temp_file.name, format='wav')
        temp_file.close()
        
        return temp_file.name
        
    except Exception as e:
        print(f"Audio conversion failed: {e}")
        # If conversion fails, try to create a basic WAV file from the raw data
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            
            # Create a simple WAV header for 16kHz, 16-bit, mono
            import struct
            
            # WAV header for 16kHz, 16-bit, mono
            sample_rate = 16000
            channels = 1
            sample_width = 2
            audio_length = len(audio_data)
            
            # Write WAV header
            temp_file.write(b'RIFF')
            temp_file.write(struct.pack('<I', 36 + audio_length))
            temp_file.write(b'WAVE')
            temp_file.write(b'fmt ')
            temp_file.write(struct.pack('<I', 16))
            temp_file.write(struct.pack('<H', 1))  # PCM
            temp_file.write(struct.pack('<H', channels))
            temp_file.write(struct.pack('<I', sample_rate))
            temp_file.write(struct.pack('<I', sample_rate * channels * sample_width))
            temp_file.write(struct.pack('<H', channels * sample_width))
            temp_file.write(struct.pack('<H', sample_width * 8))
            temp_file.write(b'data')
            temp_file.write(struct.pack('<I', audio_length))
            
            # Write audio data
            temp_file.write(audio_data)
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e2:
            print(f"Fallback WAV creation also failed: {e2}")
            return audio_file_path  # Return original if all else fails

class PhoneticAnalysisService:
    def __init__(self, language: str = "fr-FR"):
        self.language = language
        self.speech_key = AZURE_SPEECH_KEY
        self.speech_region = AZURE_SPEECH_REGION

    def analyze_pronunciation(self, audio_file_path: str, reference_text: str = "") -> Dict[str, Any]:
        # Validate and convert audio to proper format
        converted_audio_path = validate_and_convert_audio(audio_file_path)
        
        speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
        audio_config = speechsdk.audio.AudioConfig(filename=converted_audio_path)
        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, language=self.language, audio_config=audio_config)
        if reference_text:
            pron_config = speechsdk.PronunciationAssessmentConfig(
                reference_text=reference_text,
                grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
                granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
                enable_miscue=True
            )
        else:
            pron_config = speechsdk.PronunciationAssessmentConfig(
                reference_text="",
                grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
                granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
                enable_miscue=False
            )
        if self.language == "fr-FR":
            pron_config.enable_prosody_assessment()
        pron_config.apply_to(recognizer)
        result = recognizer.recognize_once()
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            assessment = speechsdk.PronunciationAssessmentResult(result)
            json_result = result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult)
            details = json.loads(json_result) if json_result else {}
            word_scores = self._extract_word_scores(details)
            overall_score = self._calculate_overall_score(word_scores)
            
            # Clean up converted file if it's different from original
            if converted_audio_path != audio_file_path and os.path.exists(converted_audio_path):
                try:
                    os.unlink(converted_audio_path)
                except:
                    pass
            
            return {
                "success": True,
                "score": overall_score,
                "word_scores": word_scores,
                "details": details,
                "recognized_text": result.text
            }
        else:
            # Clean up converted file if it's different from original
            if converted_audio_path != audio_file_path and os.path.exists(converted_audio_path):
                try:
                    os.unlink(converted_audio_path)
                except:
                    pass
            
            return {"success": False, "error": str(result.reason)}

    def _extract_word_scores(self, details: Dict[str, Any]) -> List[Dict[str, Any]]:
        word_scores = []
        if 'NBest' in details and details['NBest']:
            words = details['NBest'][0].get('Words', [])
            for word in words:
                if 'PronunciationAssessment' in word and 'AccuracyScore' in word['PronunciationAssessment']:
                    score = word['PronunciationAssessment']['AccuracyScore']
                    color = self._get_score_color(score)
                    word_scores.append({
                        "word": word.get('Word', ''),
                        "score": score,
                        "color": color
                    })
        return word_scores

    def _get_score_color(self, score: float) -> str:
        if score >= 90:
            return "#2E8B57"  # Green
        elif score >= 70:
            return "#FFD700"  # Yellow
        elif score >= 50:
            return "#FF8C00"  # Orange
        else:
            return "#DC143C"  # Red

    def _calculate_overall_score(self, word_scores: List[Dict[str, Any]]) -> float:
        if not word_scores:
            return 0.0
        return round(sum(w["score"] for w in word_scores) / len(word_scores), 1)

    def analyze_pronunciation_from_bytes(self, audio_bytes: bytes, reference_text: str = "") -> Dict[str, Any]:
        """Analyze pronunciation from audio bytes (from Streamlit audio_input)"""
        try:
            # Create a proper WAV file from the audio bytes
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            
            # Create WAV header for 16kHz, 16-bit, mono
            import struct
            
            sample_rate = 16000
            channels = 1
            sample_width = 2
            audio_length = len(audio_bytes)
            
            # Write WAV header
            temp_file.write(b'RIFF')
            temp_file.write(struct.pack('<I', 36 + audio_length))
            temp_file.write(b'WAVE')
            temp_file.write(b'fmt ')
            temp_file.write(struct.pack('<I', 16))
            temp_file.write(struct.pack('<H', 1))  # PCM
            temp_file.write(struct.pack('<H', channels))
            temp_file.write(struct.pack('<I', sample_rate))
            temp_file.write(struct.pack('<I', sample_rate * channels * sample_width))
            temp_file.write(struct.pack('<H', channels * sample_width))
            temp_file.write(struct.pack('<H', sample_width * 8))
            temp_file.write(b'data')
            temp_file.write(struct.pack('<I', audio_length))
            
            # Write audio data
            temp_file.write(audio_bytes)
            temp_file.close()
            
            # Analyze the created WAV file
            result = self.analyze_pronunciation(temp_file.name, reference_text)
            
            # Clean up temporary file
            try:
                os.unlink(temp_file.name)
            except:
                pass
            
            return result
            
        except Exception as e:
            return {"success": False, "error": f"Failed to process audio bytes: {str(e)}"}

def phonetic_analysis_skill(audio_input, reference_text: str = "", language: str = "fr-FR") -> Dict[str, Any]:
    """
    Analyze pronunciation from audio input (file path or bytes).
    
    Args:
        audio_input: Either a file path (str) or audio bytes (bytes)
        reference_text: Optional reference text for comparison
        language: Language code (default: "fr-FR")
    """
    try:
        service = PhoneticAnalysisService(language=language)
        
        # Handle different input types
        if isinstance(audio_input, str):
            # File path provided
            result = service.analyze_pronunciation(audio_input, reference_text)
        else:
            # Bytes provided (from Streamlit audio_input)
            result = service.analyze_pronunciation_from_bytes(audio_input, reference_text)
        
        if result["success"]:
            # Create color-coded feedback
            feedback_parts = []
            for w in result["word_scores"]:
                feedback_parts.append(f"<span style='color: {w['color']}; font-weight: bold;'>{w['word']}</span>")
            
            formatted_feedback = " ".join(feedback_parts)
            
            # Create detailed feedback text
            detailed_feedback = f"Pronunciation Analysis Results:\n\n"
            detailed_feedback += f"Overall Score: {result['score']}/100\n"
            detailed_feedback += f"Recognized Text: {result['recognized_text']}\n\n"
            detailed_feedback += "Word-level Analysis:\n"
            for w in result["word_scores"]:
                detailed_feedback += f"- {w['word']}: {w['score']}/100\n"
            
            return {
                "overall_score": int(result["score"]),
                "formatted_feedback": detailed_feedback,
                "word_scores": result["word_scores"],
                "details": result["details"],
                "recognized_text": result["recognized_text"],
                "color_coded_feedback": formatted_feedback
            }
        else:
            return {
                "overall_score": 0,
                "formatted_feedback": f"Analysis failed: {result.get('error', 'Unknown error')}",
                "word_scores": [],
                "details": {},
                "recognized_text": "",
                "color_coded_feedback": ""
            }
    except Exception as e:
        # Fallback error handling
        error_msg = f"Phonetic analysis error: {str(e)}"
        if "SPXERR_UNEXPECTED_EOF" in str(e):
            error_msg = "Audio file format issue. Please ensure the audio is clear and properly recorded."
        elif "SPXERR_AUDIO_SYS" in str(e):
            error_msg = "Audio system error. Please try recording again."
        elif "SPXERR_TIMEOUT" in str(e):
            error_msg = "Analysis timed out. Please try with a shorter audio clip."
        
        return {
            "overall_score": 0,
            "formatted_feedback": error_msg,
            "word_scores": [],
            "details": {},
            "recognized_text": "",
            "color_coded_feedback": ""
        } 