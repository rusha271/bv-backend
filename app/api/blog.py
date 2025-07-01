from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.blog import BlogPost
from app.schemas.blog import BlogPostCreate, BlogPostUpdate, BlogPostRead
from app.core.security import get_current_user, require_role

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/blog", response_model=list[BlogPostRead])
def list_blog_posts(db: Session = Depends(get_db)):
    return db.query(BlogPost).filter(BlogPost.published == True).all()

@router.post("/blog", response_model=BlogPostRead, dependencies=[Depends(require_role("admin"))])
def create_blog_post(post: BlogPostCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    blog = BlogPost(**post.dict(), author_id=int(current_user.sub))
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog

@router.put("/blog/{id}", response_model=BlogPostRead, dependencies=[Depends(require_role("admin"))])
def update_blog_post(id: int, post: BlogPostUpdate, db: Session = Depends(get_db)):
    blog = db.query(BlogPost).filter(BlogPost.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog post not found")
    for field, value in post.dict(exclude_unset=True).items():
        setattr(blog, field, value)
    db.commit()
    db.refresh(blog)
    return blog

@router.delete("/blog/{id}", dependencies=[Depends(require_role("admin"))])
def delete_blog_post(id: int, db: Session = Depends(get_db)):
    blog = db.query(BlogPost).filter(BlogPost.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog post not found")
    db.delete(blog)
    db.commit()
    return {"ok": True} 