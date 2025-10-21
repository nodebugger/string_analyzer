from sqlmodel import SQLModel, Field, JSON
from datetime import datetime
from typing import Dict

class StringRecord(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True)
    value: str
    properties: dict = Field(sa_type=JSON, default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
