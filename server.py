from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import torch
import logging
import asyncio
import time
import os
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("code_analysis.log")
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS Configuration
# CORS Configuration
origins = [
    "https://www.ravzzy.com",  # Your production frontend
    "http://localhost:8001",   # Your local development frontend
    # Add any other domains that need access
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global progress tracker
class GenerationProgress:
    def __init__(self):
        self.current = 0
        self.total = 0
        self.generated_text = ""
        self.is_complete = False
        self.start_time = None
        self.last_update = None
        self.tokens_per_second = 0
        
    def start_timer(self):
        self.start_time = time.time()
        self.last_update = self.start_time
        
    def update_progress(self, current, text):
        now = time.time()
        if self.last_update:
            elapsed = now - self.last_update
            if elapsed > 0:
                self.tokens_per_second = (current - self.current) / elapsed
        self.current = current
        self.generated_text = text
        self.last_update = now
        
        logger.info(
            f"Progress: {self.get_percent()}% | "
            f"Tokens: {current}/{self.total} | "
            f"Speed: {self.tokens_per_second:.2f} tokens/sec | "
            f"ETA: {self.get_eta()}"
        )
    
    def get_percent(self):
        return min(100, int((self.current / self.total) * 100)) if self.total > 0 else 0
        
    def get_eta(self):
        if self.tokens_per_second > 0 and not self.is_complete:
            remaining = max(0, (self.total - self.current) / self.tokens_per_second)
            return str(timedelta(seconds=int(remaining)))
        return "Calculating..."

progress = GenerationProgress()

# Model and tokenizer
model = None
tokenizer = None

class CodeAnalysisRequest(BaseModel):
    language: str
    max_length: int
    code: str

class CustomStreamer(TextStreamer):
    def __init__(self, tokenizer, progress):
        super().__init__(tokenizer)
        self.progress = progress
        self.token_count = 0
        
    def on_finalized_text(self, text: str, stream_end: bool = False):
        self.token_count += 1
        self.progress.update_progress(self.token_count, text)
        return super().on_finalized_text(text, stream_end)

@app.on_event("startup")
async def startup_event():
    global model, tokenizer
    try:
        model_path = "/Users/ravz/Downloads/MS-phi-2-Models"
        logger.info(f"Loading model from {model_path}")
        
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            trust_remote_code=True,
            device_map="auto",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        logger.info(f"Model loaded on {model.device}")
        
    except Exception as e:
        logger.error(f"Model loading failed: {str(e)}")
        raise RuntimeError(f"Model loading failed: {str(e)}")

@app.post("/analyze")
async def analyze_code(request: CodeAnalysisRequest):
    try:
        if not model or not tokenizer:
            raise HTTPException(status_code=500, detail="Model not loaded")
        
        # Reset progress tracker
        progress.current = 0
        progress.total = min(request.max_length, 500)
        progress.generated_text = ""
        progress.is_complete = False
        progress.start_timer()
        
        logger.info(f"Starting analysis for {request.language} code (max tokens: {progress.total})")
        
        prompt = f"Find all the errors in {request.language} code:\n\n{request.code}\n\nShare me detailed explanation and things I can improve upon:"
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(model.device)
        
        streamer = CustomStreamer(tokenizer, progress)
        
        outputs = model.generate(
            **inputs,
            max_new_tokens=progress.total,
            temperature=0.7,
            do_sample=True,
            streamer=streamer
        )
        
        progress.is_complete = True
        analysis = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        logger.info(f"Analysis completed in {time.time() - progress.start_time:.2f} seconds")
        return {"analysis": analysis.replace(prompt, "").strip()}
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/progress")
async def get_progress():
    return {
        "current": progress.current,
        "total": progress.total,
        "percent": progress.get_percent(),
        "speed": f"{progress.tokens_per_second:.2f} tokens/sec",
        "eta": progress.get_eta(),
        "is_complete": progress.is_complete,
        "generated_preview": progress.generated_text[-200:]
    }

@app.websocket("/ws/progress")
async def websocket_progress(websocket: WebSocket):
    await websocket.accept()
    try:
        while not progress.is_complete:
            await asyncio.sleep(0.5)
            await websocket.send_json({
                "current": progress.current,
                "total": progress.total,
                "percent": progress.get_percent(),
                "speed": f"{progress.tokens_per_second:.2f} tokens/sec",
                "eta": progress.get_eta(),
                "is_complete": progress.is_complete,
                "preview": progress.generated_text[-100:]
            })
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()

@app.get("/gpu-info")
async def get_gpu_info():
    return {
        "cuda_available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "current_device": torch.cuda.current_device() if torch.cuda.is_available() else None,
        "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    }

@app.get("/logs")
async def get_logs():
    return FileResponse(
        "code_analysis.log",
        media_type="text/plain",
        filename="analysis_progress.log"
    )

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "model_loaded": bool(model),
        "device": str(model.device) if model else "none",
        "cuda_available": torch.cuda.is_available()
    }