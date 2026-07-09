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


def delete_prefix(prefix: str) -> int:
    """Delete every stored object under ``prefix`` (e.g. ``deals/<id>``).
    Returns the number of objects removed. Used by the data-purge endpoint so a
    buyer can prove the seller's documents were destroyed."""
    if settings.s3_endpoint:
        s3 = _s3()
        removed = 0
        token = None
        while True:
            kw = {"Bucket": settings.s3_bucket, "Prefix": prefix}
            if token:
                kw["ContinuationToken"] = token
            resp = s3.list_objects_v2(**kw)
            for obj in resp.get("Contents", []):
                s3.delete_object(Bucket=settings.s3_bucket, Key=obj["Key"])
                removed += 1
            if not resp.get("IsTruncated"):
                return removed
            token = resp.get("NextContinuationToken")
    import shutil

    p = DATA_DIR / prefix
    if p.exists():
        n = sum(1 for _ in p.rglob("*") if _.is_file())
        shutil.rmtree(p, ignore_errors=True)
        return n
    return 0


def signed_url(key: str) -> str:
    if settings.s3_endpoint:
        return _s3().generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket, "Key": key},
            ExpiresIn=settings.signed_url_ttl,
        )
    # Local: a short-lived signed link the API's document route validates.
    from ..core.security import sign_storage_token  # lazy to avoid import cycle

    return f"/api/storage/{key}?token={sign_storage_token(key)}"


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
