import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field

import config
from daily_values import calculate_daily_value, get_daily_reference
from insights import generate_insights
from ocr import extract_text_from_image
from parser import (
    extract_ingredients,
    extract_product_name,
    extract_serving_size,
    extract_servings_per_container,
    parse_nutrition_text,
)

app = FastAPI(title="NutriScan API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

mongo_client = AsyncIOMotorClient(config.MONGODB_URI) if config.MONGODB_URI else None
db = mongo_client[config.MONGODB_DB] if mongo_client else None


# ---------- Request models (validated automatically by FastAPI) ----------

class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    nutritionData: dict


# ---------- Helpers ----------

def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def ensure_db():
    if db is None:
        raise HTTPException(status_code=503, detail="Database is not configured")


def create_access_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": now_utc() + timedelta(minutes=config.JWT_EXPIRES_MINUTES)}
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


def to_object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    ensure_db()
    try:
        payload = jwt.decode(credentials.credentials, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        user_id = payload["sub"]
    except (jwt.PyJWTError, KeyError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired. Please log in again.")

    user = await db.users.find_one({"_id": to_object_id(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def serialize_user(user):
    return {"id": str(user["_id"]), "name": user.get("name"), "email": user.get("email")}


def serialize_doc(doc, include_data: bool = False):
    created = doc.get("createdAt")
    data = doc.get("nutritionData") or {}
    result = {
        "id": str(doc["_id"]),
        "title": doc.get("title"),
        "createdAt": created.isoformat() if isinstance(created, datetime) else created,
        # Small summary so the history list can show it without loading the full scan
        "calories": (data.get("macronutrients", {}).get("calories") or {}).get("amount"),
        "healthScore": (data.get("insights") or {}).get("healthScore"),
    }
    if include_data:
        result["nutritionData"] = data
    return result


def doc_id_or_404(doc_id: str) -> ObjectId:
    try:
        return ObjectId(doc_id)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Scan not found")


# Simple per-user rate limit so a public demo can't burn through the Gemini quota.
_analyze_hits: dict[str, deque] = defaultdict(deque)


def check_rate_limit(user_id: str):
    hits = _analyze_hits[user_id]
    cutoff = time.time() - 3600
    while hits and hits[0] < cutoff:
        hits.popleft()
    if len(hits) >= config.ANALYZE_RATE_LIMIT_PER_HOUR:
        raise HTTPException(status_code=429, detail="You've hit the hourly scan limit. Try again later.")
    hits.append(time.time())


def nutrient(key: str, amount, unit: str) -> dict:
    return {
        "amount": amount,
        "unit": unit,
        "dailyReference": get_daily_reference(key),
        "percentDailyValue": calculate_daily_value(key, amount),
    }


MACROS = {
    "calories": "kcal", "totalFat": "g", "saturatedFat": "g", "transFat": "g",
    "cholesterol": "mg", "sodium": "mg", "totalCarbohydrate": "g", "dietaryFiber": "g",
    "totalSugars": "g", "addedSugars": "g", "protein": "g",
}
MICROS = {"vitaminD": "mcg", "calcium": "mg", "iron": "mg", "potassium": "mg"}


# ---------- Routes ----------

@app.get("/")
def root():
    return {"message": "NutriScan backend is working"}


@app.post("/api/auth/signup", status_code=201)
async def signup(payload: SignupRequest):
    ensure_db()
    email = payload.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="An account with that email already exists")

    user = {
        "name": payload.name.strip(),
        "email": email,
        "passwordHash": hash_password(payload.password),
        "createdAt": now_utc(),
    }
    result = await db.users.insert_one(user)
    user["_id"] = result.inserted_id
    return {"accessToken": create_access_token(str(result.inserted_id)), "user": serialize_user(user)}


@app.post("/api/auth/login")
async def login(payload: LoginRequest):
    ensure_db()
    user = await db.users.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user["passwordHash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"accessToken": create_access_token(str(user["_id"])), "user": serialize_user(user)}


@app.get("/api/auth/me")
async def me(current_user=Depends(get_current_user)):
    return serialize_user(current_user)


@app.post("/api/analyze")
async def analyze_label(
    image: UploadFile = File(...),
    foodName: str = Form("", max_length=120),
    current_user=Depends(get_current_user),
):
    check_rate_limit(str(current_user["_id"]))

    if image.content_type and not image.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Please upload an image file (JPG, PNG or WEBP).")

    max_bytes = int(config.MAX_UPLOAD_MB * 1024 * 1024)
    image_bytes = await image.read(max_bytes + 1)
    if len(image_bytes) > max_bytes:
        raise HTTPException(status_code=413, detail=f"Image is larger than {config.MAX_UPLOAD_MB:g}MB.")
    if not image_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        # OCR is slow and blocking, so run it off the event loop.
        ocr_text = await run_in_threadpool(extract_text_from_image, image_bytes)
    except Exception as error:
        raise HTTPException(status_code=422, detail=f"Couldn't read the label: {error}")

    parsed = parse_nutrition_text(ocr_text)

    nutrition_response = {
        "productName": foodName.strip() or extract_product_name(ocr_text) or "Unknown Food",
        "ocrText": ocr_text,
        "servingSize": extract_serving_size(ocr_text) or "1 serving",
        "servingsPerContainer": extract_servings_per_container(ocr_text) or 1,
        "macronutrients": {key: nutrient(key, parsed[key], unit) for key, unit in MACROS.items()},
        "micronutrients": {key: nutrient(key, parsed[key], unit) for key, unit in MICROS.items()},
        "ingredients": extract_ingredients(ocr_text),
    }

    nutrition_response["insights"] = await run_in_threadpool(generate_insights, nutrition_response, ocr_text)
    return nutrition_response


@app.get("/api/docs")
async def list_docs(current_user=Depends(get_current_user)):
    cursor = db.documents.find({"userId": current_user["_id"]}).sort("createdAt", -1)
    return [serialize_doc(doc) for doc in await cursor.to_list(length=100)]


@app.post("/api/docs", status_code=201)
async def create_doc(payload: DocumentCreate, current_user=Depends(get_current_user)):
    doc = {
        "userId": current_user["_id"],
        "title": payload.title.strip(),
        "nutritionData": payload.nutritionData,
        "createdAt": now_utc(),
    }
    result = await db.documents.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


@app.get("/api/docs/{doc_id}")
async def get_doc(doc_id: str, current_user=Depends(get_current_user)):
    # Filtering by userId too means users can only open their own scans
    doc = await db.documents.find_one({"_id": doc_id_or_404(doc_id), "userId": current_user["_id"]})
    if not doc:
        raise HTTPException(status_code=404, detail="Scan not found")
    return serialize_doc(doc, include_data=True)


@app.delete("/api/docs/{doc_id}")
async def delete_doc(doc_id: str, current_user=Depends(get_current_user)):
    result = await db.documents.delete_one({"_id": doc_id_or_404(doc_id), "userId": current_user["_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Scan not found")
    return {"deleted": True}
