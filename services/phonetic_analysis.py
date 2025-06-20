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
        
        # Try to read as WAV to check format
        try:
            with wave.open(io.BytesIO(audio_data), 'rb') as wav_file:
                # Check if it's already in the correct format
                if (wav_file.getnchannels() == 1 and  # mono
                    wav_file.getsampwidth() == 2 and  # 16-bit
                    wav_file.getframerate() == 16000):  # 16kHz
                    return audio_file_path  # Already in correct format
        except:
            pass  # Not a valid WAV file, will convert
        
        # Create a properly formatted WAV file
        import pydub
        from pydub import AudioSegment
        
        # Load audio (pydub can handle various formats)
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_data))
        except:
            # If pydub can't read it, try loading from file path
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
        return audio_file_path  # Return original if conversion fails

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

def phonetic_analysis_skill(audio_file_path: str, reference_text: str = "", language: str = "fr-FR") -> Dict[str, Any]:
    try:
        service = PhoneticAnalysisService(language=language)
        result = service.analyze_pronunciation(audio_file_path, reference_text)
        
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