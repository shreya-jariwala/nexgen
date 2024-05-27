from langchain.docstore.document import Document
import re
from lxml import etree

def build_rag_prompt(contexts, prompts):
    """
    This function takes two lists: contexts and prompts.
    It returns a list of dictionaries, where each dictionary represents a prompt with a context and a question.

    Args:
        contexts: A list of strings or Document objects representing the context for each prompt.
        prompts: A list of strings representing the questions.

    Returns:
        A list of dictionaries, where each dictionary has a 'context' key with a list of Document objects
        and a 'question' key with a string.
    """
    # Ensure that contexts is a list of Document objects
    if isinstance(contexts[0], str):
        contexts = [Document(page_content=c) for c in contexts]

    # Initialize an empty list to store the prompt dictionaries
    prompt_list = []

    # Iterate over contexts and prompts simultaneously
    for context, prompt in zip(contexts, prompts):
        # Create a dictionary with the context and the prompt
        prompt_dict = {"context": [context], "question": prompt}
        # Append the dictionary to the list
        prompt_list.append(prompt_dict)

    # Return the list of prompt dictionaries
    return prompt_list

def build_evaluation_prompt(prompts, xmls, contexts):
    """
    This function takes three lists: prompts, xmls, and contexts.
    It returns a list of dictionaries, where each dictionary represents an evaluation prompt with an input, a prediction, and a reference.

    Args:
        prompts: A list of strings representing the input for each prompt.
        xmls: A list of XML elements or strings representing the predictions.
        contexts: A list of strings representing the references or contexts.

    Returns:
        A list of dictionaries, where each dictionary has an 'input' key with a string,
        a 'prediction' key with a string (XML converted to string), and a 'reference' key with a string.
    """
    # Initialize an empty list to store the prompt dictionaries
    prompt_list = []

    # Iterate over prompts, xmls, and contexts simultaneously
    for prompt, xml, context in zip(prompts, xmls, contexts):
        # Convert the XML element to a string
        prediction = etree.tostring(xml, encoding='utf8').decode('utf8') if isinstance(xml, etree._Element) else xml
        # Create a dictionary with the prompt, prediction, and reference
        prompt_dict = {"reference": context, "prediction": prediction, "input": prompt}
        # Append the dictionary to the list
        prompt_list.append(prompt_dict)

    # Return the list of prompt dictionaries
    return prompt_list


def retrieve_context(text, start_char, end_char):
    """Retrieves context from text between start and end characters, ensuring all intermediate numbers are present.

    Args:
        text (str): The text to extract context from.
        start_char (int): The starting number.
        end_char (int): The ending number.

    Returns:
        str: The extracted context if all intermediate numbers are found, otherwise the original text.
    """

    # Ensure start and end characters are integers
    start_char = int(start_char)
    end_char = int(end_char)

    # Check if start and end characters are valid
    if start_char >= end_char:
        return text  # Invalid range, return original text

    # Build regular expressions for each number (1. 2. ... 10.)
    number_patterns = [rf"(?<!\S){num}\.\s*" for num in range(start_char, end_char + 1)]

    # Combine patterns into a single regex
    combined_pattern = r"|".join(number_patterns)

    # Find all occurrences of the numbers
    matches = re.findall(combined_pattern, text)

    # Check if all numbers are present
    if len(matches) == (end_char - start_char + 1):
        # All numbers found, extract context
        start_index = re.search(rf"(?<!\S){start_char}\.\s*", text).start()
        end_index = re.search(rf"(?<!\S){end_char}\.\s*", text).end()
        return text[start_index:end_index + 500]  # Adjust +500 as needed
    else:
        # Some numbers missing, return original text
        return text