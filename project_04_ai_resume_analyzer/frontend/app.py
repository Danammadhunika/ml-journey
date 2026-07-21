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

# Divider line under the header
st.divider()

# ── INPUT SECTION ─────────────────────────────────────────────────────────────

# Section header for inputs
st.subheader("📥 Input Your Details")

# Option 1: Upload a PDF resume
# type=["pdf"] restricts uploads to PDF files only
uploaded_file = st.file_uploader("📄 Upload Your Resume (PDF)", type=["pdf"])

# Option 2: Paste resume as text
# This is still available as a fallback if they don't have a PDF
resume_text = st.text_area("✏️ Or Paste Your Resume Here", height=200)

# Divider between resume and job description
st.divider()

# Text box for job description — always required
job_description = st.text_area("💼 Paste the Job Description Here", height=200)

# Divider before the button
st.divider()

# ── SUBMIT BUTTON ─────────────────────────────────────────────────────────────

if st.button("🔍 Analyze Resume", use_container_width=True):

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

    # Check each field separately and show specific warnings
    if not resume_text and not job_description:
        # Both fields are empty
        st.warning("Please fill in both the resume and job description before analyzing.")
    elif not resume_text:
        # Resume is missing
        st.warning("Please provide a resume — upload a PDF or paste your resume text.")
    elif not job_description:
        # Job description is missing
        st.warning("Please paste a job description before analyzing.")

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

                        st.divider()
                        st.subheader("📊 Analysis Results")

                        # Get the match score
                        score = result['match_score']

                        # Show progress bar
                        # st.progress() takes a value between 0.0 and 1.0
                        # so we divide score by 100
                        st.progress(score / 100)

                        # Color-coded score label based on range
                        if score >= 80:
                            # Green — strong match
                            st.success(f"✅ Strong Match — {score} / 100")
                        elif score >= 60:
                            # Blue — good match
                            st.info(f"👍 Good Match — {score} / 100")
                        elif score >= 40:
                            # Yellow — needs work
                            st.warning(f"⚠️ Needs Work — {score} / 100")
                        else:
                            # Red — poor match
                            st.error(f"❌ Poor Match — {score} / 100")

                        st.divider()

                        # Missing keywords section
                        st.markdown("### 🔍 Missing Keywords")
                        st.markdown("These keywords appear in the job description but not in your resume:")

                        # Display each missing keyword as a styled bullet
                        keywords = result['missing_keywords']
                        if keywords:
                            for keyword in keywords:
                                st.markdown(f"- `{keyword}`")
                        else:
                            st.success("✅ No missing keywords — great match!")

                        st.divider()

                        # Suggestion section
                        st.markdown("### 💡 Suggestion")
                        st.info(result['suggestion'])

                        st.divider()

                        # Footer message
                        st.caption("Analysis powered by Claude AI · Built by Madhunika Danam")

            except requests.exceptions.ConnectionError:
                # FastAPI is not running
                st.error("❌ Cannot connect to the backend. Make sure FastAPI is running.")

            except requests.exceptions.Timeout:
                # FastAPI took too long
                st.error("⏱️ The request timed out. Please try again.")

            except Exception as e:
                # Any other unexpected error
                st.error(f"Something unexpected happened: {str(e)}")