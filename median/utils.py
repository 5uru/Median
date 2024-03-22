import datetime
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import List, Optional

import spacy
from langchain.docstore.document import Document as LangchainDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langdetect import detect
from pke.unsupervised import TopicRank
from transformers import AutoTokenizer

logging.basicConfig(
    format="%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
)
script_dir = os.path.dirname(os.path.abspath(__file__))
now = datetime.datetime.now()
log_folder = os.path.join(script_dir, "median_logs")
os.makedirs(log_folder, exist_ok=True)
log_file_path = os.path.join(
    log_folder,
    f"function-calling-median_{ now.strftime('%Y-%m-%d_%H-%M-%S') }.log",
)
# Use RotatingFileHandler from the logging.handlers module
file_handler = RotatingFileHandler(log_file_path, maxBytes=0, backupCount=0)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
)
file_handler.setFormatter(formatter)

median_logger = logging.getLogger("function-calling-median")
median_logger.addHandler(file_handler)


def language_detection(content):
    return detect(content)


def get_topics(content, language, spacy_model: Optional[str] = "en_core_web_sm"):
    # Load the SpaCy model
    nlp = spacy.load(spacy_model)
    median_logger.info(f"Loaded SpaCy model: {spacy_model}")
    # Create a TopicRank extractor
    extractor = TopicRank()
    # Load the content of the document
    extractor.load_document(
        content.replace("\n", " "),
        language=language,
        spacy_model=nlp,  # Pass the loaded SpaCy model
        normalization="stemming",
    )

    # Select the key phrase candidates
    extractor.candidate_selection()

    # Weight the candidates
    extractor.candidate_weighting()

    # The n-highest (5) scored candidates
    key_phrases = extractor.get_n_best(n=5, stemming=False)
    median_logger.info(f"Key phrases: {key_phrases}")
    return [candidate for (candidate, _) in key_phrases]


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


def split_documents(
    chunk_size: int,
    knowledge_base: List[LangchainDocument],
    tokenizer_name: Optional[str] = EMBEDDING_MODEL_NAME,
) -> List[LangchainDocument]:
    """
    Split documents into chunks of maximum size `chunk_size` tokens and return a list of documents.
    """
    text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        AutoTokenizer.from_pretrained(tokenizer_name),
        chunk_size=chunk_size,
        chunk_overlap=chunk_size // 10,
        add_start_index=True,
        strip_whitespace=True,
        separators=MARKDOWN_SEPARATORS,
    )

    # Split documents
    docs_processed = []
    for doc in knowledge_base:
        docs_processed += text_splitter.split_documents([doc])
    median_logger.info(f"Split documents into {len(docs_processed)} chunks")
    # Remove duplicates
    unique_texts = {}
    docs_processed_unique = []
    for doc in docs_processed:
        if doc.page_content not in unique_texts:
            unique_texts[doc.page_content] = True
            docs_processed_unique.append(doc)
    median_logger.info("Removed duplicates")
    return docs_processed_unique
