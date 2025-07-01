# FastAPI
from fastapi import FastAPI
from routes import routes
import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

app = FastAPI()

app.include_router(routes.router)