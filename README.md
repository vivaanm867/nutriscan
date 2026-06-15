# NutriScan

Full-stack nutrition label analyzer that extracts nutrition facts from food label images using OCR, parses key nutrients, and generates simple AI-powered health insights.

## Overview

NutriScan helps users better understand nutrition labels by turning an uploaded image into structured nutrition data. The system reads the label, extracts important values such as calories, fat, sodium, carbohydrates, sugars, protein, and micronutrients, then presents the results in a clean dashboard with an AI-generated summary.

The project focuses on making nutrition labels easier to understand for everyday users by combining image processing, backend parsing logic, authentication, database storage, and AI-generated explanations.

## How It Works

**Nutrition Analysis Pipeline:**

Image Upload → OCR Text Extraction → Nutrition Fact Parsing → Daily Value Calculation → AI Insight Generation → Dashboard Display

### Pipeline Steps

* **Image Input:** User uploads a photo of a nutrition label.
* **OCR Processing:** EasyOCR extracts raw text from the image.
* **Nutrition Parsing:** The backend identifies key nutrition values using custom parsing logic.
* **Daily Value Calculation:** Parsed nutrients are compared against standard daily reference values.
* **AI Insights:** Gemini generates a readable summary, highlights, concerns, and health score.
* **Frontend Display:** Results are shown in a React dashboard.

## Key Technical Decisions

* **OCR-Based Label Reading:** Uses EasyOCR to extract text directly from uploaded nutrition label images.
* **Custom Nutrition Parser:** Backend parsing logic identifies nutrients such as calories, sodium, fat, carbs, sugars, protein, and micronutrients.
* **Daily Value Mapping:** Nutrient values are converted into percent daily values for easier interpretation.
* **FastAPI Backend:** Handles image uploads, OCR processing, nutrition parsing, authentication, and document storage.
* **MongoDB Storage:** Stores user accounts and saved nutrition documents.
* **JWT Authentication:** Protects user-specific routes and saved document data.
* **Gemini-Powered Insights:** Converts structured nutrition data into simple user-facing explanations.
* **React Dashboard:** Displays nutrition results in a clean, responsive interface.

## Features

* Upload nutrition label images
* Extract text from images using OCR
* Parse key nutrition facts
* Calculate percent daily values
* Generate AI-powered nutrition summaries
* Create an account and log in
* Save and view nutrition documents
* View results in a dashboard interface

## Tech Stack

**Frontend:** React, Vite, Tailwind CSS, React Router, Lucide React

**Backend:** Python, FastAPI, EasyOCR, Pillow, MongoDB, Motor, JWT, Gemini API

**Data Processing:** OCR text extraction, regex-based parsing, daily value calculations

## Development Note

AI tools were used to help generate and style the frontend interface, which was then connected to the backend.

## Current Limitations

* OCR accuracy depends on image quality and label formatting.
* Some unusual nutrition label layouts may not parse perfectly.
* Ingredient extraction is still limited.
* Gemini insights require a valid API key.
* The app is intended for general nutrition understanding and should not be used as medical advice.

## Future Improvements

* Improve image preprocessing before OCR
* Make the parser more accurate across different label formats
* Add barcode scanning
* Add personalized nutrition goals
* Improve saved scan history
* Add stronger ingredient analysis
* Deploy the frontend and backend online

## Contact

Vivaan Motwani
https://github.com/vivaanm867
