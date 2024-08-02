from pydantic import BaseModel
from fastapi import Query
import markdown

def ResponseModel(BaseModel):
    id: int | None = None
    time_taken: str

def WebSearchResponseModel(ResponseModel):
    sources: list[dict]
    answer: markdown.Markdown | str
    related: list[str]

def ImageSearchResponseModel(ResponseModel):
    pass

def VideoSearchResponseModel(ResponseModel):
    pass