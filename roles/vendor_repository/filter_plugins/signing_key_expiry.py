"""Filter deriving when an OpenPGP key stops being able to sign.

apt verifies a repository with whichever signing-capable key of the vendor's
keyring signed the Release file, and gpg treats a subkey as valid only while
its primary key is: a subkey's effective expiry is the earlier of its own and
the primary's. A vendor that rotates subkeys keeps the retired, expired one
beside the new one, so the key as a whole stops signing only when its latest
effective expiry passes. That single moment is what the predicate consumes.
"""

from __future__ import annotations

from ansible.errors import AnsibleFilterError

_RECORD_FIELDS = 12  # up to and including the capabilities field
_EXPIRY_FIELD = 6
_CAPABILITIES_FIELD = 11


def _record_expiry(fields: list[str]) -> int | None:
    """Return the record's expiry in seconds since the epoch, or None."""
    value = fields[_EXPIRY_FIELD]
    if not value:
        return None
    try:
        return int(value)
    except ValueError as error:
        raise AnsibleFilterError(
            f"Unable to parse the key expiry {value!r}: {error}"
        ) from error


def _earlier(first: int | None, second: int | None) -> int | None:
    if first is None:
        return second
    if second is None:
        return first
    return min(first, second)


def signing_key_expiry(records: object) -> int:
    """Return when the first key in gpg --with-colons output stops signing.

    The result is seconds since the epoch, or 0 when the key never stops
    signing (some signing-capable key of it has no bounded expiry) or holds
    no signing-capable key at all. Only the first primary key and its
    subkeys are considered; the fingerprint predicate rejects keyrings
    holding more than one.
    """
    if not isinstance(records, (list, tuple)) or not all(
        isinstance(record, str) for record in records
    ):
        raise AnsibleFilterError(
            "signing_key_expiry expects a list of gpg --with-colons records"
        )

    primary_expiry: int | None = None
    seen_primary = False
    effective_expiries: list[int | None] = []

    for record in records:
        fields = record.split(":")
        if len(fields) < _RECORD_FIELDS or fields[0] not in {"pub", "sub"}:
            continue
        if fields[0] == "pub":
            if seen_primary:
                break
            seen_primary = True
            primary_expiry = _record_expiry(fields)
        elif not seen_primary:
            continue
        # Lowercase capabilities describe this key itself; the uppercase
        # ones on a primary record summarise the whole key.
        if "s" in fields[_CAPABILITIES_FIELD]:
            effective_expiries.append(
                _earlier(primary_expiry, _record_expiry(fields))
            )

    if not effective_expiries or any(
        expiry is None for expiry in effective_expiries
    ):
        return 0
    return max(expiry for expiry in effective_expiries if expiry is not None)


class FilterModule:
    """Expose role-specific Jinja filters."""

    def filters(self) -> dict[str, object]:
        return {"signing_key_expiry": signing_key_expiry}
