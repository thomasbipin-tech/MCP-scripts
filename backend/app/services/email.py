"""Transactional email — the magic-link delivery today, extensible later.

Uses Resend's HTTP API when ``RESEND_API_KEY`` is set; otherwise it logs the
message (development) and reports non-delivery so the caller can decide what to
do. Delivery never leaks the token into an API response — that decision belongs
to the auth router, which only exposes it outside production.

Pure stdlib (``urllib``) so there is no new dependency and it imports on a bare
interpreter.
"""

from __future__ import annotations

import json
import logging
import urllib.request

from ..core.config import settings

log = logging.getLogger("dealproof.email")


def send_email(to: str, subject: str, text: str) -> bool:
    """Return True only if the message was accepted by the provider."""
    if not settings.resend_api_key:
        log.info("EMAIL (no provider configured) to=%s subject=%r", to, subject)
        return False
    payload = json.dumps(
        {"from": settings.email_from, "to": [to], "subject": subject, "text": text}
    ).encode()
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {settings.resend_api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return 200 <= r.status < 300
    except Exception as e:  # pragma: no cover - network path
        log.error("email send failed to=%s: %s", to, e)
        return False


def send_magic_link(email: str, token: str) -> bool:
    link = f"{settings.app_base_url}/#/verify?token={token}"
    minutes = max(1, settings.magic_link_ttl // 60)
    subject = "Your DealProofing sign-in link"
    text = (
        "Sign in to DealProofing by opening this link:\n\n"
        f"{link}\n\n"
        f"The link expires in {minutes} minutes. If you didn't request it, ignore this email."
    )
    return send_email(email, subject, text)
