from backend.apps.doc.utils import parse_page_range_string
from backend.apps.doc.utils import convert_pdf_to_markdown
from backend.apps.doc.utils import convert_docx_to_markdown


def convert_document_to_markdown(uploaded_file, page_range_string):
    """Converts a document (PDF or DOCX) to markdown based on file type and page range.

    Args:
        uploaded_file: The uploaded file object.
        page_range_string: A string representing the desired page range (e.g., '1-10', '5,12', '10').

    Returns:
        The converted markdown text, or None if an error occurs or the file type is unsupported.
    """
    try:
        page_numbers = parse_page_range_string(page_range_string)
        file_extension = uploaded_file.name.lower().split('.')[-1]

        if file_extension == 'docx':
            print("docx returned")
            return convert_docx_to_markdown(uploaded_file)
        elif file_extension == 'pdf':
            print("pdf returned")
            return convert_pdf_to_markdown(uploaded_file, page_numbers)
        else:
            print(f"Unsupported file type: {file_extension}")
            return None
    except Exception as e:
        print(f"Error converting document: {e}")
        return None