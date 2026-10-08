"""
Cloudflare R2 Storage Service.

Handles document upload, download, deletion, and object existence checks.
Cloudflare R2 is S3-compatible, so boto3 is used as the client.
"""

import os
from typing import BinaryIO, Optional

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


class R2Storage:
    """Service for interacting with Cloudflare R2 object storage."""

    def __init__(self):
        self.account_id = os.getenv("R2_ACCOUNT_ID")
        self.access_key_id = os.getenv("R2_ACCESS_KEY_ID")
        self.secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY")
        self.bucket_name = os.getenv("R2_BUCKET_NAME")

        # Use explicit endpoint if provided, otherwise build it
        self.endpoint_url = os.getenv(
            "R2_ENDPOINT",
            f"https://{self.account_id}.r2.cloudflarestorage.com",
        )

        self._validate_configuration()

        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name="auto",
        )

    def _validate_configuration(self) -> None:
        """Validate required R2 environment variables."""

        required_variables = {
            "R2_ACCOUNT_ID": self.account_id,
            "R2_ACCESS_KEY_ID": self.access_key_id,
            "R2_SECRET_ACCESS_KEY": self.secret_access_key,
            "R2_BUCKET_NAME": self.bucket_name,
        }

        missing = [
            name
            for name, value in required_variables.items()
            if not value
        ]

        if missing:
            raise RuntimeError(
                "Missing required R2 environment variables: "
                + ", ".join(missing)
            )

    def upload_file(
        self,
        file_obj: BinaryIO,
        object_key: str,
        content_type: Optional[str] = None,
    ) -> str:
        """
        Upload a file to Cloudflare R2.

        Returns:
            The object key stored in R2.
        """

        extra_args = {}

        if content_type:
            extra_args["ContentType"] = content_type

        try:
            self.client.upload_fileobj(
                Fileobj=file_obj,
                Bucket=self.bucket_name,
                Key=object_key,
                ExtraArgs=extra_args,
            )

            return object_key

        except ClientError as error:
            raise RuntimeError(
                f"Failed to upload file to R2: {error}"
            ) from error

    def download_file(self, object_key: str) -> bytes:
        """Download a file from R2."""

        try:
            response = self.client.get_object(
                Bucket=self.bucket_name,
                Key=object_key,
            )

            return response["Body"].read()

        except ClientError as error:
            raise RuntimeError(
                f"Failed to download file from R2: {error}"
            ) from error

    def delete_file(self, object_key: str) -> bool:
        """Delete a file from R2."""

        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key,
            )

            return True

        except ClientError as error:
            raise RuntimeError(
                f"Failed to delete file from R2: {error}"
            ) from error

    def file_exists(self, object_key: str) -> bool:
        """Check whether an object exists in R2."""

        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=object_key,
            )

            return True

        except ClientError as error:

            error_code = error.response.get(
                "Error",
                {},
            ).get("Code")

            if error_code in ("404", "NoSuchKey", "NotFound"):
                return False

            raise RuntimeError(
                f"Failed to check R2 object: {error}"
            ) from error


# Shared R2 storage instance
r2_storage = R2Storage()