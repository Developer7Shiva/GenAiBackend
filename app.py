from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import base64

app = Flask(__name__)

def extract_text_from_pdf_base64(base64_pdf):
    try:
        # Decode base64
        pdf_content = base64.b64decode(base64_pdf)

        # Open the PDF file from bytes
        pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
        text = ""

        # Iterate through each page
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()

        pdf_document.close()  # Close the PDF document
        return text

    except Exception as e:
        return str(e)

@app.route('/extract_text', methods=['POST'])
def extract_text():
    try:
        # Check if the POST request has JSON data
        if not request.json or 'base64_pdf' not in request.json:
            return jsonify({"error": "No valid JSON data or 'base64_pdf' field missing"})

        base64_pdf = request.json['base64_pdf']

        # Extract text from base64 PDF content
        extracted_text = extract_text_from_pdf_base64(base64_pdf)

        # Return the extracted text as JSON response
        return jsonify({"extracted_text": extracted_text})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
