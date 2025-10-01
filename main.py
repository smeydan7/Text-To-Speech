import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import torch
import soundfile as sf
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import os
import uuid
import numpy as np

app = FastAPI()

# --- Model and Processor Loading  ---
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")

vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
vocoder.to(device)

np.random.seed(42)  # Set seed for consistency
default_embedding = np.random.randn(512).astype(np.float32)
speaker_embeddings = torch.tensor(default_embedding).unsqueeze(0).to(device)


# --- Directory Setup ---
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)

# --- Pydantic Model for Request Body ---
class TextToSpeechRequest(BaseModel):
    text: str
    voice_preset: str | None = None

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    return {"status": "ok", "model": "microsoft/speecht5_tts"}

# --- Synthesis Endpoint (Updated for SpeechT5) ---
@app.post("/synthesize")
async def synthesize_speech(request: TextToSpeechRequest):
    """
    Accepts text, generates speech using SpeechT5, and returns the audio.
    """
    if not request.text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    try:
        inputs = processor(text=request.text, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        speech = model.generate_speech(
            inputs["input_ids"],
            speaker_embeddings=speaker_embeddings,
            vocoder=vocoder
        )

        speech_waveform = speech.cpu().numpy()
        sampling_rate = 16000 # SpeechT5 operates at 16kHz

        unique_id = uuid.uuid4()
        file_path = os.path.join(TEMP_DIR, f"{unique_id}.wav")

        sf.write(file_path, speech_waveform, samplerate=sampling_rate)

        return FileResponse(path=file_path, media_type="audio/wav", filename=f"speech_{unique_id}.wav")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate speech.")

app.mount("/", StaticFiles(directory="ui", html=True), name="ui")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

