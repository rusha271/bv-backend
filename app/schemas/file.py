from pydantic import BaseModel
from typing import Optional

class FileBase(BaseModel):
    filename: str
    content_type: str
    size: int
    path: str

class FileCreate(FileBase):
    pass

class FileRead(FileBase):
    id: int
    user_id: int
    created_at: Optional[str]

    class Config:
        from_attributes = True 