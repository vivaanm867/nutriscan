import re

def convert_number(value: str):
  number = float(value)

  if number.is_integer():
    return int(number)
  
  return number

def find_nutrient(text: str, label: str, unit: str = ""):
  # Pattern 1: Label before number
  # Example: Sodium 390mg
  pattern_after = rf"{re.escape(label)}\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*{unit}"

  match = re.search(pattern_after, text, re.IGNORECASE)

  if match:
      return convert_number(match.group(1))

  # Pattern 2: Number before label
  # Example: Includes 33g Added Sugars
  pattern_before = rf"(\d+(?:\.\d+)?)\s*{unit}\s*{re.escape(label)}"

  match = re.search(pattern_before, text, re.IGNORECASE)

  if match:
      return convert_number(match.group(1))

  return None

def extract_servings_per_container(text: str):
  """
  Extract servings per container from OCR text.
  Handles patterns like:
  - "6 servings per container"
  - "About 8 servings per container"
  - "6servings per container"
  """
  # Match patterns like "6 servings per container" or "About 8 servings"
  pattern = r"(?:about\s+)?(\d+)\s*servings\s*(?:per\s+container)?"
  match = re.search(pattern, text, re.IGNORECASE)
  
  if match:
    return int(match.group(1))
  
  return None

def extract_serving_size(text: str):
  """
  Extract serving size from OCR text.
  Handles patterns like:
  - "Serving size 2 Pastries (96g)"
  - "Serving size\n2 Pastries (96g)"
  - "2 Pastries (96g)" when it follows "Serving size"
  """
  lines = text.split('\n')
  
  for i, line in enumerate(lines):
    if 'serving size' in line.lower():
      # Check if serving size info is on the same line
      if re.search(r'serving\s*size\s*\d', line, re.IGNORECASE):
        # Extract everything after "serving size"
        match = re.search(r'serving\s*size\s*(.+)', line, re.IGNORECASE)
        if match:
          return match.group(1).strip()
      
      # Check if serving size info is on the next line
      if i + 1 < len(lines):
        next_line = lines[i + 1].strip()
        if next_line and re.search(r'^\d', next_line):
          return next_line
  
  # Fallback: look for patterns like "2 Pastries (96g)" without explicit "Serving size" label
  pattern = r'(\d+(?:\s+[A-Za-z]+)+\s*\(\d+[a-z]+\))'
  match = re.search(pattern, text)
  if match:
    return match.group(1).strip()
  
  return None

def extract_product_name(text: str):
  """
  Extract product name from OCR text.
  Looks for the first meaningful line (non-empty, non-label line).
  """
  lines = text.split('\n')
  
  skip_keywords = {
    'nutrition facts', 'serving', 'calories', 'amount per', 
    'total', 'dietary', 'vitamin', 'mineral', 'calcium', 'iron',
    'sodium', 'fat', 'protein', 'carbohydrate', 'sugar', 'fiber',
    'ingredient', 'contains', '%'
  }
  
  for line in lines:
    cleaned = line.strip()
    if not cleaned or len(cleaned) < 2:
      continue
    
    # Skip lines that are clearly labels
    if any(keyword in cleaned.lower() for keyword in skip_keywords):
      continue
    
    # Skip lines that are mostly numbers/symbols
    if re.match(r'^[\d\s\-\.%]+$', cleaned):
      continue
    
    # Found a reasonable product name
    return cleaned
  
  return None

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

# ---------- Ingredients ----------

# (keywords, description, isHealthy). The first matching rule wins, so order matters.
INGREDIENT_RULES = [
  (("hydrogenated",), "Hydrogenated oil, a source of trans fat.", False),
  (("high fructose", "corn syrup", "syrup", "dextrose", "maltodextrin", "sucrose",
    "fructose", "molasses", "cane sugar", "brown sugar", "sugar"),
   "Added sugar or sweetener.", False),
  (("aspartame", "sucralose", "acesulfame", "saccharin"), "Artificial sweetener.", False),
  (("red 40", "red 3", "yellow 5", "yellow 6", "blue 1", "blue 2", "color added",
    "artificial color", "caramel color"),
   "Artificial or added coloring.", False),
  (("tbhq", "bha", "bht", "sodium benzoate", "potassium sorbate", "sodium nitrite",
    "sodium nitrate"),
   "Synthetic preservative.", False),
  (("artificial flavor",), "Artificial flavoring.", False),
  (("palm oil", "palm kernel"), "Oil high in saturated fat.", False),
  (("enriched", "bleached"), "Refined flour; most of the fiber is removed.", False),
  (("whole grain", "whole wheat", "oats", "brown rice", "quinoa"), "Whole grain, a source of fiber.", True),
  (("vitamin", "niacin", "riboflavin", "thiamin", "folic acid", "iron", "calcium"),
   "Added vitamin or mineral.", True),
]


def _split_top_level(text: str):
  """Split on commas, semicolons and sentence periods that are not inside parentheses."""
  text = re.sub(r"\.\s+", "; ", text)
  parts, depth, current = [], 0, ""
  for char in text:
    if char in "([{":
      depth += 1
    elif char in ")]}":
      depth = max(0, depth - 1)
    if char in ",;" and depth == 0:
      parts.append(current)
      current = ""
    else:
      current += char
  parts.append(current)
  return parts


def _describe_ingredient(name: str):
  lowered = name.lower()
  for keywords, description, is_healthy in INGREDIENT_RULES:
    # Whole-word match, so "bha" doesn't match "alpha" (an optional plural "s" is allowed)
    if any(re.search(rf"\b{re.escape(keyword)}s?\b", lowered) for keyword in keywords):
      return description, is_healthy
  return "", True


def extract_ingredients(text: str, limit: int = 15):
  """
  Pull the ingredient list from the "INGREDIENTS:" line and flag common additives.
  Ingredients are listed by weight, so the first few matter most.
  """
  match = re.search(r"ingredients\s*:\s*(.+)", text, re.IGNORECASE)
  if not match:
    return []

  raw = match.group(1)
  # Stop at the allergen statement, e.g. "CONTAINS: WHEAT, MILK"
  raw = re.split(r"\bcontains\s*:|\ballergens?\b", raw, flags=re.IGNORECASE)[0]

  # Many labels print ingredients in ALL CAPS; only change capitalization in that case.
  all_caps = raw.isupper()

  ingredients = []
  for part in _split_top_level(raw):
    # "Contains 2% or less of molasses" -> "molasses"
    part = re.sub(r"^\s*(and\s+)?(contains\s+)?\d+%\s+or\s+less\s+of\s*:?", "", part, flags=re.IGNORECASE)
    # Drop sub-ingredients in parentheses: "Enriched flour (wheat flour, niacin)" -> "Enriched flour"
    name = re.sub(r"\s*[\(\[].*", "", part).strip(" .:*-")
    if not name or len(name) > 60:
      continue

    description, is_healthy = _describe_ingredient(name)
    ingredients.append({
      "name": name.capitalize() if all_caps else name[0].upper() + name[1:],
      "description": description,
      "isHealthy": is_healthy,
    })
    if len(ingredients) >= limit:
      break

  return ingredients
