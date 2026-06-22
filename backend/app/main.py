import os
from utils.helpers import UPLOAD_DIR
from fastapi import FastAPI, File, UploadFile


app = FastAPI()

# UPLOAD_DIR = 'static/images'
os.makedirs(UPLOAD_DIR, exist_ok=True)