import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
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


@router.get("/")
def list_my_files(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    files = (
        db.query(FileMetadata)
        .filter(FileMetadata.user_id == user_id)
        .order_by(FileMetadata.created_at.desc())
        .all()
    )

    return {
        "message": "Files retrieved successfully",
        "count": len(files),
        "files": [
            {
                "id": file.id,
                "user_id": file.user_id,
                "filename": file.filename,
                "content_type": file.content_type,
                "file_size": file.file_size,
                "file_path": file.file_path,
                "created_at": file.created_at,
            }
            for file in files
        ]
    }


@router.get("/{file_id}")
def download_my_file(
    file_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    file_record = (
        db.query(FileMetadata)
        .filter(
            FileMetadata.id == file_id,
            FileMetadata.user_id == user_id
        )
        .first()
    )

    if file_record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_path = Path(file_record.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File missing from storage"
        )

    return FileResponse(
        path=file_path,
        filename=file_record.filename,
        media_type=file_record.content_type or "application/octet-stream"
    )