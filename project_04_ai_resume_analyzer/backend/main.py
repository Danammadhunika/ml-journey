# Import the FastAPI class from the fastapi package (toolbox)
from fastapi import FastAPI

# Import datetime so we can check the current date/time later
from datetime import datetime

# Import BaseModel from Pydantic for data validation
from pydantic import BaseModel

# Build the actual app (the "empty house") using the FastAPI blueprint
app = FastAPI()

# Define the shape of data we expect to receive
class ResumeRequest(BaseModel):
    resume_text: str
    job_description: str

# Decorator: register this route for GET requests at the address "/"
@app.get("/")
# Define the function that answers when someone visits "/"
def say_hi():
    # Send back a dictionary, which FastAPI turns into JSON
    return {"message": "hi"}

# Decorator: register a route for GET requests at "/hello/{name}"
# {name} is a placeholder — FastAPI will capture whatever text is there
@app.get("/hello/{name}")          # Door 2: address is /hello/ + whatever name is typed
def greet(name: str):              # ONLY parameter here: the name from the URL
    now = datetime.now()           # get current date and time
    hour = now.hour                # pull out just the hour (0-23)

    # check which time range we're in, and set the right greeting word
    if hour < 12:
        greeting = "Good Morning"
    elif hour < 17:
        greeting = "Good Afternoon"
    elif hour < 21:
        greeting = "Good Evening"
    else:
        greeting = "Good Night"

    # combine greeting + name into one final message and send it back
    return {"message": f"{greeting}, {name}"}

@app.post("/analyze")
def analyze_resume(request: ResumeRequest):
          return {
         "resume_text": request.resume_text,
          "job_description": request.job_description
           }