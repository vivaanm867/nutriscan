from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
  return {
    "message": "NutriScan backend is working"
  }

@app.post("/api/analyze")
async def analyze_label(
  image: UploadFile = File(...),
  foodName: str = Form("")
):
  return {
    "productName": foodName or "Unknown Food",
    "brand": "Example Brand",

    "servingSize": "1 serving",
    "servingsPerContainer": 1,

    "macronutrients": {
        "calories": {
            "amount": 150,
            "unit": "kcal",
            "dailyValue": 8
        },
        "totalFat": {
            "amount": 4,
            "unit": "g",
            "dailyValue": 5
        },
        "saturatedFat": {
            "amount": 1,
            "unit": "g",
            "dailyValue": 5
        },
        "transFat": {
            "amount": 0,
            "unit": "g",
            "dailyValue": None
        },
        "cholesterol": {
            "amount": 5,
            "unit": "mg",
            "dailyValue": 2
        },
        "sodium": {
            "amount": 120,
            "unit": "mg",
            "dailyValue": 5
        },
        "totalCarbohydrate": {
            "amount": 20,
            "unit": "g",
            "dailyValue": 7
        },
        "dietaryFiber": {
            "amount": 3,
            "unit": "g",
            "dailyValue": 11
        },
        "totalSugars": {
            "amount": 6,
            "unit": "g",
            "dailyValue": None
        },
        "addedSugars": {
            "amount": 2,
            "unit": "g",
            "dailyValue": 4
        },
        "protein": {
            "amount": 8,
            "unit": "g",
            "dailyValue": 16
        }
    },

    "micronutrients": {
        "vitaminD": {
            "amount": 0,
            "unit": "mcg",
            "dailyValue": 0
        },
        "calcium": {
            "amount": 100,
            "unit": "mg",
            "dailyValue": 8
        },
        "iron": {
            "amount": 1,
            "unit": "mg",
            "dailyValue": 6
        },
        "potassium": {
            "amount": 200,
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

    "insights": {
        "healthScore": 78,
        "summary": "This is placeholder nutrition analysis from the backend.",
        "highlights": [
            "Good source of protein",
            "Moderate calorie amount"
        ],
        "concerns": [
            "Check added sugar content"
        ]
    }
  }