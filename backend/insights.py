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
    "debugError": error_message,
  }


def local_insights_from_parsed_data(nutrition_response: dict):
  macro = nutrition_response.get("macronutrients", {})
  micro = nutrition_response.get("micronutrients", {})

  calories_amount = macro.get("calories", {}).get("amount") or 0
  calories_pv = macro.get("calories", {}).get("percentDailyValue") or 0

  protein_amount = macro.get("protein", {}).get("amount") or 0
  protein_pv = macro.get("protein", {}).get("percentDailyValue") or 0

  fiber_amount = macro.get("dietaryFiber", {}).get("amount") or 0
  fiber_pv = macro.get("dietaryFiber", {}).get("percentDailyValue") or 0

  added_sugar_amount = macro.get("addedSugars", {}).get("amount") or 0
  added_sugar_pv = macro.get("addedSugars", {}).get("percentDailyValue") or 0

  sodium_amount = macro.get("sodium", {}).get("amount") or 0
  sodium_pv = macro.get("sodium", {}).get("percentDailyValue") or 0

  sat_fat_amount = macro.get("saturatedFat", {}).get("amount") or 0
  sat_fat_pv = macro.get("saturatedFat", {}).get("percentDailyValue") or 0

  vitamin_d_pv = micro.get("vitaminD", {}).get("percentDailyValue") or 0

  score = 70

  if protein_pv >= 20:
    score += 8
  elif protein_pv >= 10:
    score += 4

  if fiber_pv >= 10:
    score += 6
  elif fiber_pv >= 5:
    score += 2

  if added_sugar_pv >= 50:
    score -= 15
  elif added_sugar_pv >= 20:
    score -= 10
  elif added_sugar_pv >= 10:
    score -= 5

  if sat_fat_pv >= 20:
    score -= 8
  elif sat_fat_pv >= 10:
    score -= 3

  if sodium_pv >= 20:
    score -= 8
  elif sodium_pv >= 10:
    score -= 3

  if fiber_pv < 5:
    score -= 3

  if vitamin_d_pv == 0:
    score -= 2

  if calories_pv > 20:
    score -= 3

  score = max(0, min(100, int(score)))

  highlights = []
  concerns = []

  if protein_pv >= 20:
    highlights.append(f"Good source of protein ({protein_amount}g, {protein_pv}% DV).")

  if fiber_pv >= 10:
    highlights.append(f"Provides good dietary fiber ({fiber_amount}g, {fiber_pv}% DV).")

  if added_sugar_pv <= 5:
    highlights.append(f"Low in added sugars ({added_sugar_amount}g, {added_sugar_pv}% DV).")

  if sat_fat_pv <= 5:
    highlights.append(f"Low in saturated fat ({sat_fat_amount}g, {sat_fat_pv}% DV).")

  if sodium_pv <= 5:
    highlights.append(f"Low in sodium ({sodium_amount}mg, {sodium_pv}% DV).")

  if added_sugar_pv >= 50:
    concerns.append(f"Very high in added sugars ({added_sugar_amount}g, {added_sugar_pv}% DV).")
  elif added_sugar_pv >= 20:
    concerns.append(f"High in added sugars ({added_sugar_amount}g, {added_sugar_pv}% DV).")

  if sat_fat_pv >= 20:
    concerns.append(f"High in saturated fat ({sat_fat_amount}g, {sat_fat_pv}% DV).")
  elif sat_fat_pv >= 10:
    concerns.append(f"Moderate saturated fat ({sat_fat_amount}g, {sat_fat_pv}% DV).")

  if sodium_pv >= 20:
    concerns.append(f"High in sodium ({sodium_amount}mg, {sodium_pv}% DV).")
  elif sodium_pv >= 10:
    concerns.append(f"Moderate sodium content ({sodium_amount}mg, {sodium_pv}% DV).")

  if fiber_pv < 5:
    concerns.append(f"Low in dietary fiber ({fiber_amount}g, {fiber_pv}% DV).")

  if vitamin_d_pv == 0:
    concerns.append("Contains no Vitamin D.")

  if calories_pv > 20:
    concerns.append(f"Relatively high in calories ({calories_amount} kcal, {calories_pv}% DV).")

  if not highlights:
    highlights.append("Contains measurable nutrients based on the label.")

  if not concerns:
    concerns.append("No major nutrition red flags for a single serving.")

  summary = (
    f"This serving contains {calories_amount} calories ({calories_pv}% DV). "
    f"Added sugars: {added_sugar_amount}g ({added_sugar_pv}% DV). "
    f"Sodium: {sodium_amount}mg ({sodium_pv}% DV)."
  )

  return {
    "healthScore": score,
    "summary": summary,
    "highlights": highlights,
    "concerns": concerns,
  }


def generate_insights(nutrition_response: dict, ocr_text: str = ""):
  api_key = os.getenv("GEMINI_API_KEY")

  if not api_key:
    return fallback_insights(
      "GEMINI_API_KEY was not found. Check that backend/.env contains GEMINI_API_KEY=your_key_here."
    )

  client = genai.Client(api_key=api_key)

  prompt = f"""
You are helping analyze a nutrition label for a food label reader app.

Use the nutrition response data below to produce a clear, helpful nutrition summary.

Nutrition response with calculated percentDailyValue:
{json.dumps(nutrition_response, indent=2)}

OCR text:
{ocr_text}

Return ONLY valid JSON in this exact format:
{{
  "healthScore": 75,
  "summary": "short 2-3 sentence summary",
  "highlights": ["positive point 1", "positive point 2"],
  "concerns": ["concern 1", "concern 2"]
}}

Interpretation rules:
- Use percentDailyValue to judge whether nutrients are low, moderate, or high.
- Low = 5% DV or less.
- Moderate = 6% to 19% DV.
- High = 20% DV or more.
- Very high = 50% DV or more.
- Calories should be judged relative to the 2,000 calorie reference.
- Do not call calories high unless percentDailyValue is 20% or more.
- Added sugars at 50% DV or more should be treated as a major concern.
- Low fiber under 5% DV should be treated as a concern.
- Focus concerns on added sugars, saturated fat, sodium, low fiber, and missing/low micronutrients when relevant.
- Do not give medical advice.
- Do not mention that you are an AI.
- Keep the language simple for a general user.
- Your entire response must be valid JSON.
- Do not wrap the JSON in markdown.
- Do not use ```json.
"""

  last_error = ""

  for attempt in range(3):
    try:
      response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
          response_mime_type="application/json"
        ),
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
          "Nutrition insights were generated, but no summary was provided.",
        ),
        "highlights": insights.get("highlights", []),
        "concerns": insights.get("concerns", []),
      }

    except Exception as error:
      last_error = str(error)

      if attempt < 2:
        time.sleep(1.2 * (attempt + 1))
        continue

  print("Gemini insights error:", last_error)

  local = local_insights_from_parsed_data(nutrition_response)
  local["debugError"] = last_error
  return local