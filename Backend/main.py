from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate_text(prompt_request: PromptRequest):
    prompt = prompt_request.prompt
    
    try:
        # Log the prompt being processed
        logging.info(f"Received prompt: {prompt}")
        
        # Call the Ollama CLI with the correct model name and 'run' command
        process = subprocess.run(
            ["ollama", "run", "llama3.1:8b", prompt],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Log the output from the process
        response = process.stdout
        logging.info(f"Ollama Response: {response}")
        
        return {"response": response.strip()}
    
    except subprocess.CalledProcessError as e:
        # Log the error details
        logging.error(f"Command failed: {e.stderr}")
        raise HTTPException(status_code=500, detail="Model generation failed")
    
    except Exception as e:
        # Catch any other exceptions and log them
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")