import streamlit as st
import cv2
import pytesseract
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\sowed\PycharmProjects\mpr\app\Tesseract-OCR\tesseract.exe"

import numpy as np
from PIL import Image

st.set_page_config(page_title="OCR Extractor", layout="centered")


def preprocess_image(img):
    """Convert image to grayscale and apply thresholding."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh


def ocr_core(img):
    """Extract text using pytesseract."""
    return pytesseract.image_to_string(img)


# Streamlit UI
st.title("OCR Text Extractor")
st.write("Upload an image, and the system will extract text using Tesseract OCR.")

# File uploader
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Convert to OpenCV format
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    img_cv2 = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

    # Display original image (fixed: use_container_width replaces use_column_width)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    # Preprocess & Extract text
    processed_img = preprocess_image(img_cv2)
    extracted_text = ocr_core(processed_img)

    # Show extracted text
    st.subheader("📜 Extracted Text:")
    # st.text_area("", extracted_text, height=200)
    st.text_area("Extracted Text:", extracted_text, height=400, label_visibility="collapsed")

    # Download extracted text
    st.download_button(
        label="📥 Download Extracted Text",
        data=extracted_text,
        file_name="extracted_text.txt",
        mime="text/plain"
    )
