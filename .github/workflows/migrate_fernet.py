"""One-time, all-or-nothing Fernet rotation for Firebase to_handle records."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from typing import Any

import requests
from cryptography.fernet import Fernet, InvalidToken


FIREBASE_URL = "https://first2know-default-rtdb.firebaseio.com/to_handle.json"


def require_environment(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable {name} is missing")
    return value


def legacy_key(password: str, encryption_key: str) -> bytes:
    digest = hashlib.md5((password + encryption_key).encode()).hexdigest()
    expanded = digest * 32
    return base64.urlsafe_b64encode(expanded.encode()[:32])


def main() -> None:
    old_secrets = json.loads(require_environment("OLD_SECRETS_JSON"))
    old_password = old_secrets.get("email_password")
    if not isinstance(old_password, str) or not old_password:
        raise RuntimeError("SECRETS_JSON does not contain email_password")

    new_key = require_environment("NEW_FERNET_KEY").encode()
    new_fernet = Fernet(new_key)

    response = requests.get(
        FIREBASE_URL,
        headers={"X-Firebase-ETag": "true"},
        timeout=30,
    )
    response.raise_for_status()
    etag = response.headers.get("ETag")
    if not etag:
        raise RuntimeError("Firebase did not return an ETag")

    records: Any = response.json()
    if not isinstance(records, dict) or not records:
        raise RuntimeError("Firebase to_handle collection is empty or invalid")

    migrated: dict[str, dict[str, Any]] = {}
    plaintext_by_id: dict[str, bytes] = {}
    record_user: str | None = None

    # Complete every validation and decryption before issuing the single write.
    for record_id, raw_record in records.items():
        if not isinstance(record_id, str) or not isinstance(raw_record, dict):
            raise RuntimeError("A Firebase record has an invalid shape")
        encrypted = raw_record.get("encrypted")
        user = raw_record.get("user")
        if not isinstance(encrypted, str) or not encrypted:
            raise RuntimeError("A Firebase record has no encrypted payload")
        if not isinstance(user, str) or not user:
            raise RuntimeError("A Firebase record has no user")
        if record_user is None:
            record_user = user
        elif user != record_user:
            raise RuntimeError("Firebase records belong to more than one user")

        old_key = legacy_key(old_password, user)
        if new_key == old_key:
            raise RuntimeError("Replacement key unexpectedly matches the legacy key")
        old_fernet = Fernet(old_key)

        try:
            plaintext = old_fernet.decrypt(encrypted.encode())
        except InvalidToken as exc:
            raise RuntimeError("A Firebase record cannot be decrypted with the legacy key") from exc
        json.loads(plaintext)

        updated_record = dict(raw_record)
        updated_record["encrypted"] = new_fernet.encrypt(plaintext).decode()
        if new_fernet.decrypt(updated_record["encrypted"].encode()) != plaintext:
            raise RuntimeError("Local verification of a migrated record failed")
        migrated[record_id] = updated_record
        plaintext_by_id[record_id] = plaintext

    update = requests.put(
        FIREBASE_URL,
        headers={"If-Match": etag},
        json=migrated,
        timeout=30,
    )
    if update.status_code == 412:
        raise RuntimeError("Firebase changed during migration; no records were written")
    update.raise_for_status()

    verification = requests.get(FIREBASE_URL, timeout=30)
    verification.raise_for_status()
    stored: Any = verification.json()
    if not isinstance(stored, dict) or set(stored) != set(migrated):
        raise RuntimeError("Post-migration record set does not match")
    for record_id, raw_record in stored.items():
        if not isinstance(raw_record, dict):
            raise RuntimeError("A stored record has an invalid shape")
        encrypted = raw_record.get("encrypted")
        if not isinstance(encrypted, str):
            raise RuntimeError("A stored record has no encrypted payload")
        if new_fernet.decrypt(encrypted.encode()) != plaintext_by_id[record_id]:
            raise RuntimeError("Post-migration plaintext verification failed")

    print(f"Rotated and verified {len(migrated)} encrypted records")


if __name__ == "__main__":
    main()
