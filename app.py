from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from config.routes.system import router

app = FastAPI(
    title="API QDRANT",
    description="API QDRANT",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENV") != "production" else None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
