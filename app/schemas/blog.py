from pydantic import BaseModel
from typing import Optional

class BlogPostBase(BaseModel):
    title: str
    content: str
    published: Optional[bool] = False

class BlogPostCreate(BlogPostBase):
    pass

class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None

class BlogPostRead(BlogPostBase):
    id: int
    author_id: int
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        orm_mode = True 