import sqlite3
from contextlib import contextmanager
from datetime import datetime
from sqlite3 import Error

from median.app.utils import median_logger

DB_NAME = "flashcards.db"


@contextmanager
def get_db_connection( ) :
    """
    Context manager to establish a connection to the database.

    Yields:
        Connection: A connection to the database.

    Raises:
        Error: If there is a database error.
    """
    conn = None
    try :
        conn = sqlite3.connect(DB_NAME)
        median_logger.info(f"Connected to {DB_NAME}")
        yield conn
    except Error as e :
        median_logger.error(f"Database error: {e}")
        raise
    finally :
        if conn :
            conn.close( )
            median_logger.info(f"Connection to {DB_NAME} closed")


def create_table( ) :
    """
    Creates a table in the database.

    Returns:
        None
    """

    with get_db_connection( ) as conn :
        c = conn.cursor( )
        try :
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
        except Error as e :
            median_logger.error(f"Failed to create table: {e}")
            raise


def insert_flashcard_data(
        question: str ,
        answer: str ,
        model: str ,
        last_test: datetime ,
        total: int ,
        flashcard_name: str ,
) :
    """
    Inserts flashcard data into the 'flashcards' table in the database.

    Args:
        question (str): The question for the flashcard.
        answer (str): The answer for the flashcard.
        model (str): The model associated with the flashcard.
        last_test (datetime): The date of the last test for the flashcard.
        total (int): The total number of tests taken for the flashcard.
        flashcard_name (str): The name of the flashcard.

    Returns:
        None

    Raises:
        Error: If there is an error inserting the flashcard data.
    """

    with get_db_connection( ) as conn :
        c = conn.cursor( )
        try :
            c.execute(
                    "INSERT INTO flashcards(question, answer, model, lastTest, total, flashcardName) VALUES (?,?,?,?,?,?)" ,
                    (question , answer , model , last_test , total , flashcard_name) ,
            )
            conn.commit( )
            median_logger.info("Flashcard data inserted")
        except Error as e :
            median_logger.error(f"Failed to insert flashcard data: {e}")
            raise


def select_flashcard_by_name(flashcard_name: str) -> list[ tuple ] :
    """
    Selects flashcard data from the 'flashcards' table in the database based on the flashcard name.

    Args:
        flashcard_name (str): The name of the flashcard to select.

    Returns:
        list[tuple]: A list of tuples containing the selected flashcard data.

    Raises:
        None
    """

    with get_db_connection( ) as conn :
        c = conn.cursor( )
        try :
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
                    "SELECT * FROM flashcards WHERE flashcardName = ?" , (flashcard_name ,)
            )
            median_logger.info(f"Selected flashcard by name: {flashcard_name}")
            return c.fetchall( )
        except Error as e :
            median_logger.error(f"Failed to select flashcard by name: {e}")
            return [ ]


def select_all_unique_flashcard_names( ) -> list[ str ] :
    """
    Selects all unique flashcard names from the 'flashcards' table in the database.

    Returns:
        list[str]: A list of unique flashcard names.

    Raises:
        None
    """

    with get_db_connection( ) as conn :
        c = conn.cursor( )
        try :
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
            return [ i[ 0 ] for i in c.fetchall( ) ]
        except Error as e :
            median_logger.error(f"Failed to select all unique flashcard names: {e}")
            return [ ]


def update_flashcard_data(
        id_: int ,
        question: str ,
        answer: str ,
        model: str ,
        last_test: datetime ,
        total: int ,
        flashcard_name: str ,
) :
    """
    Updates the data of a flashcard in the 'flashcards' table in the database.

    Args:
        id_ (int): The ID of the flashcard to update.
        question (str): The updated question for the flashcard.
        answer (str): The updated answer for the flashcard.
        model (str): The updated model associated with the flashcard.
        last_test (datetime): The updated date of the last test for the flashcard.
        total (int): The updated total number of tests taken for the flashcard.
        flashcard_name (str): The updated name of the flashcard.

    Returns:
        None

    Raises:
        Error: If there is an error updating the flashcard data.
    """

    with get_db_connection( ) as conn :
        c = conn.cursor( )
        try :
            c.execute(
                    "UPDATE flashcards SET question = ?, answer = ?, model = ?, lastTest = ?, total = ?, flashcardName = ? WHERE id = ?" ,
                    (question , answer , model , last_test , total , flashcard_name , id_) ,
            )
            conn.commit( )
            median_logger.info("Flashcard data updated")
        except Error as e :
            median_logger.error(f"Failed to update flashcard data: {e}")
            raise
