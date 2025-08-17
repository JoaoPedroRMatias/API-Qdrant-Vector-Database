from pydantic import BaseModel


class NameCollection(BaseModel):
    name_collection: str
    