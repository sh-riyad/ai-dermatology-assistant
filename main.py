from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from app.auth.auth import AuthRouter, get_current_user
from app.core.database import init_db
from app.api.v1.user import UsersRouter
from app.api.v1.chat import ChatRouter
from app.api.v1.disease_report import DiseaseReportRouter
from app.api.v1.disease_classification import ClassificationRouter
from app.api.v1.doctor_search import DoctorSearchRouter
import logging
from starlette.middleware.cors import CORSMiddleware
from app.middleware.middleware import LoggingMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get PORT from environment variable with default fallback
PORT = int(os.getenv('PORT', 8000))

init_db()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
        title="AI Dermatology Assistant API",
        description="",
        version="1.0.0"
    )

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

app.include_router(AuthRouter,prefix="/auth", tags=["Authentication"])
app.include_router(ChatRouter, tags=["Chat"])
app.include_router(UsersRouter, prefix="/user", tags=["Users"])
app.include_router(DiseaseReportRouter, prefix="/chat", tags=["Disease Report Generate"])
app.include_router(ClassificationRouter, prefix="/chat", tags=["Disease Classification"])
app.include_router(DoctorSearchRouter, prefix="/chat", tags=["Search Doctor"])

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")