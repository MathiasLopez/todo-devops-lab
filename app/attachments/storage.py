# attachments/storage.py
import logging
import os
import boto3
from botocore.client import Config

logger = logging.getLogger(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_PUBLIC_URL = os.getenv("MINIO_PUBLIC_URL", MINIO_ENDPOINT)
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "attachments")

_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
)

# Separate client for presigned URLs — signed with the public host so the
# signature matches when the browser resolves the URL from outside Docker.
_public_client = boto3.client(
    "s3",
    endpoint_url=MINIO_PUBLIC_URL,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
)


def ensure_bucket() -> None:
    """Create the bucket if it doesn't exist. Called once at app startup."""
    try:
        _client.head_bucket(Bucket=MINIO_BUCKET)
    except Exception:
        try:
            _client.create_bucket(Bucket=MINIO_BUCKET)
            logger.info("Created MinIO bucket: %s", MINIO_BUCKET)
        except Exception:
            logger.exception("Failed to create MinIO bucket '%s' — uploads will fail", MINIO_BUCKET)


def upload_file(file_obj, key: str, content_type: str) -> None:
    _client.upload_fileobj(
        file_obj,
        MINIO_BUCKET,
        key,
        ExtraArgs={"ContentType": content_type},
    )


def generate_presigned_url(key: str, filename: str, expiry_seconds: int = 900) -> str:
    return _public_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": MINIO_BUCKET,
            "Key": key,
            "ResponseContentDisposition": f'attachment; filename="{filename}"',
        },
        ExpiresIn=expiry_seconds,
    )


def delete_file(key: str) -> None:
    _client.delete_object(Bucket=MINIO_BUCKET, Key=key)
