"""S3 service for file upload operations."""

import boto3
from botocore.exceptions import ClientError

from app.core.config import Settings

ALLOWED_CONTENT_TYPES = [
    "audio/mpeg",      # .mp3
    "audio/wav",       # .wav
    "audio/mp4",       # .m4a
    "audio/webm",      # .webm
    "audio/ogg",       # .ogg
    "audio/x-m4a",     # .m4a alternate
]


class S3Service:
    """Service for S3 file operations."""

    def __init__(self, settings: Settings):
        """Initialize S3 client with credentials from settings."""
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        self.bucket_name = settings.s3_bucket_name

    def generate_presigned_upload_url(
        self, object_key: str, content_type: str, expiration: int = 3600
    ) -> str:
        """Generate a presigned URL for PUT operation.

        Args:
            object_key: The S3 object key (path) for the file.
            content_type: MIME type of the file to upload.
            expiration: URL expiration time in seconds (default: 1 hour).

        Returns:
            Presigned URL string for uploading the file.

        Raises:
            ClientError: If S3 operation fails.
        """
        return self.client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": object_key,
                "ContentType": content_type,
            },
            ExpiresIn=expiration,
        )

    def delete_file(self, object_key: str) -> None:
        """Delete a file from S3.

        Args:
            object_key: The S3 object key (path) to delete.

        Raises:
            ClientError: If S3 operation fails.
        """
        self.client.delete_object(Bucket=self.bucket_name, Key=object_key)
