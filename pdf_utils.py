"""
Contains high level functions for PDF conversion.

List of functions:
- extract_text_line_by_line(pdf_path: str) -> list: Extracts text from a PDF file and returns it as a list of lines.
- extract_with_unstructured(pdf_path: str) -> str: Extracts text from a PDF using an unstructured approach.

"""

import re

import pytesseract
from pdf2image import convert_from_path
from pdfminer.high_level import extract_text
from unstructured.partition.pdf import partition_pdf  # type: ignore


def extract_text_line_by_line(pdf_path: str) -> list[str] | None:
    """
    Extracts text from a PDF file and returns it as a list of lines.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        list[str] | None: A list of text lines extracted from the PDF file, or None if an error occurs.
    """
    try:
        text = extract_text(pdf_path)

        if not text.strip():
            text = extract_with_unstructured(pdf_path)

        lines = text.split("\n")
        return [re.sub(r"\s+", " ", line).strip() for line in lines if line.strip()]
    except Exception as e:
        print(f"Error: {e}")
        return None


def extract_with_unstructured(pdf_path: str) -> str:
    """
    Extracts text from a PDF file using an unstructured approach.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF file.
    """
    elements = partition_pdf(
        pdf_path,
        include_page_breaks=True,
        hi_res_model_name="yolox",
        strategy="hi_res",
        infer_table_structure=True,
        languages=["eng"],
    )
    text: str = "\n\n".join(str(el) for el in elements)
    return text


# text = extract_with_unstructured("AAi Div.pdf")
# # Save the text in a text file
# with open("extracted_text.txt", "w") as text_file:
#     text_file.write(text)


def extract_with_pytesseract(pdf_path: str) -> str:
    """
    Extracts text from a PDF file using PyTesseract.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF file.
    """
    images = convert_from_path(pdf_path)
    return "".join(
        pytesseract.image_to_string(image, config="--psm 6") for image in images
    )


pytesseract_text = extract_with_pytesseract("AAi Div.pdf")
# Save the text in a text file
with open("pytesseract_text.txt", "w") as text_file:
    text_file.write(pytesseract_text)
