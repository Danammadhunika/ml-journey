# ── IMPORTS ──────────────────────────────────────────────────────────────────

# Streamlit — builds the web interface (input boxes, buttons, display)
import streamlit as st

# requests — sends HTTP requests from Streamlit to FastAPI
# This is the "waiter" that carries data between Streamlit and FastAPI
import requests

# ── PAGE SETUP ────────────────────────────────────────────────────────────────

# Set the browser tab title and page layout
st.set_page_config(page_title="AI Resume Analyzer", layout="centered")

# Main title shown at the top of the page
st.title("🤖 AI-Powered Resume Analyzer")

# Subtitle description
st.markdown("Paste your resume and job description below to get an AI match score, missing keywords, and improvement suggestions.")

# ── INPUT SECTION ─────────────────────────────────────────────────────────────

# Text area for the resume — st.text_area creates a large input box
# "label" is what shows above the box, "height" controls how tall it is
resume_text = st.text_area("📄 Paste Your Resume Here", height=200)

# Text area for the job description
job_description = st.text_area("💼 Paste the Job Description Here", height=200)

# ── SUBMIT BUTTON ─────────────────────────────────────────────────────────────

# st.button creates a clickable button
# Everything inside the if block only runs when the button is clicked
if st.button("🔍 Analyze Resume"):

    # Check that both boxes have text before sending to FastAPI
    # If either is empty, show a warning instead of sending a blank request
    if not resume_text or not job_description:
        st.warning("Please fill in both the resume and job description before analyzing.")

    else:
        # Show a spinner while waiting for Claude's response
        with st.spinner("Analyzing your resume with AI..."):

            # Send a POST request to your FastAPI backend
            # This is exactly like clicking Execute in Swagger docs
            # but done automatically by Python code
            response = requests.post(
                "http://127.0.0.1:8000/analyze",  # your FastAPI route
                json={                              # data sent as JSON
                    "resume_text": resume_text,
                    "job_description": job_description
                }
            )

            # Parse the JSON response from FastAPI into a Python dictionary
            result = response.json()

        # ── DISPLAY RESULTS ───────────────────────────────────────────────

        # Section header
        st.subheader("📊 Analysis Results")

        # Display match score as a big metric
        # st.metric shows a large labeled number
        st.metric(label="Match Score", value=f"{result['match_score']} / 100")

        # Display missing keywords as a list
        st.markdown("### 🔍 Missing Keywords")
        for keyword in result['missing_keywords']:
            # st.markdown with a bullet point for each keyword
            st.markdown(f"- {keyword}")

        # Display the suggestion in a highlighted info box
        st.markdown("### 💡 Suggestion")
        st.info(result['suggestion'])