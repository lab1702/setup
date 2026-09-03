"""Regression tests for the signing key expiry filter.

The filter decides when a vendor keyring is re-fetched or its source
quarantined, so its reading of gpg's colon records is exercised here
directly against synthetic records. Run from the repository root with:

    python3 -m unittest discover --start-directory roles/vendor_repository/tests
"""

from __future__ import annotations

import importlib.util
import pathlib
import unittest

_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "filter_plugins"
    / "signing_key_expiry.py"
)
_SPEC = importlib.util.spec_from_file_location("signing_key_expiry", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
signing_key_expiry = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(signing_key_expiry)

expiry_of = signing_key_expiry.signing_key_expiry
AnsibleFilterError = signing_key_expiry.AnsibleFilterError

Y2020 = 1609372800
Y2027 = 1822521600
Y2030 = 1893456000
Y2032 = 1957996800


def pub(caps: str, expiry: int | None = None) -> str:
    return f"pub:-:255:22:AAAA:1600000000:{expiry or ''}::-:::{caps}:::::ed25519:::0:"


def sub(caps: str, expiry: int | None = None) -> str:
    return f"sub:-:255:18:BBBB:1600000000:{expiry or ''}:::::{caps}:::::cv25519::"


FPR = "fpr:::::::::AAAA:"
UID = "uid:-::::1600000000::HASH::Vendor <vendor@example.invalid>::::::::::0:"


class SigningKeyExpiryTests(unittest.TestCase):
    def test_primary_that_signs_and_expires(self) -> None:
        # CRAN's shape: the primary signs and carries the expiry.
        self.assertEqual(expiry_of([pub("scaESCA", Y2027), FPR, UID, sub("e", Y2027)]), Y2027)

    def test_primary_that_signs_forever(self) -> None:
        self.assertEqual(expiry_of([pub("scSC"), FPR, UID]), 0)

    def test_encryption_subkey_expiry_is_ignored(self) -> None:
        # MEGA's shape: only the encryption subkey is bounded separately.
        self.assertEqual(expiry_of([pub("scESC", Y2032), FPR, UID, sub("e", Y2020)]), Y2032)

    def test_retired_signing_subkey_beside_a_valid_one(self) -> None:
        # A rotated key keeps the expired subkey; the valid one still signs.
        self.assertEqual(
            expiry_of([pub("cSC"), FPR, UID, sub("s", Y2020), sub("s")]), 0
        )

    def test_latest_bounded_signing_subkey_wins(self) -> None:
        self.assertEqual(
            expiry_of([pub("cSC"), FPR, UID, sub("s", Y2020), sub("s", Y2030)]),
            Y2030,
        )

    def test_expired_primary_bounds_its_subkeys(self) -> None:
        self.assertEqual(expiry_of([pub("cC", Y2020), FPR, UID, sub("s")]), Y2020)

    def test_primary_expiry_caps_a_later_subkey(self) -> None:
        self.assertEqual(
            expiry_of([pub("cC", Y2027), FPR, UID, sub("s", Y2030)]), Y2027
        )

    def test_unbounded_signing_primary_outlives_bounded_subkey(self) -> None:
        self.assertEqual(expiry_of([pub("scSC"), FPR, UID, sub("s", Y2030)]), 0)

    def test_key_without_signing_capability_never_expires(self) -> None:
        self.assertEqual(expiry_of([pub("cC", Y2027), FPR, UID, sub("e", Y2027)]), 0)

    def test_only_the_first_key_is_considered(self) -> None:
        records = [pub("scSC", Y2027), FPR, UID, pub("scSC", Y2020), FPR, UID]
        self.assertEqual(expiry_of(records), Y2027)

    def test_subkeys_before_any_primary_are_ignored(self) -> None:
        self.assertEqual(expiry_of([sub("s", Y2020), pub("scSC")]), 0)

    def test_short_and_foreign_records_are_ignored(self) -> None:
        self.assertEqual(expiry_of(["tru::1:1600000000:0:3:1:5", "", pub("scSC", Y2027)]), Y2027)

    def test_empty_output_never_expires(self) -> None:
        self.assertEqual(expiry_of([]), 0)

    def test_unparseable_expiry_is_an_error(self) -> None:
        with self.assertRaises(AnsibleFilterError):
            expiry_of(["pub:-:255:22:AAAA:1600000000:soon::-:::scSC:::::ed25519:::0:"])

    def test_non_list_input_is_an_error(self) -> None:
        with self.assertRaises(AnsibleFilterError):
            expiry_of("pub:...")

    def test_filter_is_registered_under_its_task_name(self) -> None:
        filters = signing_key_expiry.FilterModule().filters()
        self.assertIs(filters["signing_key_expiry"], expiry_of)


if __name__ == "__main__":
    unittest.main()
