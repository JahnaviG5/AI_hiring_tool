import os
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
from pdf2image import convert_from_path
import pytesseract
import pdfplumber

# ✅ Set Streamlit page config FIRST
st.set_page_config(page_title="Resume Analyzer", layout="wide")

# ✅ Load environment variables (optional for local)
load_dotenv()

# ✅ Get API key from environment (especially important for Hugging Face)
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("🚨 GOOGLE_API_KEY is not set. Please configure it in Hugging Face → Settings → Secrets.")
    st.stop()

# ✅ Configure Google Gemini API
genai.configure(api_key=api_key)

# Extract text from PDF
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
        print(f"Direct text extraction failed: {e}")

    # OCR fallback
    print("Falling back to OCR.")
    try:
        images = convert_from_path(pdf_path)
        for image in images:
            text += pytesseract.image_to_string(image) + "\n"
    except Exception as e:
        print(f"OCR failed: {e}")
    return text.strip()

# Generate Gemini response
def analyze_resume(resume_text, job_description=None):
    if not resume_text:
        return "❌ Resume text could not be extracted."

    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    You are an experienced HR with technical expertise. Analyze the following resume:
    
    Resume:
    {resume_text}
    
    Provide:
    - Summary
    - Skills present
    - Skills to improve
    - Suggested courses
    - Strengths and weaknesses
    """

    if job_description:
        prompt += f"""
        Also compare the resume to this job description:
        {job_description}
        """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Gemini API Error: {e}"

# --- Streamlit UI ---

st.title("🤖 AI Resume Analyzer")
st.write("Upload your resume and optionally a job description. We'll evaluate your profile using Google Gemini AI.")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
with col2:
    job_description = st.text_area("Job Description (Optional)", placeholder="Paste job description here...")

if uploaded_file:
    st.success("✅ Resume uploaded successfully!")
    with open("uploaded_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    resume_text = extract_text_from_pdf("uploaded_resume.pdf")

    if st.button("🔍 Analyze Resume"):
        with st.spinner("Analyzing..."):
            result = analyze_resume(resume_text, job_description)
            st.success("✅ Analysis complete!")
            st.write(result)
else:
    st.warning("⚠️ Please upload a resume in PDF format.")

# Footer
st.markdown("---")
st.markdown("""
<p style='text-align: center;'>
    Powered by <b>Streamlit</b> + <b>Google Gemini AI</b><br>
    Developed by <a href='https://www.linkedin.com/in/dutta-sujoy/' target='_blank'><b>Sujoy Dutta</b></a>
</p>
""", unsafe_allow_html=True)