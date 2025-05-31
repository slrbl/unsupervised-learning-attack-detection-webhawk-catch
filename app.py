# app.py

from fastapi import FastAPI
from pydantic import BaseModel
from catch_api import main

app = FastAPI()

# Define input model
class NameInput(BaseModel):
    placeholder: str
    logs_content: str

# Health check endpoint
@app.get("/")
def root():
    return {"message": "FastAPI service is running"}

# POST endpoint to log analysis
@app.post("/scan")
def scan(input: NameInput):
    result = main(input.placeholder,input.logs_content)
    return {"result": result}

