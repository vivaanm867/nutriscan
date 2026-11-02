"""All settings in one place, read from environment variables (or backend/.env)."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

ENV = os.getenv("ENV", "development").lower()
IS_PROD = ENV == "production"

# --- Database ---
MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB = os.getenv("MONGODB_DB", "nutriscan")

# --- Auth ---
JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", str(60 * 24)))

if not JWT_SECRET:
    if IS_PROD:
        raise RuntimeError("JWT_SECRET must be set in production.")
    JWT_SECRET = "dev-only-insecure-secret-change-me-in-prod"

# --- AI ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# --- Limits ---
MAX_UPLOAD_MB = float(os.getenv("MAX_UPLOAD_MB", "8"))
ANALYZE_RATE_LIMIT_PER_HOUR = int(os.getenv("ANALYZE_RATE_LIMIT_PER_HOUR", "30"))

# --- Web ---
# Comma-separated list of frontend URLs allowed to call the API.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:3001,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]