"""S3 service for downloading audio files."""

import logging
import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class S3Service:
    """Service for S3/MinIO file operations."""

    def __init__(self):
        """Initialize the S3 service with credentials from settings."""
        settings = get_settings()
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
        )
        self._bucket = settings.s3_bucket_name
        logger.info(f"S3Service initialized for bucket: {self._bucket}")

    def download_file(self, s3_key: str, local_path: str) -> str:
        """Download a file from S3 to a local path.

        Args:
            s3_key: The S3 object key.
            local_path: The local file path to save to.

        Returns:
            The local file path.

        Raises:
            ClientError: If the download fails.
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        logger.info(f"Downloading s3://{self._bucket}/{s3_key} to {local_path}")
        try:
            self._client.download_file(self._bucket, s3_key, local_path)
            logger.info(f"Download complete: {local_path}")
            return local_path
        except ClientError as e:
            logger.error(f"Failed to download file: {e}")
            raise

    def file_exists(self, s3_key: str) -> bool:
        """Check if a file exists in S3.

        Args:
            s3_key: The S3 object key.

        Returns:
            True if the file exists, False otherwise.
        """
        try:
            self._client.head_object(Bucket=self._bucket, Key=s3_key)
            return True
        except ClientError:
            return False

    def get_file_size(self, s3_key: str) -> Optional[int]:
        """Get the size of a file in S3.

        Args:
            s3_key: The S3 object key.

        Returns:
            File size in bytes, or None if file doesn't exist.
        """
        try:
            response = self._client.head_object(Bucket=self._bucket, Key=s3_key)
            return response["ContentLength"]
        except ClientError:
            return None
