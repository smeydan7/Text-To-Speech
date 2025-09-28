from fastapi import FastAPI, Body
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, Field
from transformers import pipeline
import io
import soundfile as sf
import base64

app = FastAPI(title="Text to Speech", description="A simple text to speech API")

tts = pipeline(
    task="text-to-speech",
    model="ResembleAI/chatterbox"
)

class TextToSpeechRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

@app.post("/tts")
def endpoint(tts_request: TTSRequest):
    output = tts(tts_request.text)
    audio_array = output["audio"]["array"]
    sr = output["audio"]["sampling_rate"]

    with io.BytesIO() as audio_file:
        sf.write(buff, audio_array, sr, format="WAV")
        wav_bytes = buff.getvalue()

    return Response(
        content=wav_bytes,
        media_type="audio/wav"
        headers={"Content-Disposition": "inline; filename='speech.wav'"}
    )

