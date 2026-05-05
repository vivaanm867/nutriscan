import re

def convert_number(value: str):
  number = float(value)

  if number.is_integer():
    return int(number)
  
  return number

def find_nutrient(text: str, label: str, unit: str = ""):
  pattern = rf"{re.escape(label)}\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*{unit}"

  match = re.search(pattern, text, re.IGNORECASE)

  if not match:
    return None
  
  return convert_number(match.group(1))

def parse_nutrition_text(text: str):
  return {
        "calories": find_nutrient(text, "Calories"),
        "totalFat": find_nutrient(text, "Total Fat", "g"),
        "saturatedFat": find_nutrient(text, "Saturated Fat", "g"),
        "transFat": find_nutrient(text, "Trans Fat", "g"),
        "cholesterol": find_nutrient(text, "Cholesterol", "mg"),
        "sodium": find_nutrient(text, "Sodium", "mg"),
        "totalCarbohydrate": find_nutrient(text, "Total Carbohydrate", "g"),
        "dietaryFiber": find_nutrient(text, "Dietary Fiber", "g"),
        "totalSugars": find_nutrient(text, "Total Sugars", "g"),
        "addedSugars": find_nutrient(text, "Added Sugars", "g"),
        "protein": find_nutrient(text, "Protein", "g"),
        "vitaminD": find_nutrient(text, "Vitamin D", "mcg"),
        "calcium": find_nutrient(text, "Calcium", "mg"),
        "iron": find_nutrient(text, "Iron", "mg"),
        "potassium": find_nutrient(text, "Potassium", "mg"),
    }