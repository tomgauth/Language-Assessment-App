from fpdf import FPDF
import streamlit as st
from datetime import datetime
import unicodedata

def clean_text_for_pdf(text):
    """
    Replace non-latin1 characters in the text with their closest ASCII equivalent.
    """
    return unicodedata.normalize('NFKD', text).encode('latin-1', 'ignore').decode('latin-1')

def export_results_to_pdf(username, transcription, vocabulary_score, total_lemmas, unique_lemmas, 
                          fluency_score, wpm, syntax_score, communication_score, prompt_text, code):
    # Generate the current timestamp with date, hour, and minute
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")

    # Create an instance of FPDF
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set title font and size
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Language Assessment Results", ln=True, align="C")

    # Add a line break
    pdf.ln(10)

    # Set regular font for details
    pdf.set_font("Arial", size=12)

    # Clean up text for PDF (remove unsupported characters)
    username = clean_text_for_pdf(username)
    transcription = clean_text_for_pdf(transcription)
    prompt_text = clean_text_for_pdf(prompt_text)

    # Add user information
    pdf.cell(200, 10, f"User Name: {username}", ln=True)
    pdf.cell(200, 10, f"Timestamp: {timestamp.replace('_', ' ')}", ln=True)  # Replace _ with space for a readable timestamp
    pdf.cell(200, 10, f"Question Code: {code}", ln=True)
    pdf.cell(200, 10, f"Prompt Text: {prompt_text}", ln=True)    

    # Add a line break
    pdf.ln(10)

    # Add transcription
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "Transcription:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, transcription)

    # Add a line break
    pdf.ln(10)

    # Add results
    pdf.cell(200, 10, f"Vocabulary Score: {vocabulary_score}", ln=True)
    pdf.cell(200, 10, f"Total Lemmas: {total_lemmas}", ln=True)
    pdf.cell(200, 10, f"Unique Lemmas: {unique_lemmas}", ln=True)
    pdf.cell(200, 10, f"Fluency Score (WPM): {fluency_score}", ln=True)
    pdf.cell(200, 10, f"Words per Minute (WPM): {wpm}", ln=True)
    pdf.cell(200, 10, f"Syntax Score: {syntax_score}", ln=True)
    pdf.cell(200, 10, f"Communication Score: {communication_score}", ln=True)

    # Generate PDF in memory and provide download link
    pdf_output = pdf.output(dest='S').encode('latin1')

    # Construct the filename with username and timestamp
    file_name = f"{username}_results_{timestamp}.pdf"

    # Provide a download button for the PDF
    st.download_button(
        label="Download Results as PDF",
        data=pdf_output,
        file_name=file_name,
        mime="application/pdf"
    )
