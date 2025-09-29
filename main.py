import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import torch
import scipy.io.wavfile as wavfile
from transformers import AutoProcessor, BarkModel
import os
import uuid

# Initialize FastAPI app
app = FastAPI()

# --- Model Loading ---
# Load the processor and model from Hugging Face.
# This will download the model on the first run and cache it.
# We'll use Suno's Bark model, which is great for realistic speech.
processor = AutoProcessor.from_pretrained("suno/bark-small")
model = BarkModel.from_pretrained("suno/bark-small")

# Move model to GPU if available for faster inference
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Define a temporary directory to store the audio files
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

# --- Pydantic Model for Request Body ---
# This defines the expected structure of the JSON payload for our endpoint.
class TextToSpeechRequest(BaseModel):
    text: str
    voice_preset: str | None = None # Optional voice preset

# --- Root Endpoint to Serve the Frontend ---
@app.get("/")
async def read_index():
    """Serves the frontend HTML file."""
    return FileResponse('ui/index.html')

# --- Synthesis Endpoint ---
@app.post("/synthesize")
async def synthesize_speech(request: TextToSpeechRequest):
    """
    Accepts text and a voice preset, generates speech, saves it as a temporary
    WAV file, and returns the audio file as a response.
    """
    if not request.text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    try:
        # Prepare the input text for the model
        inputs = processor(
            text=[request.text],
            return_tensors="pt",
            voice_preset=request.voice_preset
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generate the audio waveform
        # The model generates audio at its own sampling rate.
        with torch.no_grad():
            speech_output = model.generate(**inputs, do_sample=True)

        sampling_rate = model.generation_config.sample_rate
        speech_waveform = speech_output[0].cpu().numpy().squeeze()

        # Generate a unique filename to avoid conflicts
        unique_id = uuid.uuid4()
        file_path = os.path.join(TEMP_DIR, f"{unique_id}.wav")

        # Save the audio to a WAV file
        wavfile.write(file_path, rate=sampling_rate, data=speech_waveform)

        # Return the audio file to the user
        return FileResponse(path=file_path, media_type="audio/wav", filename=f"speech_{unique_id}.wav")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate speech.")


# --- To run the app, use the command: uvicorn main:app --reload ---
# Example of how to run this file from your terminal:
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
