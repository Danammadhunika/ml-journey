# ── IMPORTS ──────────────────────────────────────────────────────────────────

# Streamlit — builds the web interface
import streamlit as st

# requests — sends HTTP requests from Streamlit to FastAPI
import requests

# ── PAGE SETUP ────────────────────────────────────────────────────────────────

# Set browser tab title and layout
st.set_page_config(page_title="AI Resume Analyzer", layout="centered")

# Main title
st.title("🤖 AI-Powered Resume Analyzer")

# Subtitle
st.markdown("Paste your resume and job description below to get an AI match score, missing keywords, and improvement suggestions.")

# ── INPUT SECTION ─────────────────────────────────────────────────────────────

# Text box for resume
resume_text = st.text_area("📄 Paste Your Resume Here", height=200)

# Text box for job description
job_description = st.text_area("💼 Paste the Job Description Here", height=200)

# ── SUBMIT BUTTON ─────────────────────────────────────────────────────────────

if st.button("🔍 Analyze Resume"):

    # Check both boxes have text before sending
    if not resume_text or not job_description:
        st.warning("Please fill in both the resume and job description before analyzing.")

    else:
        with st.spinner("Analyzing your resume with AI..."):
            try:
                # Try to send data to FastAPI backend
                response = requests.post(
                    "http://127.0.0.1:8000/analyze",  # FastAPI route
                    json={
                        "resume_text": resume_text,       # resume from text box
                        "job_description": job_description # job description from text box
                    },
                    timeout=30  # give up after 30 seconds if no response
                )

                # Check if FastAPI returned success (200) or an error
                if response.status_code != 200:
                    st.error("Something went wrong with the analysis. Please try again.")

                else:
                    # Convert JSON response into Python dictionary
                    result = response.json()

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