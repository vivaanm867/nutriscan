from io import BytesIO

import easyocr
import numpy as np
from PIL import Image

_reader = None


def _get_reader():
  global _reader

  if _reader is None:
    _reader = easyocr.Reader(["en"], gpu=False)

  return _reader


def extract_text_from_image(image_bytes: bytes) -> str:
  try:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
  except Exception as error:
    raise RuntimeError(f"Failed to decode image: {error}")

  reader = _get_reader()
  result = reader.readtext(np.array(image), detail=0, paragraph=True)

  if not result:
    raise RuntimeError("EasyOCR did not find any text in the image.")

  if isinstance(result, list):
    extracted_text = "\n".join(line for line in result if str(line).strip())
  else:
    extracted_text = str(result).strip()

  if not extracted_text:
    raise RuntimeError("EasyOCR returned empty text after processing.")

  return extracted_text