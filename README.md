# NutriScan

Full-stack nutrition label analyzer that reads food label photos with Gemini Vision, parses key nutrients and ingredients, and generates simple AI-powered health insights.

**🔗 Live demo: https://nutriscan-app-2txo.onrender.com**

## Overview

NutriScan helps users better understand nutrition labels by turning an uploaded image into structured nutrition data. The system reads the label, extracts important values such as calories, fat, sodium, carbohydrates, sugars, protein, and micronutrients, flags common additives in the ingredient list, then presents the results in a clean dashboard with an AI-generated summary.

The project focuses on making nutrition labels easier to understand for everyday users by combining image processing, backend parsing logic, authentication, database storage, and AI-generated explanations.

## How It Works

**Nutrition Analysis Pipeline:**

Image Upload → Image Preprocessing → Gemini Vision Text Extraction → Nutrition & Ingredient Parsing → Daily Value Calculation → AI Insight Generation → Dashboard Display

### Pipeline Steps

* **Image Input:** User uploads a photo of a nutrition label.
* **Preprocessing:** Pillow auto-rotates phone photos and downscales them to 1600px to cut upload size and API cost.
* **Text Extraction:** Gemini Vision transcribes the label into a consistent, line-by-line format. Non-label images are rejected.
* **Nutrition Parsing:** A custom regex parser extracts 15 nutrients, serving size, and servings per container.
* **Ingredient Analysis:** The ingredient list is split (respecting nested sub-ingredients) and each item is checked against rules for added sugars, artificial colors and sweeteners, preservatives, hydrogenated oils, refined flour, and whole grains.
* **Daily Value Calculation:** Parsed nutrients are compared against FDA daily reference values.
* **AI Insights:** Gemini generates a readable summary, highlights, concerns, and a health score, with a rules-based fallback if the API is unavailable.
* **Frontend Display:** Results are shown in a React dashboard.

## Key Technical Decisions

* **Switched from EasyOCR to Gemini Vision:** EasyOCR misread characters on real labels (`0g` → `Og`, `390mg` → `39 omg`, `35g` → `359`), so only **7 of 15** nutrients parsed correctly on a test label. With Gemini Vision producing clean text, the same parser extracted **15 of 15**. It also removed the ~2GB PyTorch dependency, which made free-tier hosting possible.
* **Custom Nutrition Parser:** Regex-based parsing handles both "Sodium 390mg" and "Includes 33g Added Sugars" formats.
* **Rule-Based Ingredient Flags:** Deterministic, whole-word keyword rules (so "BHA" doesn't match "alpha") keep ingredient flags fast, free, and explainable.
* **Daily Value Mapping:** Nutrient values are converted into percent daily values for easier interpretation.
* **FastAPI Backend:** Handles image uploads, text extraction, parsing, authentication, and saved scans.
* **MongoDB Storage:** Stores user accounts and saved nutrition scans (MongoDB Atlas). Scans are scoped to their owner, so users can only open or delete their own.
* **JWT Authentication:** Uses PyJWT and bcrypt password hashing to protect user-specific routes and the analysis endpoint.
* **API Protection:** 8MB upload limit, image type validation, and a per-user hourly scan limit to protect the Gemini quota.
* **Environment-Based Config:** All secrets and settings (database, API keys, allowed origins) come from environment variables.
* **React Dashboard:** Displays nutrition results in a clean, responsive interface.

## Features

* Upload nutrition label images (including from a phone camera)
* Extract label text with Gemini Vision
* Parse key nutrition facts and calculate percent daily values
* Flag ingredients like added sugars, artificial colors, and preservatives
* Generate AI-powered nutrition summaries
* Create an account and log in
* Save scans to your history, reopen them, and delete them
* View results in a dashboard interface

## Tech Stack

**Frontend:** React, Vite, Tailwind CSS, React Router, Lucide React

**Backend:** Python, FastAPI, Google Gemini (google-genai), Pillow, MongoDB, Motor, PyJWT, bcrypt

**Deployment:** Render (FastAPI web service and static site), MongoDB Atlas

## Run Locally

**Requirements:** Python 3.11+, Node.js 20+, a free [MongoDB Atlas](https://www.mongodb.com/atlas) cluster, and a free [Gemini API key](https://aistudio.google.com/apikey).

**Backend:**

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
python -m pip install -r requirements.txt
```

Copy `backend/.env.example` to `backend/.env` and fill in your values, then:

```bash
python -m uvicorn main:app --reload
```

The API runs at http://localhost:8000 (interactive docs at `/docs`).

**Frontend** (new terminal, from the project root):

```bash
npm install
npm run dev
```

The app runs at http://localhost:3000.

## Development Note

AI tools were used to help generate and style the frontend interface, which was then connected to the backend.

## Current Limitations

* Accuracy depends on image quality. Blurry or angled photos may miss values.
* Values are per serving as printed on the label. Non-US label formats may parse less reliably.
* Ingredient flags are general, keyword-based guidance and may miss uncommon additives.
* The free hosting tier sleeps when idle, so the first request after a while is slow.
* The app is intended for general nutrition understanding and should not be used as medical advice.

## Future Improvements

* Add barcode scanning
* Use personalized nutrition goals in the results
* Compare two products side by side
* Add automated tests and CI

## Contact

Vivaan Motwani
https://github.com/vivaanm867
