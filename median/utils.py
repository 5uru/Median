import datetime
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import List
from typing import Optional

import spacy
from langchain.docstore.document import Document as LangchainDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langdetect import detect
from pke.unsupervised import TopicRank
from spacy.language import Language
from transformers import AutoTokenizer

# Constants
EMBEDDING_MODEL_NAME = "thenlper/gte-small"
MARKDOWN_SEPARATORS = [
    "\n#{1,6} ",
    "```\n",
    "\n\\*\\*\\*+\n",
    "\n---+\n",
    "\n___+\n",
    "\n\n",
    "\n",
    " ",
    "",
]
SPACY_MODELS = {}


# Logging setup
def setup_logging():
    """Sets up logging configuration for the application.


    :returns: The configured logger object.

    :rtype: Logger

    """

    logging.basicConfig(
        format=
        "%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
        level=logging.INFO,
    )
    script_dir = os.path.dirname(os.path.abspath(__file__))
    now = datetime.datetime.now()
    log_folder = os.path.join(script_dir, "median_logs")
    os.makedirs(log_folder, exist_ok=True)
    log_file_path = os.path.join(
        log_folder,
        f"median_{now.strftime('%Y-%m-%d_%H-%M-%S')}.log",
    )
    file_handler = RotatingFileHandler(log_file_path,
                                       maxBytes=5 * 1024 * 1024,
                                       backupCount=5)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    logger = logging.getLogger("median")
    logger.addHandler(file_handler)
    return logger


median_logger = setup_logging()


# Utility Functions
def load_spacy_model(spacy_model: str) -> Language:
    """Loads a SpaCy language model and caches it for future use.

    :param spacy_model: The name of the SpaCy model to load.
    :type spacy_model: str
    :param spacy_model: str:
    :returns: The loaded SpaCy language model.
    :rtype: Language

    """

    if spacy_model not in SPACY_MODELS:
        try:
            SPACY_MODELS[spacy_model] = spacy.load(spacy_model)
            median_logger.info(f"Loaded SpaCy model: {spacy_model}")
        except Exception as e:
            median_logger.error(
                f"Error loading SpaCy model: {e}. Attempting to download.")
            spacy.cli.download(spacy_model)
            SPACY_MODELS[spacy_model] = spacy.load(spacy_model)
    return SPACY_MODELS[spacy_model]


def language_detection(content: str) -> str:
    """Detects the language of the provided content.

    :param content: The content for language detection.
    :type content: str
    :param content: str:
    :returns: The detected language.
    :rtype: str

    """

    return detect(content)


def get_topics(content: str,
               language: str,
               spacy_model: Optional[str] = "en_core_web_sm") -> List[str]:
    """Extracts key topics from the provided content using the specified language and SpaCy model.

    :param content: The content from which to extract key topics.
    :type content: str
    :param language: The language of the content.
    :type language: str
    :param spacy_model: The SpaCy model to use for topic extraction (default is "en_core_web_sm").
    :type spacy_model: Optional[str]
    :param content: str:
    :param language: str:
    :param spacy_model: Optional[str]:  (Default value = "en_core_web_sm")
    :returns: A list of key topics extracted from the content.
    :rtype: List[str]

    """

    nlp = load_spacy_model(spacy_model)
    extractor = TopicRank()
    extractor.load_document(content,
                            language=language,
                            spacy_model=nlp,
                            normalization="stemming")
    extractor.candidate_selection()
    extractor.candidate_weighting()
    key_phrases = extractor.get_n_best(n=5, stemming=False)
    median_logger.info(f"Extracted key phrases: {key_phrases}")
    return [candidate for (candidate, _) in key_phrases]


def split_documents(
    chunk_size: int,
    knowledge_base: List[LangchainDocument],
    tokenizer_name: Optional[str] = EMBEDDING_MODEL_NAME,
) -> List[LangchainDocument]:
    """Splits and deduplicates documents based on the specified chunk size and tokenizer.

    :param chunk_size: The size of each chunk for splitting the documents.
    :type chunk_size: int
    :param knowledge_base: The list of documents to split.
    :type knowledge_base: List[LangchainDocument]
    :param tokenizer_name: The name of the tokenizer to use (default is EMBEDDING_MODEL_NAME).
    :type tokenizer_name: Optional[str]
    :param chunk_size: int:
    :param knowledge_base: List[LangchainDocument]:
    :param tokenizer_name: Optional[str]:  (Default value = EMBEDDING_MODEL_NAME)
    :returns: The list of unique documents after splitting and deduplication.
    :rtype: List[LangchainDocument]

    """

    text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        AutoTokenizer.from_pretrained(tokenizer_name),
        chunk_size=chunk_size,
        chunk_overlap=chunk_size // 10,
        add_start_index=True,
        strip_whitespace=True,
        separators=MARKDOWN_SEPARATORS,
    )

    # Split and deduplicate documents
    docs_processed = text_splitter.split_documents(knowledge_base)
    unique_texts = set()
    docs_unique = [
        doc for doc in docs_processed
        if not (doc.page_content in unique_texts
                or unique_texts.add(doc.page_content))
    ]
    median_logger.info(
        f"Processed and deduplicated documents. Total unique chunks: {len(docs_unique)}."
    )
    return docs_unique
