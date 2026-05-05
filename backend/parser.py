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