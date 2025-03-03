from re import S
from pydantic import BaseModel
from typing import Optional,List

class Document(BaseModel):
    id: Optional[int]= None
    title: str
    content: str
    category: Optional[str] = None

class SearchQuery(BaseModel):
    text: str
    limit: int = 5

class UpdateDocument(BaseModel):
    title:Optional[str]= None
    content: Optional[str]= None
    category :Optional[str]= None
