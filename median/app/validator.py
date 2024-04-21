import ast
import json
import re
from typing import List

from jsonschema import validate
from pydantic import BaseModel , ValidationError

from median.app.utils import median_logger


class Quiz(BaseModel) :
    """
    A data model class representing a quiz with a question and an answer.
    """

    question: str
    answer: str


class QuizCollection(BaseModel) :
    """
    A data model class representing a collection of quizzes, where each quiz consists of a question and an answer.
    """

    collection: List[ Quiz ]


# serialize pydantic model into json schema
pydantic_schema = QuizCollection.schema_json( )
json_schema = json.loads(pydantic_schema)
median_logger.info(f"JSON schema: {json_schema}")


def extract_json_from_markdown(text) :
    """
    Extracts JSON-like dictionaries from a given text using regular expressions.

    Args:
        text (str): The text to extract JSON-like dictionaries from.

    Returns:
        List[dict]: A list of extracted dictionaries from the text.
    """

    # Regular expression pattern to match simple dictionary-like structures
    dict_pattern = r"\{[^\{\}]*\}"

    # Find all substrings that look like dictionaries
    potential_dicts = re.findall(dict_pattern , text)

    extracted_dicts = [ ]
    for d_str in potential_dicts :
        # Convert the string representation of dictionary to actual dictionary
        try :
            # Safe literal evaluation of dict string
            d = ast.literal_eval(d_str)
            if isinstance(d , dict) :  # Ensure it is a dictionary
                extracted_dicts.append(d)
                median_logger.info(f"Extracted dictionary: {d}")
        except (ValueError , SyntaxError) :
            # Skip if conversion fails
            median_logger.error(f"Failed to convert {d_str} to dictionary")

    return extracted_dicts


def load_json_data(json_object) :
    """
    Attempts to load JSON data using json.loads, ast.literal_eval, or extracting JSON-like structures.

    Args:
        json_object: The JSON object to load.

    Returns:
        tuple: A tuple containing the loaded JSON object and an error message if loading fails.
    """
    result_json = None
    error_message = None

    try :
        result_json = json.loads(json_object)
        median_logger.info(f"JSON data: {result_json} using json.loads")
    except json.decoder.JSONDecodeError :
        median_logger.error("Failed to load JSON data using json.loads")
        try :
            result_json = ast.literal_eval(json_object)
            median_logger.info(f"JSON data: {result_json} using ast.literal_eval")
        except (SyntaxError , ValueError) :
            median_logger.error("Failed to load JSON data using ast.literal_eval")
            try :
                result_json = extract_json_from_markdown(json_object)
            except Exception as e :
                error_message = f"JSON decoding error: {e}"
                median_logger.error(error_message)

    return result_json , error_message


def validate_json_against_schema(result_json) :
    """
    Validates JSON data against a schema.

    Args:
        result_json: The JSON object to validate.

    Returns:
        tuple: A tuple containing a boolean indicating validation success and an error message if validation fails.
    """
    valid = False
    error_message = None

    try :
        if isinstance(result_json , list) :
            median_logger.info("List found, validating each item")
            for index , item in enumerate(result_json) :
                validate(instance=item , schema=json_schema)
                median_logger.info(f"Validation successful for item {index + 1}")
        else :
            median_logger.info("No list found, validating without list")
            validate(instance=result_json , schema=json_schema)
            median_logger.info("Validation successful")
        valid = True
    except ValidationError as e :
        error_message = f"Validation failed: {e}"
        median_logger.error(error_message)

    return valid , error_message


def validate_json_data(json_object) :
    """
    Validates JSON data by attempting to load it and then validating it against a schema.

    Args:
        json_object: The JSON object to validate.

    Returns:
        tuple: A tuple containing a boolean indicating validation success, the parsed JSON object, and an error message if validation fails.
    """
    result_json , error_message = load_json_data(json_object)

    if error_message is not None :
        median_logger.error(error_message)
        return False , result_json , error_message

    valid , error_message = validate_json_against_schema(result_json)

    if error_message is not None :
        median_logger.error("Validation failed")
    else :
        median_logger.info("Validation successful")

    return valid , result_json , error_message
