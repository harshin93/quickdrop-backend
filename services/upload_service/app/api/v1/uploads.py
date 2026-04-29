import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from services.upload_service.app.core.security import get_current_user_id
from services.upload_service.app.db.dependencies import get_db
from services.upload_service.app.models.file import FileMetadata

router = APIRouter(prefix="/uploads", tags=["Uploads"])

UPLOAD_DIR = Path("services/upload_service/uploads")


@router.post("/")
def upload_file(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = file_path.stat().st_size
    file_record = FileMetadata(
    user_id=user_id,
    filename=file.filename,
    file_path=str(file_path),
    content_type=file.content_type,
    file_size=file_size,
)

    db.add(file_record)
    db.commit()
    db.refresh(file_record)

    return {
        "message": "File uploaded successfully",
        "file": {
            "id": file_record.id,
            "user_id": file_record.user_id,
            "filename": file_record.filename,
            "content_type": file_record.content_type,
            "file_size": file_record.file_size,
            "file_path": file_record.file_path,
            "created_at": file_record.created_at,
        }
    }