from pydantic import BaseModel
from datetime import date


class Model1Base(BaseModel):
    name: str
    value: int


class Model1(Model1Base):
    date: date
