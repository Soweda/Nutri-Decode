from flask import Blueprint, render_template, request, jsonify, url_for
import os
import cv2
import pytesseract
import re
import numpy as np
from werkzeug.utils import secure_filename

main = Blueprint("main", __name__)
UPLOAD_FOLDER = "./app/static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\sowed\PycharmProjects\mpr\app\Tesseract-OCR\tesseract.exe"

def preprocess_image(img_path):
    """Load image, convert to grayscale, and apply thresholding for better OCR."""
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text(img_path):
    """Extract text using Tesseract OCR."""
    processed_img = preprocess_image(img_path)
    text = pytesseract.image_to_string(processed_img)
    return text.strip()

def extract_nutritional_values(text):
    """Extract nutrient information using regex."""
    nutrients = {}
    nutrient_patterns = {
    "carbohydrates": r"(?:carbohydrates?|carbs?|carbohydrate?)[:\s]*([\d.]+)\s*g?",
    "sugar": r"(?:sugar|sugars)[:\s]*([\d.]+)\s*g?",
    "added_sugar": r"(?:added\s*sugar|added\s*sugars)[:\s]*([\d.]+)\s*g?",
    "protein": r"(?:protein|proteins)[:\s]*([\d.]+)\s*g?",
    "fat": r"(?:fat|fats)[:\s]*([\d.]+)\s*g?",
    "saturated_fat": r"(?:saturated\s*(?:fat|fats|fatty\s*acids?))[:\s]*([\d.]+)\s*g?",
    "monounsaturated_fat": r"(?:monounsaturated\s*(?:fat|fats|fatty\s*acids?))[:\s]*([\d.]+)\s*g?",
    "polyunsaturated_fat": r"(?:polyunsaturated\s*(?:fat|fats|fatty\s*acids?))[:\s]*([\d.]+)\s*g?",
    "trans_fat": r"(?:trans\s*(?:fat|fats|fatty\s*acids?))[:\s]*([\d.]+)\s*g?",
    "cholesterol": r"(?:cholestrol|cholesterol)[:\s]*([\d.]+)\s*mg?",
    "calcium": r"(?:calcium)[:\s]*([\d.]+)\s*mg?",
    "iron": r"(?:iron)[:\s]*([\d.]+)\s*mg?",
    "sodium": r"(?:sodium)[:\s]*([\d.]+)\s*mg?",
    "potassium": r"(?:potassium)[:\s]*([\d.]+)\s*mg?",
    "fiber": r"(?:fiber|fibres|dietary\s*fiber)[:\s]*([\d.]+)\s*g?",
    "vitamin_a": r"(?:vitamin\s*A)[:\s]*([\d.]+)\s*(?:mcg|mg|IU)?",
    "vitamin_c": r"(?:vitamin\s*C)[:\s]*([\d.]+)\s*mg?",
    "vitamin_d": r"(?:vitamin\s*D)[:\s]*([\d.]+)\s*(?:mcg|IU)?",
    "vitamin_e": r"(?:vitamin\s*E)[:\s]*([\d.]+)\s*mg?",
    "vitamin_k": r"(?:vitamin\s*K)[:\s]*([\d.]+)\s*mcg?",
    "energy": r"(?:energy|calories|kcal)[:\s]*([\d.]+)\s*kcal?",
    "zinc": r"(?:zinc)[:\s]*([\d.]+)\s*mg?",
    "magnesium": r"(?:magnesium)[:\s]*([\d.]+)\s*mg?",
    }
    for nutrient, pattern in nutrient_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            value=value.replace("O","0")
            # Convert all values to grams (mg -> g)
            if "mg" in pattern and float(value) > 0:
                value = round(float(value) / 1000, 3)  # Convert mg to g
            nutrients[nutrient] = float(value)
    return nutrients

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded!"})
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected!"})
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    extracted_text = extract_text(filepath)
    nutrients = extract_nutritional_values(extracted_text)
    return jsonify({
        "success": True,
        "message": "File uploaded and processed successfully!",
        "extracted_text": extracted_text,
        "uploaded_url": url_for("static", filename=f"uploads/{filename}"),
        "nutrients": nutrients
    })

@main.route("/update_nutrients", methods=["POST"])
def update_nutrients():
    data = request.get_json()
    weight = float(data.get("weight", 100))
    original_nutrients = data.get("nutrients", {})
    adjusted_nutrients = {nutrient: round(value * weight / 100, 2) for nutrient, value in original_nutrients.items()}
    return jsonify({
        "success": True,
        "nutrients": adjusted_nutrients
    })
