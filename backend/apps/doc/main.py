from backend.apps.doc.utils import convert_doc_to_markdown
from backend.apps.doc.utils import get_page_range

def convert_document(uploaded_file, target_pages):

    """Converts an uploaded document to markdown.

    Args:
        uploaded_file: The uploaded PDF file object.
        page_range: The desired page range (e.g., '1-10', '5,12', '10').

    Returns:
        The converted markdown text or None if an error occurred.
    """

    pages_list = get_page_range(target_pages)

    converted_document = convert_doc_to_markdown(uploaded_file, pages_list)

    return converted_document
