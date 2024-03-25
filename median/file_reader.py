import PyPDF2
from docx import Document


def read_docx(docx_file):
    """

    :param docx_file: 

    """
    # Create a Document object
    doc = Document(docx_file)
    # Extract the text
    content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return content


def read_pdf(pdf_path):
    """

    :param pdf_path: 

    """
    # Read the PDF file
    pdf_reader = PyPDF2.PdfFileReader(pdf_path)
    # Extract the content
    content = ""
    for page in range(pdf_reader.getNumPages()):
        content += pdf_reader.getPage(page).extractText()

    return content


def main(file, file_type):
    """

    :param file: param file_type:
    :param file_type: 

    """
    if file_type == "text/markdown":
        return file.read().decode()
    elif file_type == "application/pdf":
        return read_pdf(file)
    elif (
        file_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        return read_docx(file)
    elif file_type == "text/plain":
        return file.read().decode()
    else:
        return None
