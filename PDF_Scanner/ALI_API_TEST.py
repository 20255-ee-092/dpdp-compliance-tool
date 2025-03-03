import requests
import sys
import os

def upload_pdf(file_path):
    """
    Upload a PDF file to the document field extraction service.
    
    Args:
        file_path (str): Path to the PDF file to upload
    
    Returns:
        dict: The JSON response from the server
    """
    # Check if file exists
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None
    
    # URL for the API endpoint
    url = "https://doc-field-extraction.onrender.com/upload"
    
    # Prepare the file for upload
    with open(file_path, 'rb') as file:
        files = {'file': (os.path.basename(file_path), file, 'application/pdf')}
        print("files: ",files)
        # Send the POST request
        print(f"Uploading {file_path} to {url}...")
        response = requests.post(url, files=files)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Upload successful!")
        return response.json()
    else:
        print(f"Error: HTTP {response.status_code}")
        print(response.text)
        return None

if __name__ == "__main__":
    # If run from command line, get file path from arguments
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        result = upload_pdf(file_path)
        if result:
            print("Response:")
            print(result)
    else:
        print("Usage: python upload_pdf.py path/to/your/file.pdf")