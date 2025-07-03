# FastAPI
from fastapi import FastAPI
from routes import routes
from routes import transcribe
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.include_router(routes.router)
app.include_router(transcribe.router)