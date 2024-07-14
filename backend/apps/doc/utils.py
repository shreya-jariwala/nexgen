import pymupdf4llm
import fitz
import re

def convert_doc_to_markdown(uploaded_file, pages_list):
    """Converts a uploaded document to markdown.

    Args:
        uploaded_file: The uploaded PDF file object.
        pages_list: The desired page range (e.g., [1, 2, 3] or [1, 5]).

    Returns:
        The converted markdown text.
    """

    try:
        # Open the PDF file
        doc = fitz.open(stream=uploaded_file.read())

        md_text = ""
        for page_num in pages_list:
            page = doc[page_num]
            
            # Extract text in reading order
            blocks = page.get_text("blocks")

            # Iterate through text blocks
            for block in blocks:
                # Ignore empty blocks or blocks with only whitespace
                if not block[4].strip():
                    continue

                # Get the text from the block
                block_text = block[4].strip()

                # Add the text to the markdown string
                md_text += block_text + "\n"

        return md_text
    except Exception as e:
        raise(f"Error parsing document: {e}")

def get_page_range(page_range_str):
    """Validates a page range string with flexible formatting and returns a list of pages.

    Args:
        page_range_str: The page range string (e.g., '1 - 10', ' 5, 12', '10').

    Returns:
        A list of pages if valid, otherwise None.

    Raises:
        ValueError: If the page range is invalid.
    """

    match = re.search(r"^\s*(\d+)\s*([-,\s]+\s*(\d+)\s*)?$", page_range_str)
    if match:
        start_page = int(match.group(1))
        end_page = int(match.group(3)) if match.group(3) else start_page  # Handle single page case

        if start_page <= end_page:
            return list(range(start_page - 1, end_page))
        else:
            raise ValueError("Invalid page range: start page must be less than or equal to end page.")
    else:
        raise ValueError("Invalid page range format.") 
