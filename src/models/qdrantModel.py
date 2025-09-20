from pydantic import BaseModel


class NameCollection(BaseModel):
    name_collection: str
    
class DocumentCreate(BaseModel):
    title: str
    description: str