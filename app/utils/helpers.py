from slugify import slugify
from fastapi import UploadFile, HTTPException

ALLOWED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/jpg"]
MAX_FILE_SIZE_MB = 10

def generate_slug(text: str) -> str:
    return slugify(text)

def validate_file_upload(file: UploadFile):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type.")
    file.file.seek(0, 2)  # Seek to end
    size = file.file.tell()
    file.file.seek(0)
    if size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10MB).") 