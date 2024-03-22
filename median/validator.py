import ast
import json
import re
from typing import List

from jsonschema import validate
from pydantic import BaseModel, ValidationError

from median.utils import median_logger


class Quiz(BaseModel):
    question: str
    answer: str


class QuizCollection(BaseModel):
    collection: List[Quiz]


# serialize pydantic model into json schema
pydantic_schema = QuizCollection.schema_json()
json_schema = json.loads(pydantic_schema)
median_logger.info(f"JSON schema: {json_schema}")


def extract_json_from_markdown(text):
    # Regular expression pattern to match simple dictionary-like structures
    dict_pattern = r"\{[^\{\}]*\}"

    # Find all substrings that look like dictionaries
    potential_dicts = re.findall(dict_pattern, text)

    extracted_dicts = []
    for d_str in potential_dicts:
        # Convert the string representation of dictionary to actual dictionary
        try:
            # Safe literal evaluation of dict string
            d = ast.literal_eval(d_str)
            if isinstance(d, dict):  # Ensure it is a dictionary
                extracted_dicts.append(d)
                median_logger.info(f"Extracted dictionary: {d}")
        except (ValueError, SyntaxError):
            # Skip if conversion fails
            median_logger.error(f"Failed to convert {d_str} to dictionary")

    return extracted_dicts


def validate_json_data(json_object):
    valid = False
    error_message = None
    result_json = None

    try:
        # Attempt to load JSON using json.loads
        try:
            result_json = json.loads(json_object)
            median_logger.info(f"JSON data: {result_json} using json.loads")
        except json.decoder.JSONDecodeError:
            # If json.loads fails, try ast.literal_eval
            median_logger.error("Failed to load JSON data using json.loads")
            try:
                result_json = ast.literal_eval(json_object)
                median_logger.info(f"JSON data: {result_json} using ast.literal_eval")
            except (SyntaxError, ValueError):
                # If both json.loads and ast.literal_eval fail, try extracting JSON-like structures
                median_logger.error("Failed to load JSON data using ast.literal_eval")
                try:
                    result_json = extract_json_from_markdown(json_object)
                except Exception as e:
                    error_message = f"JSON decoding error: {e}"
                    median_logger.error(error_message)
                    return valid, result_json, error_message

        # Return early if both json.loads and ast.literal_eval fail
        if result_json is None:
            error_message = "Failed to decode JSON data"
            median_logger.error(error_message)
            return valid, result_json, error_message
        else:
            median_logger.info(f"JSON data: {result_json}")
        # Validate each item in the list against schema if it's a list
        if isinstance(result_json, list):
            median_logger.info("List found, validating each item")
            for index, item in enumerate(result_json):
                try:
                    validate(instance=item, schema=json_schema)
                    median_logger.info(f"Validation successful for item {index + 1}")
                except ValidationError as e:
                    error_message = f"""Validation failed for item {
                        index + 1
                    }: {e}"""
                    median_logger.error(error_message)
                    break
        else:
            # Default to validation without list
            median_logger.info("No list found, validating without list")
            try:
                validate(instance=result_json, schema=json_schema)
                median_logger.info("Validation successful")
            except ValidationError as e:
                error_message = f"Validation failed: {e}"
                median_logger.error(error_message)

    except Exception as e:
        error_message = f"Error occurred: {e}"
        median_logger.error(error_message)

    if error_message is None:
        valid = True
        median_logger.info("Validation successful")
    else:
        median_logger.error("Validation failed")

    return valid, result_json, error_message
