import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import torch
import scipy.io.wavfile as wavfile
from transformers import AutoProcessor, BarkModel
import os
import uuid

app = FastAPI()

# --- Model Loading ---
processor = AutoProcessor.from_pretrained("suno/bark-small")
model = BarkModel.from_pretrained("suno/bark-small")
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# --- Directory Setup ---
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

# --- Pydantic Model for Request Body ---
class TextToSpeechRequest(BaseModel):
    text: str
    voice_preset: str | None = None

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
        inputs = processor(
            text=[request.text],
            return_tensors="pt",
            voice_preset=request.voice_preset
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            speech_output = model.generate(**inputs, do_sample=True)

        sampling_rate = model.generation_config.sample_rate
        speech_waveform = speech_output[0].cpu().numpy().squeeze()

        unique_id = uuid.uuid4()
        file_path = os.path.join(TEMP_DIR, f"{unique_id}.wav")

        wavfile.write(file_path, rate=sampling_rate, data=speech_waveform)

        return FileResponse(path=file_path, media_type="audio/wav", filename=f"speech_{unique_id}.wav")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate speech.")

app.mount("/", StaticFiles(directory="ui", html=True), name="ui")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

