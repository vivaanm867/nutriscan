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
from parser import parse_nutrition_text

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
    image_bytes = await image.read()
    ocr_text = extract_text_from_image(image_bytes)
    parsed_data = parse_nutrition_text(ocr_text)
    insights = generate_insights(parsed_data, ocr_text)

    return {
        "productName": foodName or "Unknown Food",
        "ocrText": ocr_text,
        "brand": "Example Brand",
        "servingSize": "1 serving",
        "servingsPerContainer": 1,

        "macronutrients": {
            "calories": {
                "amount": parsed_data["calories"],
                "unit": "kcal",
                "dailyValue": 8
            },
            "totalFat": {
                "amount": parsed_data["totalFat"],
                "unit": "g",
                "dailyValue": 5
            },
            "saturatedFat": {
                "amount": parsed_data["saturatedFat"],
                "unit": "g",
                "dailyValue": 5
            },
            "transFat": {
                "amount": parsed_data["transFat"],
                "unit": "g",
                "dailyValue": None
            },
            "cholesterol": {
                "amount": parsed_data["cholesterol"],
                "unit": "mg",
                "dailyValue": 2
            },
            "sodium": {
                "amount": parsed_data["sodium"],
                "unit": "mg",
                "dailyValue": 5
            },
            "totalCarbohydrate": {
                "amount": parsed_data["totalCarbohydrate"],
                "unit": "g",
                "dailyValue": 7
            },
            "dietaryFiber": {
                "amount": parsed_data["dietaryFiber"],
                "unit": "g",
                "dailyValue": 11
            },
            "totalSugars": {
                "amount": parsed_data["totalSugars"],
                "unit": "g",
                "dailyValue": None
            },
            "addedSugars": {
                "amount": parsed_data["addedSugars"],
                "unit": "g",
                "dailyValue": 4
            },
            "protein": {
                "amount": parsed_data["protein"],
                "unit": "g",
                "dailyValue": 16
            }
        },

        "micronutrients": {
            "vitaminD": {
                "amount": parsed_data["vitaminD"],
                "unit": "mcg",
                "dailyValue": 0
            },
            "calcium": {
                "amount": parsed_data["calcium"],
                "unit": "mg",
                "dailyValue": 8
            },
            "iron": {
                "amount": parsed_data["iron"],
                "unit": "mg",
                "dailyValue": 6
            },
            "potassium": {
                "amount": parsed_data["potassium"],
                "unit": "mg",
                "dailyValue": 4
            }
        },

        "ingredients": [
            {
                "name": "Example Ingredient",
                "description": "This is placeholder ingredient information.",
                "isHealthy": True
            }
        ],

        "insights": insights
    }


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