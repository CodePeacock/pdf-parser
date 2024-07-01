import pdfplumber


def extract_text(pdf_path):
    """Extracts text from a PDF file and returns it as a string with layout information.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text with layout information.

    Raises:
        Exception: If an error occurs during the extraction process.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""

            for page_num in range(len(pdf.pages)):
                page = pdf.pages[page_num]

                # Extract text with layout information
                text += page.extract_text()

        return text

    except Exception as e:
        print(f"Error: {e}")
        return None


print(extract_text("uploads/ABHAY-2.pdf"))
