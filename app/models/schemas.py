from pydantic import BaseModel


class QuestionResponse(BaseModel):
    question: str
    answer: str


class ProcessResponse(BaseModel):
    text_preview: str
    entities: list