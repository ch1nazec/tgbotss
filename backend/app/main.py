import os
from sqlalchemy.orm import configure_mappers
from utils.helpers import UPLOAD_DIR
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from routers import all_routers


configure_mappers()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# UPLOAD_DIR = 'static/images'
os.makedirs(UPLOAD_DIR, exist_ok=True)

for router in all_routers:
    app.include_router(router)