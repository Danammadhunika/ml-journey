# ── IMPORTS ──────────────────────────────────────────────────────────────────

# Bring in the FastAPI tool from the fastapi package
# Without this, Python doesn't know what FastAPI means
from fastapi import FastAPI

# Bring in datetime so we can check the current hour later
from datetime import datetime

# Bring in BaseModel from Pydantic
# BaseModel gives our data class automatic validation superpowers
from pydantic import BaseModel

# Bring in os — a built-in Python tool for reading system/environment variables
# We need this to safely read our API key from the .env file
import os

# Bring in json — lets us convert Claude's text response into a Python dictionary
import json

# Bring in the anthropic package — this is what lets our app talk to Claude
# We installed this with: pip install anthropic
import anthropic

# Bring in load_dotenv from the python-dotenv package
# This reads our .env file and makes the values inside it available to our code
# We installed this with: pip install python-dotenv
from dotenv import load_dotenv


# ── SETUP ─────────────────────────────────────────────────────────────────────

# Actually run load_dotenv() — this opens the .env file and loads the values
# Must be called before os.getenv() otherwise the key won't be found
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Read the value of ANTHROPIC_API_KEY from the .env file
# os.getenv("name") looks for a variable with that exact name
# The name must match exactly what's written in your .env file
api_key = os.getenv("ANTHROPIC_API_KEY")

# Create a Claude client using the API key we just loaded
# Think of this as picking up the phone and dialing Claude's number
# From now on, whenever we want to talk to Claude, we use this "client" variable
client = anthropic.Anthropic(api_key=api_key)

# Build the actual FastAPI app — the empty house
# All our routes (doors) will be attached to this "app" variable
app = FastAPI()


# ── DATA MODEL ────────────────────────────────────────────────────────────────

# Define the shape of data we expect to receive at our POST route
# Think of this as a form template with two required fields
# Anyone sending data to /analyze must include both of these fields
# If a field is missing or wrong type, Pydantic automatically rejects it
class ResumeRequest(BaseModel):
    resume_text: str        # the person's resume — must be text
    job_description: str    # the job they're applying for — must be text


# ── ROUTES (DOORS) ────────────────────────────────────────────────────────────

# Door 1: GET /
# Decorator: register this function as the handler for GET requests at "/"
# This is just a health check — confirms the app is alive and running
@app.get("/")
def say_hi():
    # Return a simple dictionary — FastAPI auto-converts this to JSON
    return {"message": "hi"}


# Door 2: GET /hello/{name}
# {name} is a path parameter — a variable slot in the URL
# Whatever text is typed after /hello/ gets captured as "name"
@app.get("/hello/{name}")
def greet(name: str):           # name comes from the URL, must be text
    now = datetime.now()        # get the current date and time right now
    hour = now.hour             # pull out just the hour as a number (0-23)

    # Check which time range we're in and set the greeting word accordingly
    # elif only runs if everything above it was False — so ranges narrow automatically
    if hour < 12:
        greeting = "Good Morning"
    elif hour < 17:               # at this point we already know hour >= 12
        greeting = "Good Afternoon"
    elif hour < 21:               # at this point we already know hour >= 17
        greeting = "Good Evening"
    else:                         # anything 21 or later
        greeting = "Good Night"

    # Combine greeting + name using an f-string
    # f"..." means: fill in {variable} placeholders with their actual values
    return {"message": f"{greeting}, {name}"}


# Door 3: POST /analyze
# POST because the user is SENDING data to us (resume + job description)
# Not just visiting — they're dropping something off for us to process
@app.post("/analyze")
def analyze_resume(request: ResumeRequest):
    # "request" holds the incoming data — shaped exactly like ResumeRequest
    # request.resume_text = the resume the user sent
    # request.job_description = the job description the user sent

    # Send a message to Claude using our client
    # This is like texting Claude: "hey, compare these two things for me"
    message = client.messages.create(
        model="claude-sonnet-4-6",  # which Claude model to use (Sonnet = best balance)
        max_tokens=2048,            # increased from 1024 — handles longer resumes
        messages=[
            {
                "role": "user",     # "user" means this message is coming from us
                "content": f"""
You are a resume expert. Compare the resume to the job description below.

Respond ONLY with a JSON object. No extra text, no markdown, no code fences, no backticks, no explanation outside the JSON.

Return exactly this structure:
{{
  "match_score": <number between 0 and 100>,
  "missing_keywords": ["keyword1", "keyword2", "keyword3"],
  "suggestion": "<one clear sentence suggestion>"
}}

Resume:
{request.resume_text}

Job Description:
{request.job_description}
"""
                # f-string: fills in actual resume and job description text
                # This is called a PROMPT — the instruction we give to Claude
                # Double curly braces {{ }} = literal { } characters in f-strings
                # Single {variable} = fill in the variable's value
            }
        ]
    )

    # Get the raw text response from Claude
    raw = message.content[0].text

    # Strip any accidental whitespace from the beginning and end
    raw = raw.strip()

    # Remove markdown code fences if Claude added them anyway
    # Sometimes Claude wraps JSON in ```json ... ``` despite instructions
    if raw.startswith("```"):
        raw = raw.split("```")[1]  # get content between first pair of backticks
        if raw.startswith("json"):
            raw = raw[4:]          # remove the word "json" after the backticks
        raw = raw.strip()          # clean up any remaining whitespace

    # If Claude returned an empty response, return a friendly error
    if not raw:
        return {"error": "Claude returned an empty response. Please try again."}

    # Try to parse Claude's JSON text into a real Python dictionary
    # json.loads() = "load string" — converts JSON text to Python dictionary
    try:
        parsed = json.loads(raw)
        return parsed  # return the clean structured data
    except json.JSONDecodeError:
        # If JSON parsing fails, return the raw text so we can debug
        return {"error": f"Could not parse response: {raw[:200]}"}