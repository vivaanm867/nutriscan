import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai


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


def local_insights_from_parsed_data(nutrition_response: dict):
    # Extract values from nutrition_response structure (with percentDailyValue)
    macro = nutrition_response.get("macronutrients", {})
    micro = nutrition_response.get("micronutrients", {})
    
    # Get amounts and percentDailyValues
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
    
    vitamin_d_amount = micro.get("vitaminD", {}).get("amount") or 0
    vitamin_d_pv = micro.get("vitaminD", {}).get("percentDailyValue") or 0

    score = 70

    # Positive factors (increase score)
    if protein_pv and protein_pv >= 20:  # High protein (20%+ DV)
        score += 8
    elif protein_pv and protein_pv >= 10:  # Moderate protein (10-19% DV)
        score += 4
    
    if fiber_pv and fiber_pv >= 10:  # Good fiber (10%+ DV)
        score += 6
    elif fiber_pv and fiber_pv >= 5:  # Some fiber (5-9% DV)
        score += 2
    
    # Negative factors (decrease score)
    if added_sugar_pv and added_sugar_pv >= 50:  # Very high added sugar (50%+ DV)
        score -= 15
    elif added_sugar_pv and added_sugar_pv >= 20:  # High added sugar (20-49% DV)
        score -= 10
    elif added_sugar_pv and added_sugar_pv >= 10:  # Moderate added sugar (10-19% DV)
        score -= 5
    
    if sat_fat_pv and sat_fat_pv >= 20:  # High saturated fat (20%+ DV)
        score -= 8
    elif sat_fat_pv and sat_fat_pv >= 10:  # Moderate saturated fat (10-19% DV)
        score -= 3
    
    if sodium_pv and sodium_pv >= 20:  # High sodium (20%+ DV)
        score -= 8
    elif sodium_pv and sodium_pv >= 10:  # Moderate sodium (10-19% DV)
        score -= 3
    
    if fiber_pv and fiber_pv < 5:  # Low fiber (under 5% DV)
        score -= 3
    
    if vitamin_d_pv and vitamin_d_pv == 0:  # No vitamin D
        score -= 2
    
    if calories_pv and calories_pv > 20:  # High calories only if over 20% DV
        score -= 3

    score = max(0, min(100, int(score)))

    highlights = []
    concerns = []

    # Build highlights based on percentDailyValue
    if protein_pv and protein_pv >= 20:
        highlights.append(f"Good source of protein ({protein_amount}g, {protein_pv}% DV).")
    if fiber_pv and fiber_pv >= 10:
        highlights.append(f"Provides good dietary fiber ({fiber_amount}g, {fiber_pv}% DV).")
    if added_sugar_pv and added_sugar_pv <= 5:
        highlights.append(f"Low in added sugars ({added_sugar_amount}g, {added_sugar_pv}% DV).")
    if sat_fat_pv and sat_fat_pv <= 5:
        highlights.append(f"Low in saturated fat ({sat_fat_amount}g, {sat_fat_pv}% DV).")
    if sodium_pv and sodium_pv <= 5:
        highlights.append(f"Low in sodium ({sodium_amount}mg, {sodium_pv}% DV).")

    # Build concerns based on percentDailyValue
    if added_sugar_pv and added_sugar_pv >= 50:
        concerns.append(f"Very high in added sugars ({added_sugar_amount}g, {added_sugar_pv}% DV).")
    elif added_sugar_pv and added_sugar_pv >= 20:
        concerns.append(f"High in added sugars ({added_sugar_amount}g, {added_sugar_pv}% DV).")
    
    if sat_fat_pv and sat_fat_pv >= 20:
        concerns.append(f"High in saturated fat ({sat_fat_amount}g, {sat_fat_pv}% DV).")
    elif sat_fat_pv and sat_fat_pv >= 10:
        concerns.append(f"Moderate saturated fat ({sat_fat_amount}g, {sat_fat_pv}% DV).")
    
    if sodium_pv and sodium_pv >= 20:
        concerns.append(f"High in sodium ({sodium_amount}mg, {sodium_pv}% DV).")
    elif sodium_pv and sodium_pv >= 10:
        concerns.append(f"Moderate sodium content ({sodium_amount}mg, {sodium_pv}% DV).")
    
    if fiber_pv and fiber_pv < 5:
        concerns.append(f"Low in dietary fiber ({fiber_amount}g, {fiber_pv}% DV).")
    
    if vitamin_d_pv and vitamin_d_pv == 0:
        concerns.append("Contains no Vitamin D.")
    
    if calories_pv and calories_pv > 20:
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
        "concerns": concerns
    }


def generate_insights(nutrition_response: dict, ocr_text: str = ""):
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    if not api_key:
        return fallback_insights(
            "GEMINI_API_KEY was not found. Check that backend/.env exists and contains GEMINI_API_KEY=your_key_here."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are helping analyze a nutrition label for a food label reader app.

Use the nutrition response data below to produce a clear, helpful nutrition summary.

Nutrition response (with calculated percentDailyValue):
{json.dumps(nutrition_response, indent=2)}

Return ONLY valid JSON in this exact format:
{{
  "healthScore": 75,
  "summary": "short 2-3 sentence summary",
  "highlights": ["positive point 1", "positive point 2"],
  "concerns": ["concern 1", "concern 2"]
}}

IMPORTANT INTERPRETATION RULES:
- Use percentDailyValue to judge if a nutrient is low, moderate, or high.
- Low = 5% DV or less
- Moderate = 5% to 19% DV (for most nutrients) OR 10-19% for calories
- High = 20% DV or more
- Very High = 50% DV or more

CALORIE INTERPRETATION:
- 370 calories (18-19% of 2000) = MODERATE, not high. Only flag calories as high if above 20% DV.

HIGHLIGHT NUTRIENTS (when high/very high):
- Added Sugars at 66% DV = VERY HIGH - this is a major concern
- Saturated Fat at 15% DV = moderate concern
- Sodium at 17% DV = moderate concern
- Fiber at 4% DV = LOW, note as a negative

NUTRIENT FOCUS:
- Focus on high percentDailyValue nutrients, especially:
  1. Added sugars (flag as very high if 50%+ DV)
  2. Saturated fat (flag if 20%+ DV)
  3. Sodium (flag if 20%+ DV)
  4. Low fiber (flag if under 10% DV)
  5. Low vitamin D (flag if 0% DV)
  6. Do NOT flag calories as high unless above 20% DV

SUMMARY GUIDANCE:
- Be concise: 2-3 short sentences
- Highlight the main nutritional profile
- Mention specific percentDailyValue concerns if relevant (e.g., "33g added sugars (66% DV)")
- Do not give medical advice
- Keep the language simple for a general user

Rules:
- Your entire response must be valid JSON.
- Do not wrap the JSON in markdown.
- Do not use ```json.
- healthScore should be an integer from 0 to 100.
- highlights should focus on good nutritional aspects.
- concerns should focus on high percentDailyValue nutrients, not just presence.
"""

    models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash"]
    last_error = ""

    for model_name in models_to_try:
      for attempt in range(3):
        try:
          response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={"response_mime_type": "application/json"}
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
    local = local_insights_from_parsed_data(nutrition_response)
    local["debugError"] = last_error
    return local