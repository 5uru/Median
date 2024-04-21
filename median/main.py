from fastapi import FastAPI
from pydantic import BaseModel

from median.app.database import (
    select_all_unique_flashcard_names ,
)
from median.app.generate_quizz import quiz

app = FastAPI( )


class Flashcard(BaseModel) :
    name: str


class ModelData(BaseModel) :
    model: str
    result: int
    total: int
    last_test: str


class QuizContent(BaseModel) :
    content: str


@app.get("/flashcards")
async def get_flashcards( ) -> list[ str ] :
    return select_all_unique_flashcard_names( )


@app.post("/generate_quiz")
async def generate_quiz(quiz_content: QuizContent) :
    quizzes , topics = quiz(quiz_content.content)
    return { "quizzes" : quizzes , "topics" : topics }
