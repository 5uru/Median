from fastapi import FastAPI
from pydantic import BaseModel

from app.database import (
    select_all_unique_flashcard_names,
    select_flashcard_by_name,
    update_flashcard_data,
)
from app.spaced_repetition import recall_prediction, update_model

app = FastAPI()


class Flashcard(BaseModel):
    name: str


class ModelData(BaseModel):
    model: str
    result: int
    total: int
    last_test: str


@app.get("/flashcards")
async def get_flashcards():
    return select_all_unique_flashcard_names()


@app.get("/flashcard/{name}")
async def get_flashcard(name: str):
    return select_flashcard_by_name(name)


@app.put("/flashcard")
async def update_flashcard(flashcard: Flashcard):
    return update_flashcard_data(flashcard.dict())


@app.get("/recall/{database}")
async def get_recall_prediction(database: str):
    return recall_prediction(database)


@app.put("/model")
async def update_recall_model(data: ModelData):
    new_model = update_model(data.model, data.result, data.total, data.last_test)
    return {"new_model": new_model}
