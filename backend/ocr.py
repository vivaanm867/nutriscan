from io import BytesIO

from google import genai
from google.genai import types
from PIL import Image, ImageOps

import config

PROMPT = """Transcribe the Nutrition Facts label in this image as plain text.
Rules:
- First line: the product name, if it is printed. Otherwise skip it.
- Then "Serving size ..." and "N servings per container" if shown.
- Then one nutrient per line, written as "<Nutrient> <amount><unit>", e.g. "Sodium 390mg".
  Write "Includes 10g Added Sugars" for added sugars.
- Use the digit 0, never the letter O. Do not include % Daily Value numbers.
- If an ingredients list is visible, add one final line starting with "INGREDIENTS:".
- If the image is not a nutrition label, reply with exactly: NOT_A_LABEL"""


def _prepare_image(image_bytes: bytes) -> bytes:
  """Fix phone rotation and shrink big photos so uploads are fast and cheap."""
  try:
    image = Image.open(BytesIO(image_bytes))
    image = ImageOps.exif_transpose(image).convert("RGB")
  except Exception as error:
    raise RuntimeError(f"Failed to decode image: {error}")

  image.thumbnail((1600, 1600))
  output = BytesIO()
  image.save(output, format="JPEG", quality=90)
  return output.getvalue()


def extract_text_from_image(image_bytes: bytes) -> str:
  if not config.GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set.")

  client = genai.Client(api_key=config.GEMINI_API_KEY)
  response = client.models.generate_content(
    model=config.GEMINI_MODEL,
    contents=[
      types.Part.from_bytes(data=_prepare_image(image_bytes), mime_type="image/jpeg"),
      PROMPT,
    ],
    config=types.GenerateContentConfig(temperature=0),
  )

  text = (response.text or "").strip()

  if not text:
    raise RuntimeError("No text was found in the image.")
  if text == "NOT_A_LABEL":
    raise RuntimeError("This doesn't look like a nutrition label.")

  return text