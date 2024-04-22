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

    # Regex patterns
    question_pattern = r'"question": "(.*?)"'
    answer_pattern = r'"answer": "(.*?)"'

    # Find questions and answers
    questions = re.findall(question_pattern , text)
    answers = re.findall(answer_pattern , text)

    # Create a collection of quizzes
    quizzes = [ { "question" : q , "answer" : a } for q , a in zip(questions , answers) ]

    # Return the collection of quizzes
    if questions and answers :
        return { "collection" : quizzes }
    else :
        return None


def validate_json_data(json_object) :
    """
    Validates JSON data by attempting to load it using json loads, ast.literal_eval, or extracting JSON-like structures.

    Args:
        json_object: The JSON object to validate.

    Returns:
        tuple: A tuple containing a boolean indicating validation success, the parsed JSON object, and an error message if validation fails.
    """

    valid = False
    error_message = None
    result_json = None

    try :
        # Attempt to load JSON using json.loads
        try :
            result_json = json.loads(json_object)
            median_logger.info(f"JSON data: {result_json} using json.loads")
        except json.decoder.JSONDecodeError :
            # If json.loads fails, try ast.literal_eval
            median_logger.error("Failed to load JSON data using json.loads")
            try :
                result_json = ast.literal_eval(json_object)
                median_logger.info(f"JSON data: {result_json} using ast.literal_eval")
            except (SyntaxError , ValueError) :
                # If both json.loads and ast.literal_eval fail, try extracting JSON-like structures
                median_logger.error("Failed to load JSON data using ast.literal_eval")
                try :
                    result_json = extract_json_from_markdown(json_object)
                except Exception as e :
                    error_message = f"JSON decoding error: {e}"
                    median_logger.error(error_message)
                    return valid , result_json , error_message

        # Return early if both json.loads and ast.literal_eval fail
        if result_json is None :
            error_message = "Failed to decode JSON data"
            median_logger.error(error_message)
            return valid , result_json , error_message
        else :
            median_logger.info(f"JSON data: {result_json}")
            # Validate each item in the list against schema if it's a list
            try :
                validate(instance=result_json , schema=json_schema)
                median_logger.info("Validation successful")
            except ValidationError as e :
                error_message = f"Validation failed: {e}"
                median_logger.error(error_message)

    except Exception as e :
        error_message = f"Error occurred: {e}"
        median_logger.error(error_message)

    if error_message is None :
        valid = True
        median_logger.info("Validation successful")
    else :
        median_logger.error("Validation failed")

    return valid , result_json , error_message
