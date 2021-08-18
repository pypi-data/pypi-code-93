import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

DOWNLOAD_DIR = "downloads"
VIDEO_DIR = os.path.join(DOWNLOAD_DIR,"videos")
CAPTION_DIR = os.path.join(DOWNLOAD_DIR,"captions")
OUTPUT_DIR = 'output'





