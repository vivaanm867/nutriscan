import os
from pathlib import Path

import requests
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

def extract_text_from_image(image_bytes: bytes) -> str:
  api_key = os.getenv("OCR_SPACE_API_KEY")

  if not api_key:
    raise RuntimeError(
      "OCR_SPACE_API_KEY was not found. Add it to backend\.env"
    )
  
  url = "https://api.ocr.space/parse/image"

  files = {
    "file": ("nutrition_label.jpg", image_bytes)
  }

  data = {
    "apikey": api_key,
    "language": "eng",
    "isOverlayRequired": "false",
    "OCREngine": "2",
    "scale": "true",
    "detectOrientation": "true",
  }

  headers = {
    "apikey": api_key
  }

  response = requests.post(
    url,
    files=files,
    data=data,
    headers=headers,
    timeout=30
  )

  if response.status_code != 200:
    raise RuntimeError(
      f"OCR.space request failed with status {response.status_code}: {response.text}"
    )
  
  result = response.json()

  if result.get("IsErroredOnProcessing"):
    raise RuntimeError(
      f"OCR.space processing error: {result.get('ErrorMessage')}"
    )
  
  parsed_results = result.get("ParsedResults", [])

  if not parsed_results:
    raise RuntimeError("OCR.space returned no parsed results.")
  
  extracted_text = parsed_results[0].get("ParsedText", "")

  if not extracted_text.strip():
        raise RuntimeError("OCR.space did not find any text in the image.")

  return extracted_text