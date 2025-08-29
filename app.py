from fastapi import FastAPI, Form, Response, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import numpy as np, soundfile as sf, io, os

# Lazy import to avoid heavy init until first call
pipe = None
def get_pipe():
    global pipe
    if pipe is None:
        from kokoro import KPipeline
        try:
            import torch
            torch.set_num_threads(1)   # keep memory/CPU lower on free tier
        except Exception:
            pass
        pipe = KPipeline(lang_code="a")  # American English
    return pipe

app = FastAPI(title="Kokoro TTS (HF Space)")

# CORS so your Node.js can call this Space from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or lock to your domain
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

KOKORO_SECRET = os.getenv("KOKORO_SECRET", "")

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
        return JSONResponse({"error":"unauthorized"}, status_code=401)

    p = get_pipe()
    chunks = [audio for _,_,audio in p(text, voice=voice, speed=speed, split_pattern=r"[.!?\n]+")]
    if not chunks:
        return JSONResponse({"error":"empty-audio"}, status_code=422)

    audio = np.concatenate(chunks).astype(np.float32)
    buf = io.BytesIO()
    # 16-bit PCM WAV for max browser compatibility
    sf.write(buf, audio, 24000, format="WAV", subtype="PCM_16")
    return Response(content=buf.getvalue(), media_type="audio/wav")
