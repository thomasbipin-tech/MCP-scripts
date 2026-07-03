"""Document storage abstraction.

Local filesystem by default (dev/tests); S3-compatible (MinIO/R2) when
``S3_ENDPOINT`` is configured. Keys are prefixed per-deal so access can be scoped
and purged per SPEC §7. Signed URLs are 15-minute (config) presigned S3 URLs in
prod, or an API-served path locally.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from ..core.config import settings

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def storage_key(deal_id: str, doc_id: str) -> str:
    return f"deals/{deal_id}/{doc_id}.pdf"


def put_object(key: str, data: bytes) -> str:
    if settings.s3_endpoint:
        _s3().put_object(Bucket=settings.s3_bucket, Key=key, Body=data,
                         ServerSideEncryption="AES256")
        return key
    path = DATA_DIR / key
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return key


def get_object(key: str) -> bytes:
    if settings.s3_endpoint:
        obj = _s3().get_object(Bucket=settings.s3_bucket, Key=key)
        return obj["Body"].read()
    return (DATA_DIR / key).read_bytes()


def signed_url(key: str) -> str:
    if settings.s3_endpoint:
        return _s3().generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket, "Key": key},
            ExpiresIn=settings.signed_url_ttl,
        )
    # Local dev: served via the API's document-content route.
    return f"/api/storage/{key}"


_client = None


def _s3():
    global _client
    if _client is None:
        import boto3  # lazy

        _client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )
    return _client
