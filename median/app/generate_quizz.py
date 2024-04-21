from langchain.docstore.document import Document as LangchainDocument

from median.app.llm_provider import generation
from median.app.utils import (
    get_topics ,
    language_detection ,
    median_logger ,
    split_documents ,
)
from median.app.validator import validate_json_data


def generate_quiz_for_doc(doc: str , lang: str , topics: list[ str ]) :
    """
    Generates a quiz based on a document, language, and topics.

    Args:
        doc (str): The document for which the quiz is generated.
        lang (str): The language for the quiz.
        topics (list[str]): The topics to include in the quiz.

    Returns:
        dict: The generated quiz data in JSON format.

    Raises:
        ValueError: If a valid quiz cannot be generated after 3 attempts.
    """

    median_logger.info(f"Generating quiz for: {doc}")
    for attempt in range(3) :
        quiz_data = generation(doc , lang , " ,".join(topics))
        median_logger.info(f"Attempt {attempt + 1}, generated quiz: {quiz_data}")
        valid , quiz_json , error = validate_json_data(quiz_data)
        if valid :
            return quiz_json
        median_logger.error(f"Validation failed: {error}")
    raise ValueError("Failed to generate valid quiz after 3 attempts.")


def quiz(content: str) :
    """
    Generates quizzes based on the content provided.

    Args:
        content (str): The content for which quizzes are generated.

    Returns:
        tuple: A tuple containing the list of generated quizzes and the topics extracted from the content.
    """

    lang = language_detection(content)
    spacy_model = "fr_core_news_sm" if lang == "fr" else "en_core_web_sm"
    topics = get_topics(content , lang , spacy_model)

    corpus = [ LangchainDocument(page_content=content.replace("\n\n" , " ")) ]
    content_split = split_documents(4000 , corpus)
    content_formatted = [ doc.page_content for doc in content_split ]

    generated_quizzes = [
            generate_quiz_for_doc(doc , lang , topics) for doc in content_formatted if doc
    ]

    quiz_list = [
            q for quiz_content in generated_quizzes for q in quiz_content[ "collection" ]
    ]
    return quiz_list , topics
