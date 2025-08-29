from fastapi import FastAPI, Form, Response, Header
from fastapi.responses import JSONResponse
from typing import Optional
from kokoro import KPipeline
import numpy as np, soundfile as sf, io, os

app = FastAPI(title="Kokoro TTS")

# change "a"→ American English, "b"→ British, etc.
pipe = KPipeline(lang_code="a")

# optional shared-secret to prevent public abuse
KOKORO_SECRET = os.getenv("KOKORO_SECRET", "")

def synth(text: str, voice: str, speed: float) -> bytes:
    chunks = [audio for _, _, audio in pipe(text, voice=voice, speed=speed, split_pattern=r"[\n\.!?]+")]
    if not chunks:
        return b""
    audio = np.concatenate(chunks).astype(np.float32)
    buf = io.BytesIO()
    # 16-bit PCM for max browser compatibility
    sf.write(buf, audio, 24000, format="WAV", subtype="PCM_16")
    return buf.getvalue()

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/tts")
def tts(
    text: str = Form(...),
    voice: str = Form("af_heart"),
    speed: float = Form(1.0),
    x_kokoro_auth: Optional[str] = Header(None)
):
    if KOKORO_SECRET and x_kokoro_auth != KOKORO_SECRET:
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    data = synth(text, voice, speed)
    if not data:
        return JSONResponse({"error": "empty-audio"}, status_code=422)
    return Response(content=data, media_type="audio/wav")
