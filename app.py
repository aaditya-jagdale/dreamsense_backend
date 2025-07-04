# FastAPI
from fastapi import FastAPI
from routes import routes
from routes import transcribe
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(
    title="DreamSense API",
    description="AI-powered dream analysis and interpretation API",
    version="1.0.0"
)

app.include_router(routes.router, prefix="/api/v1", tags=["main"])
app.include_router(transcribe.router, prefix="/api/v1", tags=["audio"])