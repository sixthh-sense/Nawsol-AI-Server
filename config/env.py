import os
from dotenv import load_dotenv

load_dotenv()

KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")
KAKAO_SECRET_KEY = os.getenv("KAKAO_SECRET_KEY")

if not KAKAO_CLIENT_ID:
    raise RuntimeError("KAKAO_CLIENT_ID is not set")
if not KAKAO_REDIRECT_URI:
    raise RuntimeError("KAKAO_REDIRECT_URI is not set")
if not KAKAO_SECRET_KEY:
    raise RuntimeError("KAKAO_SECRET_KEY is not set")