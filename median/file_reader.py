import io

import PyPDF2
from docx import Document


def read_docx(docx_file):
    """
    Read the content of a DOCX file.

    :param docx_file: The path to the DOCX file or a file-like object.
    :return: The content of the DOCX file as a string.
    """
    if isinstance(docx_file, str):
        doc = Document(docx_file)
    else:
        doc = Document(io.BytesIO(docx_file.read()))
    content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return content


def read_pdf(pdf_file):
    """
    Read the content of a PDF file.

    :param pdf_file: The path to the PDF file or a file-like object.
    :return: The content of the PDF file as a string.
    """
    if isinstance(pdf_file, str):
        pdf_reader = PyPDF2.PdfReader(pdf_file)
    else:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))
    content = ""
    for page in range(len(pdf_reader.pages)):
        content += pdf_reader.pages[page].extract_text()
    return content


def main(file, file_type):
    """
    Read the content of a file based on its type.

    :param file: The file object or the file path.
    :param file_type: The MIME type of the file.
    :return: The content of the file as a string or None if the file type is not supported.
    """
    file_readers = {
        "text/markdown": lambda f: f.read().decode(),
        "application/pdf": read_pdf,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": read_docx,
        "text/plain": lambda f: f.read().decode(),
    }

    if file_type not in file_readers:
        raise ValueError(f"Unsupported file type: {file_type}")

    return file_readers[file_type](file)
