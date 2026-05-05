import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


def fallback_insights(error_message: str = ""):
    return {
        "healthScore": 70,
        "summary": "Nutrition insights are temporarily unavailable, but basic nutrition data was extracted.",
        "highlights": [],
        "concerns": [
            "Could not generate AI nutrition insights right now."
        ],
        "debugError": error_message
    }


def local_insights_from_parsed_data(parsed_data: dict):
    calories = parsed_data.get("calories") or 0
    protein = parsed_data.get("protein") or 0
    fiber = parsed_data.get("dietaryFiber") or 0
    added_sugar = parsed_data.get("addedSugars") or 0
    sodium = parsed_data.get("sodium") or 0
    sat_fat = parsed_data.get("saturatedFat") or 0
    vitamin_d = parsed_data.get("vitaminD") or 0

    score = 70
    if protein >= 8:
        score += 5
    if fiber >= 3:
        score += 5
    if added_sugar <= 5:
        score += 3
    if sat_fat <= 2:
        score += 2
    if sodium > 400:
        score -= 8
    elif sodium > 200:
        score -= 4
    if calories > 350:
        score -= 6
    elif calories > 250:
        score -= 3
    if vitamin_d == 0:
        score -= 2

    score = max(0, min(100, int(score)))

    highlights = []
    concerns = []

    if protein >= 8:
        highlights.append(f"Good source of protein ({protein}g).")
    if fiber >= 3:
        highlights.append(f"Provides dietary fiber ({fiber}g).")
    if added_sugar <= 5:
        highlights.append(f"Low in added sugars ({added_sugar}g).")
    if sat_fat <= 2:
        highlights.append(f"Low saturated fat ({sat_fat}g).")

    if sodium > 200:
        concerns.append(f"Sodium is on the higher side ({sodium}mg).")
    if added_sugar > 10:
        concerns.append(f"Added sugar is relatively high ({added_sugar}g).")
    if calories > 300:
        concerns.append(f"Calories are relatively high per serving ({calories}).")
    if vitamin_d == 0:
        concerns.append("Provides little or no Vitamin D.")

    if not highlights:
        highlights.append("Contains measurable nutrients based on the label.")
    if not concerns:
        concerns.append("No major nutrition red flags for a single serving.")

    summary = (
        f"This serving has {calories} calories, {protein}g protein, and {fiber}g fiber. "
        f"It includes {added_sugar}g added sugar and {sodium}mg sodium."
    )

    return {
        "healthScore": score,
        "summary": summary,
        "highlights": highlights,
        "concerns": concerns
    }


def generate_insights(parsed_data: dict, ocr_text: str = ""):
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return fallback_insights(
            "GEMINI_API_KEY was not found. Check that backend/.env exists and contains GEMINI_API_KEY=your_key_here."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are helping analyze a nutrition label for a food label reader app.

Use the parsed nutrition data and OCR text below to produce a clear, helpful nutrition summary.

Parsed nutrition data:
{json.dumps(parsed_data, indent=2)}

OCR text:
{ocr_text}

Return ONLY valid JSON in this exact format:
{{
  "healthScore": 75,
  "summary": "short 2-3 sentence summary",
  "highlights": ["positive point 1", "positive point 2"],
  "concerns": ["concern 1", "concern 2"]
}}

Rules:
- Your entire response must be valid JSON.
- Do not wrap the JSON in markdown.
- Do not use ```json.
- healthScore should be an integer from 0 to 100.
- summary should be 2-3 short sentences.
- highlights should focus on good nutritional aspects.
- concerns should focus on things like high sodium, added sugar, saturated fat, low fiber, or high calories.
- Do not give medical advice.
- Do not mention that you are an AI.
- Keep the language simple for a general user.
"""

    models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash"]
    last_error = ""

    for model_name in models_to_try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )

                text = (response.text or "").strip()
                text = text.replace("```json", "").replace("```", "").strip()

                try:
                    insights = json.loads(text)
                except json.JSONDecodeError:
                    last_error = f"Gemini returned non-JSON text: {text}"
                    break

                return {
                    "healthScore": insights.get("healthScore", 70),
                    "summary": insights.get(
                        "summary",
                        "Nutrition insights were generated, but no summary was provided."
                    ),
                    "highlights": insights.get("highlights", []),
                    "concerns": insights.get("concerns", [])
                }

            except Exception as error:
                last_error = str(error)
                if attempt < 2:
                    time.sleep(1.2 * (attempt + 1))
                    continue
                break

    print("Gemini insights error:", last_error)
    local = local_insights_from_parsed_data(parsed_data)
    local["debugError"] = last_error
    return local