from pydantic import BaseModel, Field


class NameCollection(BaseModel):
    name_collection: str

class DocumentCreate(BaseModel):
    title: str
    description: str

class DocumentSearch(BaseModel):
    query: str
    limit: int = Field(default=2, ge=1)