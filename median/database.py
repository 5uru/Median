import sqlite3
from contextlib import contextmanager
from sqlite3 import Error

from median.utils import median_logger

DB_NAME = "flashcards.db"


@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        median_logger.info(f"Connected to {DB_NAME}")
        yield conn
    except Error as e:
        median_logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()
            median_logger.info(f"Connection to {DB_NAME} closed")


def create_table():
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute(
                """CREATE TABLE IF NOT EXISTS flashcards
                                 (id INTEGER PRIMARY KEY,
                                  question TEXT, 
                                  answer TEXT, 
                                  model TEXT, 
                                  lastTest TEXT,
                                  total INTEGER,  
                                  flashcardName TEXT)"""
            )
            median_logger.info("Table flashcards created")
        except Error as e:
            median_logger.error(f"Failed to create table: {e}")
            raise


def insert_flashcard_data(question, answer, model, last_test, total, flashcard_name):
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO flashcards(question, answer, model, lastTest, total, flashcardName) VALUES (?,?,?,?,?,?)",
                (question, answer, model, last_test, total, flashcard_name),
            )
            conn.commit()
            median_logger.info("Flashcard data inserted")
        except Error as e:
            median_logger.error(f"Failed to insert flashcard data: {e}")
            raise


def select_flashcard_by_name(flashcard_name):
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute(
                """
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY,
            flashcardName TEXT,
            question TEXT,
            answer TEXT,
            model TEXT,
            lastTest TEXT,
            total INTEGER
        )
    """
            )
            c.execute(
                "SELECT * FROM flashcards WHERE flashcardName = ?", (flashcard_name,)
            )
            median_logger.info(f"Selected flashcard by name: {flashcard_name}")
            return c.fetchall()
        except Error as e:
            median_logger.error(f"Failed to select flashcard by name: {e}")
            return []


def select_all_unique_flashcard_names():
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute(
                """
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY,
            flashcardName TEXT,
            question TEXT,
            answer TEXT,
            model TEXT,
            lastTest TEXT,
            total INTEGER
        )
    """
            )
            c.execute("SELECT DISTINCT flashcardName FROM flashcards")
            median_logger.info("Selected all unique flashcard names")
            return [i[0] for i in c.fetchall()]
        except Error as e:
            median_logger.error(f"Failed to select all unique flashcard names: {e}")
            return []


def update_flashcard_data(
    id_, question, answer, model, last_test, total, flashcard_name
):
    with get_db_connection() as conn:
        c = conn.cursor()
        try:
            c.execute(
                "UPDATE flashcards SET question = ?, answer = ?, model = ?, lastTest = ?, total = ?, flashcardName = ? WHERE id = ?",
                (question, answer, model, last_test, total, flashcard_name, id_),
            )
            conn.commit()
            median_logger.info("Flashcard data updated")
        except Error as e:
            median_logger.error(f"Failed to update flashcard data: {e}")
            raise
