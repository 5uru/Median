from langchain.docstore.document import Document as LangchainDocument

from median.llm_provider import generation
from median.utils import get_topics , language_detection , median_logger , split_documents
from median.validator import validate_json_data


def quiz(content):
    lang = language_detection(content)
    median_logger.info(f"Language detected: {lang}")
    topics = get_topics(content, lang, "fr_core_news_sm")
    median_logger.info(f"Key phrases: {topics}")
    corpus = [LangchainDocument(page_content=content.replace("\n\n", " "))]

    content_split = split_documents(4000, corpus)

    content_split = [doc.page_content for doc in content_split]

    all_quiz = []
    for doc in content_split:
        # Try to parse the JSON string
        median_logger.info(f"Generating quiz for: {doc}")
        doc_quiz = generation(doc, lang, " ,".join(topics))  # generate quiz
        median_logger.info(f"Generated quiz: {doc_quiz}")
        validation, json_object, error_message = validate_json_data(doc_quiz)
        if validation:
            all_quiz.append(json_object)
            median_logger.info(f"Quiz generated: {json_object}")
        else:
            median_logger.error(error_message)
            # repeat two more times
            for _ in range(2):
                median_logger.info(f"Regenerating {_} quiz for: {doc} ")
                doc_quiz = generation(doc, lang, " ,".join(topics))
                median_logger.info(f"Generated quiz: {doc_quiz}")
                try:
                    validation, json_object, error_message = validate_json_data(
                        doc_quiz
                    )
                    if validation:
                        all_quiz.append(json_object)
                        median_logger.info(f"Quiz generated: {json_object}")
                        break
                except Exception as e:
                    median_logger.error(f"Error: {e}")
                    continue
    quiz_list = []
    for quiz_content in all_quiz:
        for question in quiz_content["collection"]:
            quiz_list.append(question)
    return quiz_list, topics
