from docx import Document

def parse_docx(docx_file, start_page, end_page):
    """
    Extracts text from a docx file from a specific page range.

    Args:
        docx_file (str): Path to the docx file.
        start_page (int): Starting page number (1-based).
        end_page (int): Ending page number (1-based).

    Returns:
        str: Extracted text from the specified page range.
    """

    document = Document(docx_file)

    text = ""
    # Loop through paragraphs from desired pages
    for page in document.paragraphs[start_page - 1:end_page]:
        text += page.text.strip() + "\n"  # Add newline between paragraphs

    return text