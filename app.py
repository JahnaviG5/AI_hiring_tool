import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
from pdf2image import convert_from_path
import pytesseract
import pdfplumber

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Check API key
if not api_key:
    st.error("GOOGLE_API_KEY not found. Please check your .env file.")
else:
    genai.configure(api_key=api_key)

# Page setup
st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title("📄 AI Resume Analyzer")
st.write("Analyze your resume and match it with job descriptions using Google Gemini AI.")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        if text.strip():
            return text.strip()
    except Exception as e:
        st.warning(f"Direct text extraction failed: {e}")

    # Fallback to OCR
    st.info("Using OCR as fallback for image-based PDF...")
    try:
        images = convert_from_path(pdf_path)
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
    except Exception as e:
        st.error(f"OCR failed: {e}")
    return text.strip()

# Function to get response from Gemini AI
def analyze_resume(resume_text, job_description=None):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
You are an experienced HR with technical expertise in roles like Data Science, DevOps, AI, etc.
Please review this resume and share:
- If the profile fits a role
- Strengths and weaknesses
- Existing skills
- Suggested improvements and courses

Resume:
{resume_text}
"""
    if job_description:
        prompt += f"\n\nCompare it to this Job Description:\n{job_description}"

    response = model.generate_content(prompt)
    return response.text.strip()

# Upload section
col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📤 Upload your resume (PDF)", type=["pdf"])
with col2:
    job_description = st.text_area("💼 Job Description", placeholder="Paste job description (optional)...")

# Handle file
if uploaded_file:
    st.success("✅ Resume uploaded successfully!")
    with open("uploaded_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    resume_text = extract_text_from_pdf("uploaded_resume.pdf")
    st.write("📄 **Extracted Resume Preview:**")
    st.text(resume_text[:1000])  # show first 1000 characters

    if st.button("🔍 Analyze Resume"):
        with st.spinner("Analyzing with Google Gemini AI..."):
            try:
                result = analyze_resume(resume_text, job_description)
                st.success("✅ Analysis complete!")
                st.markdown(result)
            except Exception as e:
                st.error(f"❌ Failed to analyze resume: {e}")
else:
    st.warning("📎 Please upload a resume PDF to begin.")

# Footer
st.markdown("---")
st.markdown(
    """<p style='text-align: center;'>Powered by <b>Streamlit</b> & <b>Google Gemini AI</b> | Developed by 
    <a href="https://www.linkedin.com/in/dutta-sujoy/" target="_blank" style="text-decoration: none;">Sujoy Dutta</a></p>""",
    unsafe_allow_html=True
)

st.write("hii ladd")