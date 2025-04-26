import streamlit as st
import os

def check_dependencies():
    """Check if required libraries are installed and provide installation instructions"""
    check_tesseract()
    check_pdf_libraries()

def check_tesseract():
    """Check if Tesseract OCR is installed and configured"""
    try:
        import pytesseract
        # If on Windows, check if tesseract path is set
        if os.name == 'nt':
            if not pytesseract.pytesseract.tesseract_cmd:
                st.warning("Tesseract path not set. Please install Tesseract OCR and set the path in Settings.")
                st.markdown("""
                ### Installing Tesseract OCR on Windows:
                1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
                2. Install and note the installation path
                3. Enter the path in the Settings tab (typically `C:\\Program Files\\Tesseract-OCR\\tesseract.exe`)
                """)
    except ImportError:
        st.error("pytesseract not installed. Install with: pip install pytesseract")

def check_pdf_libraries():
    """Check for PDF processing libraries"""
    pdf_libs = []
    
    try:
        import fitz
        pdf_libs.append("PyMuPDF")
    except ImportError:
        pass
    
    try:
        import pdf2image
        pdf_libs.append("pdf2image")
    except ImportError:
        pass
    
    if not pdf_libs:
        st.info("For enhanced PDF OCR, install PyMuPDF: `pip install PyMuPDF` or pdf2image: `pip install pdf2image poppler-utils`")
    else:
        st.success(f"PDF OCR enabled using: {', '.join(pdf_libs)}")