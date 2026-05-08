import logging

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import UploadFile

from services.upload_service.app.core.config import settings

logger = logging.getLogger(__name__)


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region_name,
        config=Config(signature_version="s3v4"),
    )


def upload_file_to_storage(file: UploadFile, object_key: str) -> None:
    s3_client = get_s3_client()

    try:
        file.file.seek(0)

        s3_client.upload_fileobj(
            Fileobj=file.file,
            Bucket=settings.s3_bucket_name,
            Key=object_key,
            ExtraArgs={
                "ContentType": file.content_type or "application/octet-stream"
            },
        )

        logger.info(
            "File uploaded to object storage bucket=%s object_key=%s",
            settings.s3_bucket_name,
            object_key,
        )

    except ClientError as exc:
        logger.exception(
            "Object storage upload failed bucket=%s object_key=%s",
            settings.s3_bucket_name,
            object_key,
        )
        raise RuntimeError("Could not upload file to object storage") from exc


def get_file_stream_from_storage(object_key: str):
    s3_client = get_s3_client()

    try:
        response = s3_client.get_object(
            Bucket=settings.s3_bucket_name,
            Key=object_key,
        )

        logger.info(
            "File retrieved from object storage bucket=%s object_key=%s",
            settings.s3_bucket_name,
            object_key,
        )

        return response["Body"]

    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code")

        if error_code in ("NoSuchKey", "404"):
            logger.warning(
                "Object not found in storage bucket=%s object_key=%s",
                settings.s3_bucket_name,
                object_key,
            )
            raise FileNotFoundError("File missing from object storage") from exc

        logger.exception(
            "Object storage download failed bucket=%s object_key=%s",
            settings.s3_bucket_name,
            object_key,
        )
        raise RuntimeError("Could not retrieve file from object storage") from exc