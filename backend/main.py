from datetime import datetime, timedelta
import os

from bson import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

from insights import generate_insights
from ocr import extract_text_from_image
from parser import (
    parse_nutrition_text,
    extract_servings_per_container,
    extract_serving_size,
    extract_product_name
)
from daily_values import calculate_daily_value, get_daily_reference

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGODB_URI = os.getenv("MONGODB_URI")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_MINUTES = 60 * 24

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

mongo_client = AsyncIOMotorClient(MONGODB_URI) if MONGODB_URI else None
db = mongo_client["nutriscan"] if mongo_client else None


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class DocumentCreate(BaseModel):
    title: str
    fileSize: int | None = None
    thumbnailUrl: str | None = None
    nutritionData: dict | None = None


def ensure_db():
    if db is None:
        raise HTTPException(status_code=500, detail="Database is not configured")


def create_access_token(payload: dict):
    expires = datetime.utcnow() + timedelta(minutes=JWT_EXPIRES_MINUTES)
    to_encode = {**payload, "exp": expires}
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    ensure_db()
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def serialize_user(user):
    return {
        "id": str(user["_id"]),
        "name": user.get("name"),
        "email": user.get("email"),
    }


def serialize_doc(doc):
    return {
        "id": str(doc["_id"]),
        "title": doc.get("title"),
        "fileSize": doc.get("fileSize"),
        "thumbnailUrl": doc.get("thumbnailUrl"),
        "createdAt": doc.get("createdAt"),
    }

@app.get("/")
def root():
    return {
        "message": "NutriScan backend is working"
    }


@app.post("/api/auth/signup")
async def signup(payload: SignupRequest):
    ensure_db()
    existing = await db.users.find_one({"email": payload.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Account already exists")

    user_doc = {
        "name": payload.name,
        "email": payload.email.lower(),
        "passwordHash": hash_password(payload.password),
        "createdAt": datetime.utcnow().isoformat(),
    }
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    token = create_access_token({"sub": str(result.inserted_id)})
    return {"accessToken": token, "user": serialize_user(user_doc)}


@app.post("/api/auth/login")
async def login(payload: LoginRequest):
    ensure_db()
    user = await db.users.find_one({"email": payload.email.lower()})
    if not user or not verify_password(payload.password, user["passwordHash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token({"sub": str(user["_id"])})
    return {"accessToken": token, "user": serialize_user(user)}


@app.get("/api/auth/me")
async def me(current_user = Depends(get_current_user)):
    return serialize_user(current_user)

@app.post("/api/analyze")
async def analyze_label(
    image: UploadFile = File(...),
    foodName: str = Form("")
):
    try:
        image_bytes = await image.read()
        ocr_text = extract_text_from_image(image_bytes)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"OCR failed: {str(error)}"
        )

    try:
        parsed_data = parse_nutrition_text(ocr_text)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Parser failed: {str(error)}"
        )

    # Extract serving metadata from OCR text
    servings_per_container = extract_servings_per_container(ocr_text) or 1
    serving_size = extract_serving_size(ocr_text) or "1 serving"
    product_name = foodName or extract_product_name(ocr_text) or "Unknown Food"

    # Build the full nutrition response
    nutrition_response = {
      "productName": product_name,
      "ocrText": ocr_text,
      "brand": "Example Brand",
      "servingSize": serving_size,
      "servingsPerContainer": servings_per_container,

      "macronutrients": {
        "calories": {
          "amount": parsed_data["calories"],
          "unit": "kcal",
          "dailyReference": get_daily_reference("calories"),
          "percentDailyValue": calculate_daily_value("calories", parsed_data["calories"])
        },
        "totalFat": {
          "amount": parsed_data["totalFat"],
          "unit": "g",
          "dailyReference": get_daily_reference("totalFat"),
          "percentDailyValue": calculate_daily_value("totalFat", parsed_data["totalFat"])
        },
        "saturatedFat": {
          "amount": parsed_data["saturatedFat"],
          "unit": "g",
          "dailyReference": get_daily_reference("saturatedFat"),
          "percentDailyValue": calculate_daily_value("saturatedFat", parsed_data["saturatedFat"])
        },
        "transFat": {
          "amount": parsed_data["transFat"],
          "unit": "g",
          "percentDailyValue": calculate_daily_value("transFat", parsed_data["transFat"])
        },
        "cholesterol": {
          "amount": parsed_data["cholesterol"],
          "unit": "mg",
          "dailyReference": get_daily_reference("cholesterol"),
          "percentDailyValue": calculate_daily_value("cholesterol", parsed_data["cholesterol"])
        },
        "sodium": {
          "amount": parsed_data["sodium"],
          "unit": "mg",
          "dailyReference": get_daily_reference("sodium"),
          "percentDailyValue": calculate_daily_value("sodium", parsed_data["sodium"])
        },
        "totalCarbohydrate": {
          "amount": parsed_data["totalCarbohydrate"],
          "unit": "g",
          "dailyReference": get_daily_reference("totalCarbohydrate"),
          "percentDailyValue": calculate_daily_value("totalCarbohydrate", parsed_data["totalCarbohydrate"])
        },
        "dietaryFiber": {
          "amount": parsed_data["dietaryFiber"],
          "unit": "g",
          "dailyReference": get_daily_reference("dietaryFiber"),
          "percentDailyValue": calculate_daily_value("dietaryFiber", parsed_data["dietaryFiber"])
        },
        "totalSugars": {
          "amount": parsed_data["totalSugars"],
          "unit": "g",
          "percentDailyValue": calculate_daily_value("totalSugars", parsed_data["totalSugars"])
        },
        "addedSugars": {
          "amount": parsed_data["addedSugars"],
          "unit": "g",
          "dailyReference": get_daily_reference("addedSugars"),
          "percentDailyValue": calculate_daily_value("addedSugars", parsed_data["addedSugars"])
        },
        "protein": {
          "amount": parsed_data["protein"],
          "unit": "g",
          "dailyReference": get_daily_reference("protein"),
          "percentDailyValue": calculate_daily_value("protein", parsed_data["protein"])
        }
      },

      "micronutrients": {
        "vitaminD": {
          "amount": parsed_data["vitaminD"],
          "unit": "mcg",
          "dailyReference": get_daily_reference("vitaminD"),
          "percentDailyValue": calculate_daily_value("vitaminD", parsed_data["vitaminD"])
        },
        "calcium": {
          "amount": parsed_data["calcium"],
          "unit": "mg",
          "dailyReference": get_daily_reference("calcium"),
          "percentDailyValue": calculate_daily_value("calcium", parsed_data["calcium"])
        },
        "iron": {
          "amount": parsed_data["iron"],
          "unit": "mg",
          "dailyReference": get_daily_reference("iron"),
          "percentDailyValue": calculate_daily_value("iron", parsed_data["iron"])
        },
        "potassium": {
          "amount": parsed_data["potassium"],
          "unit": "mg",
          "dailyReference": get_daily_reference("potassium"),
          "percentDailyValue": calculate_daily_value("potassium", parsed_data["potassium"])
        }
      },

      "ingredients": [
        {
          "name": "Example Ingredient",
          "description": "This is placeholder ingredient information.",
          "isHealthy": True
        }
      ]
    }

    # Generate insights passing the full nutrition response
    try:
        insights = generate_insights(nutrition_response, ocr_text)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Insights failed: {str(error)}"
        )

    # Attach insights to nutrition response
    nutrition_response["insights"] = insights

    return nutrition_response


@app.get("/api/docs")
async def list_docs(current_user = Depends(get_current_user)):
    ensure_db()
    cursor = db.documents.find({"userId": current_user["_id"]}).sort("createdAt", -1)
    docs = await cursor.to_list(length=100)
    return [serialize_doc(doc) for doc in docs]


@app.post("/api/docs")
async def create_doc(payload: DocumentCreate, current_user = Depends(get_current_user)):
    ensure_db()
    doc = {
        "userId": current_user["_id"],
        "title": payload.title,
        "fileSize": payload.fileSize,
        "thumbnailUrl": payload.thumbnailUrl,
        "nutritionData": payload.nutritionData,
        "createdAt": datetime.utcnow().isoformat(),
    }
    result = await db.documents.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)