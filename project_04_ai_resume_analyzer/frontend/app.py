# ── IMPORTS ──────────────────────────────────────────────────────────────────

# Streamlit — builds the web interface
import streamlit as st

# requests — sends HTTP requests from Streamlit to FastAPI
import requests

# pdfplumber — extracts text from uploaded PDF files
import pdfplumber

# ── PAGE SETUP ────────────────────────────────────────────────────────────────

# Set browser tab title and layout
st.set_page_config(page_title="AI Resume Analyzer", layout="centered")

# Main title
st.title("🤖 AI-Powered Resume Analyzer")

# Subtitle
st.markdown("Upload your resume or paste it below, then add the job description to get an AI match score, missing keywords, and improvement suggestions.")

# ── INPUT SECTION ─────────────────────────────────────────────────────────────

# Option 1: Upload a PDF resume
# type=["pdf"] restricts uploads to PDF files only
uploaded_file = st.file_uploader("📄 Upload Your Resume (PDF)", type=["pdf"])

# Option 2: Paste resume as text
# This is still available as a fallback if they don't have a PDF
resume_text = st.text_area("✏️ Or Paste Your Resume Here", height=200)

# Text box for job description — always required
job_description = st.text_area("💼 Paste the Job Description Here", height=200)

# ── SUBMIT BUTTON ─────────────────────────────────────────────────────────────

if st.button("🔍 Analyze Resume"):

    # If user uploaded a PDF, extract the text from it
    # This overwrites whatever was in the paste box
    if uploaded_file is not None:
        # Open the PDF and extract text from all pages
        with pdfplumber.open(uploaded_file) as pdf:
            # Loop through every page, extract text, join with newline
            # if page.extract_text() skips blank pages
            resume_text = "\n".join(
                page.extract_text() for page in pdf.pages if page.extract_text()
            )

    # Check that we have resume text (either from upload or paste)
    # and that job description is filled in
    if not resume_text or not job_description:
        st.warning("Please provide a resume (upload or paste) and a job description before analyzing.")

    else:
        with st.spinner("Analyzing your resume with AI..."):
            try:
                # Send resume text and job description to FastAPI
                response = requests.post(
                    "http://127.0.0.1:8000/analyze",  # FastAPI route
                    json={
                        "resume_text": resume_text,        # text from PDF or paste box
                        "job_description": job_description  # job description from text box
                    },
                    timeout=30  # give up after 30 seconds
                )

                # Check if FastAPI returned success (200) or error
                if response.status_code != 200:
                    st.error("Something went wrong with the analysis. Please try again.")

                else:
                    # Convert JSON response into Python dictionary
                    result = response.json()

                    # Check if Claude returned an error instead of results
                    if "error" in result:
                        st.error(f"Analysis failed: {result['error']}")

                    else:
                        # ── DISPLAY RESULTS ───────────────────────────────────

                        st.subheader("📊 Analysis Results")

                        # Big match score number
                        st.metric(label="Match Score", value=f"{result['match_score']} / 100")

                        # Missing keywords as bullet points
                        st.markdown("### 🔍 Missing Keywords")
                        for keyword in result['missing_keywords']:
                            st.markdown(f"- {keyword}")

                        # Suggestion in highlighted box
                        st.markdown("### 💡 Suggestion")
                        st.info(result['suggestion'])

            except requests.exceptions.ConnectionError:
                # FastAPI is not running
                st.error("❌ Cannot connect to the backend. Make sure FastAPI is running.")

            except requests.exceptions.Timeout:
                # FastAPI took too long
                st.error("⏱️ The request timed out. Please try again.")

            except Exception as e:
                # Any other unexpected error
                st.error(f"Something unexpected happened: {str(e)}")