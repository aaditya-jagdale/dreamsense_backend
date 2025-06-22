# FastAPI
from fastapi import FastAPI
import uvicorn
from routes import routes

app = FastAPI()

app.include_router(routes.router)

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)