import google.generativeai as genai
import sys
import os
from PIL import Image
from pdf2image import convert_from_path

def check_poppler_installation():
    """Check if Poppler is properly installed and accessible."""
    try:
        # Try to convert a simple PDF - this will fail if Poppler is not installed
        convert_from_path(os.path.join(os.path.dirname(__file__), 'test.pdf'))
        return True
    except Exception as e:
        if 'poppler' in str(e).lower():
            print("\nError: Poppler is not installed or not in PATH!")
            print("\nTo use this script, please install Poppler:")
            print("1. Windows: Download from http://blog.alivate.com.au/poppler-windows/")
            print("2. Extract the downloaded file")
            print("3. Add the bin/ folder to your system PATH")
            print("\nAlternatively, you can use conda to install:")
            print("conda install -c conda-forge poppler")
        return False

def test_api_key(api_key):
    try:
        # Configure the Gemini API with your key
        genai.configure(api_key=api_key)
        
        # Try to get the available models as a simple test
        model_list = genai.list_models()
        
        # If we get here without an error, the key is working
        print("✓ API key is valid and working!")
        print("\nAvailable models:")
        for model in model_list:
            print(f"- {model.name}")
        return True
        
    except Exception as e:
        print("✗ API key validation failed!")
        print(f"Error: {str(e)}")
        return False

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using Gemini's vision capabilities."""
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Check Poppler installation first
        if not check_poppler_installation():
            return None
        
        # Convert PDF pages to images
        images = convert_from_path(pdf_path)
        
        # Configure Gemini vision model
        model = genai.GenerativeModel('gemini-pro-vision')
        
        # Process each page and extract text
        full_text = ""
        for i, image in enumerate(images):
            # Save the image temporarily
            temp_image_path = f"temp_page_{i}.png"
            image.save(temp_image_path)
            
            # Load image for Gemini
            img = Image.open(temp_image_path)
            
            # Extract text using Gemini vision
            response = model.generate_content(["Extract all text from this image", img])
            
            # Add extracted text
            full_text += response.text + "\n"
            
            # Clean up temporary file
            os.remove(temp_image_path)
        
        return full_text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return None

def analyze_text_with_gemini(api_key, text):
    """Analyze text using Gemini API."""
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)
        
        # Get the generative model
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate response
        response = model.generate_content(f"Please analyze this text and provide a summary:\n{text}")
        
        return response.text
    except Exception as e:
        print(f"Error analyzing text with Gemini: {str(e)}")
        return None

if __name__ == "__main__":
    # Your API key
    API_KEY = "AIzaSyADxNOa7VMVwtFmFbNO9kcgulsoiHJ8pVc"
    
    print("Testing Gemini API key...\n")
    if test_api_key(API_KEY):
        # If API key is valid, process PDF if provided
        if len(sys.argv) > 1:
            pdf_path = sys.argv[1]
            print(f"\nProcessing PDF: {pdf_path}")
            
            # Extract text from PDF
            extracted_text = extract_text_from_pdf(pdf_path)
            if extracted_text:
                print("\nExtracted text from PDF:")
                print("-" * 50)
                print(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
                print("-" * 50)
                
                # Analyze text with Gemini
                print("\nAnalyzing text with Gemini...")
                analysis = analyze_text_with_gemini(API_KEY, extracted_text)
                if analysis:
                    print("\nGemini Analysis:")
                    print("-" * 50)
                    print(analysis)
                    print("-" * 50)
        else:
            print("\nUsage: python test_gemini_api.py <path_to_pdf>")
            print("No PDF file provided. Only tested API key.")