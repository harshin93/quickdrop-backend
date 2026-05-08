import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from services.upload_service.app.core.security import get_current_user_id
from services.upload_service.app.core.storage import (
    get_file_stream_from_storage,
    upload_file_to_storage,
)
from services.upload_service.app.db.dependencies import get_db
from services.upload_service.app.models.file import FileMetadata

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/uploads", tags=["Uploads"])


def get_upload_file_size(file: UploadFile) -> int:
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    return file_size


@router.post("/")
def upload_file(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    logger.info(
        "Upload attempt user_id=%s filename=%s content_type=%s",
        user_id,
        file.filename,
        file.content_type,
    )

    if not file.filename:
        logger.warning("Upload failed: empty filename user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    try:
        file_size = get_upload_file_size(file)

        object_key = f"users/{user_id}/{uuid4()}-{file.filename}"

        upload_file_to_storage(
            file=file,
            object_key=object_key,
        )

        file_record = FileMetadata(
            user_id=user_id,
            filename=file.filename,
            file_path=object_key,
            content_type=file.content_type,
            file_size=file_size,
        )

        db.add(file_record)
        db.commit()
        db.refresh(file_record)

        logger.info(
            "Upload successful user_id=%s file_id=%s filename=%s file_size=%s object_key=%s",
            user_id,
            file_record.id,
            file_record.filename,
            file_record.file_size,
            file_record.file_path,
        )

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
            },
        }

    except SQLAlchemyError:
        db.rollback()
        logger.exception(
            "Upload failed: database error user_id=%s filename=%s",
            user_id,
            file.filename,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save file metadata",
        )

    except RuntimeError:
        logger.exception(
            "Upload failed: object storage error user_id=%s filename=%s",
            user_id,
            file.filename,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save file",
        )


@router.get("/")
def list_my_files(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    logger.info("List files request user_id=%s", user_id)

    try:
        files = (
            db.query(FileMetadata)
            .filter(FileMetadata.user_id == user_id)
            .order_by(FileMetadata.created_at.desc())
            .all()
        )

        logger.info(
            "List files successful user_id=%s count=%s",
            user_id,
            len(files),
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
            ],
        }

    except SQLAlchemyError:
        logger.exception("List files failed: database error user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve files",
        )


@router.get("/{file_id}")
def download_my_file(
    file_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    logger.info(
        "Download request user_id=%s file_id=%s",
        user_id,
        file_id,
    )

    try:
        file_record = (
            db.query(FileMetadata)
            .filter(
                FileMetadata.id == file_id,
                FileMetadata.user_id == user_id,
            )
            .first()
        )

        if file_record is None:
            logger.warning(
                "Download failed: file not found or unauthorized user_id=%s file_id=%s",
                user_id,
                file_id,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )

        file_stream = get_file_stream_from_storage(file_record.file_path)

        logger.info(
            "Download successful user_id=%s file_id=%s filename=%s object_key=%s",
            user_id,
            file_id,
            file_record.filename,
            file_record.file_path,
        )

        return StreamingResponse(
            file_stream.iter_chunks(chunk_size=8192),
            media_type=file_record.content_type or "application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{file_record.filename}"'
            },
        )

    except HTTPException:
        raise

    except FileNotFoundError:
        logger.exception(
            "Download failed: file missing from object storage user_id=%s file_id=%s object_key=%s",
            user_id,
            file_id,
            file_record.file_path if "file_record" in locals() else None,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File missing from storage",
        )

    except SQLAlchemyError:
        logger.exception(
            "Download failed: database error user_id=%s file_id=%s",
            user_id,
            file_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve file",
        )

    except RuntimeError:
        logger.exception(
            "Download failed: object storage error user_id=%s file_id=%s",
            user_id,
            file_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve file",
        )