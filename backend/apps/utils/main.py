import re

import re

def get_sanitized_filename(filename):
  """
  Cleans a filename for safe use with Python and SQLite3 and adds "mb_" prefix.

  Args:
      filename: The filename to be cleaned.

  Returns:
      A cleaned filename with "mb_" prefix, special characters removed,
      and spaces replaced with underscores.
  """

  # Delete numbers with brackets around it
  cleaned_filename = re.sub(r"\(\d\)", "", filename)

  # Remove all non-alphanumeric characters and underscores
  cleaned_filename = re.sub(r'[^\w_]', '_', cleaned_filename)

  # Replace multiple underscores with a single underscore
  cleaned_filename = re.sub(r'_+', '_', cleaned_filename)

  # Strip trailing underscore (if any)
  cleaned_filename = cleaned_filename.rstrip("_")

  # Add "mb_" prefix to the filename
  cleaned_filename = "sj_" + cleaned_filename + "_mb"

  return cleaned_filename.lower()  # Convert to lowercase for consistency

def get_page_range(page_range_str):
    """Validates a page range string with flexible formatting and returns the range.

    Args:
        page_range_str: The page range string (e.g., '1 - 10', ' 5, 12', '10').

    Returns:
        A tuple containing (start_page, end_page) if valid, otherwise None.

    Raises:
        ValueError: If the page range is invalid.
    """

    match = re.search(r"^\s*(\d+)\s*([-,\s]+\s*(\d+)\s*)?$", page_range_str)
    if match:
        start_page = int(match.group(1))
        end_page = int(match.group(3)) if match.group(3) else start_page  # Handle single page case

        if start_page <= end_page:
            return start_page, end_page
        else:
            raise ValueError("Invalid page range: start page must be less than or equal to end page.")
    else:
        raise ValueError("Invalid page range format.") 