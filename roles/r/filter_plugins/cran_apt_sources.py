"""Filters for migrating duplicate CRAN APT source entries.

An entry competes with the managed source when it points at the configured
repository itself or at any CRAN mirror, which serves the same Ubuntu
repository under the configured URL's distinctive path layout.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

from ansible.errors import AnsibleFilterError

_ONE_LINE_SOURCE = re.compile(
    r"^[ \t]*(?:deb|deb-src)[ \t]+"
    r"(?:\[[^\]\r\n]*\][ \t]+)?"
    r"(?P<uri>[^ \t\r\n#]+)",
    re.IGNORECASE,
)
_DEB822_FIELD = re.compile(r"^(?P<name>[A-Za-z][A-Za-z0-9-]*):[ \t]*(?P<value>.*)$")
# False spellings accepted by APT's boolean parser.
_DEB822_FALSE_VALUES = {"0", "disable", "false", "no", "off", "without"}


def _normalise_repository_uri(uri: str) -> tuple[str, str, int | None, str] | None:
    """Return the APT-relevant parts of an HTTP(S) repository URI."""
    try:
        parsed = urlsplit(uri)
        port = parsed.port
    except ValueError:
        return None

    scheme = parsed.scheme.lower()
    if (
        scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        return None

    if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        port = None

    path = parsed.path.rstrip("/") or "/"
    return scheme, parsed.hostname.lower(), port, path


def _is_matching_repository_uri(candidate: str, expected: str) -> bool:
    candidate_parts = _normalise_repository_uri(candidate)
    expected_parts = _normalise_repository_uri(expected)
    if candidate_parts is None or expected_parts is None:
        return False

    # _normalise_repository_uri only accepts HTTP(S) URIs, and CRAN has
    # historically documented both forms, so schemes need no further
    # comparison: an old HTTP entry is not left behind.
    _, candidate_host, candidate_port, candidate_path = candidate_parts
    _, expected_host, expected_port, expected_path = expected_parts

    if (
        candidate_host == expected_host
        and candidate_port == expected_port
        and candidate_path == expected_path
    ):
        return True

    # Every CRAN mirror serves the Ubuntu repository under the configured
    # URL's distinctive path layout (cran.r-project.org/bin/linux/ubuntu,
    # mirror.example.edu/CRAN/bin/linux/ubuntu, ...), so an entry on any host
    # whose path ends with that layout also competes with the managed source.
    # The suffix's leading "/" keeps the comparison on full path-segment
    # boundaries. A root or single-segment expected path (for example the
    # "/ubuntu" of Ubuntu's own archive URLs) identifies nothing
    # CRAN-specific, so such a configured URL matches exactly or not at
    # all: suffix-matching it would classify unrelated repositories --
    # including the OS archive -- as competing and delete them.
    return expected_path.count("/") >= 2 and candidate_path.endswith(expected_path)


def _migrate_one_line_sources(content: str, repository_url: str) -> tuple[str, int]:
    retained_lines: list[str] = []
    matching_entries = 0

    for line in content.splitlines(keepends=True):
        match = _ONE_LINE_SOURCE.match(line)
        if match and _is_matching_repository_uri(match.group("uri"), repository_url):
            matching_entries += 1
            continue
        retained_lines.append(line)

    return "".join(retained_lines), matching_entries


def _line_ending(line: str) -> str:
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    return ""


def _deb822_field_values(stanza: list[str], field_name: str) -> list[str]:
    values: list[str] = []
    current_field: str | None = None

    for raw_line in stanza:
        line = raw_line.rstrip("\r\n")
        if line.lstrip(" \t").startswith("#"):
            continue

        field_match = _DEB822_FIELD.match(line)
        if field_match:
            current_field = field_match.group("name").casefold()
            if current_field == field_name:
                values.append(field_match.group("value"))
            continue

        if line.startswith((" ", "\t")) and current_field == field_name and values:
            values[-1] += " " + line.strip(" \t")
        else:
            current_field = None

    return [value.strip() for value in values]


def _migrate_deb822_stanza(
    stanza: list[str], repository_url: str
) -> tuple[list[str], int]:
    enabled_values = _deb822_field_values(stanza, "enabled")
    if (
        len(enabled_values) == 1
        and enabled_values[0].casefold() in _DEB822_FALSE_VALUES
    ):
        return stanza, 0

    retained_lines: list[str] = []
    matching_entries = 0
    unrelated_entries = 0
    in_uris_field = False

    for raw_line in stanza:
        ending = _line_ending(raw_line)
        line = raw_line[: -len(ending)] if ending else raw_line

        if line.lstrip(" \t").startswith("#"):
            retained_lines.append(raw_line)
            continue

        field_match = _DEB822_FIELD.match(line)
        if field_match:
            in_uris_field = field_match.group("name").lower() == "uris"
            if not in_uris_field:
                retained_lines.append(raw_line)
                continue

            prefix = line[: field_match.start("value")]
            values = field_match.group("value").split()
        elif line.startswith((" ", "\t")) and in_uris_field:
            value_start = len(line) - len(line.lstrip(" \t"))
            prefix = line[:value_start]
            values = line[value_start:].split()
        else:
            in_uris_field = False
            retained_lines.append(raw_line)
            continue

        unrelated_values = []
        for value in values:
            if _is_matching_repository_uri(value, repository_url):
                matching_entries += 1
            else:
                unrelated_entries += 1
                unrelated_values.append(value)

        if len(unrelated_values) == len(values):
            retained_lines.append(raw_line)
        elif unrelated_values:
            retained_lines.append(prefix + " ".join(unrelated_values) + ending)
        elif field_match:
            # Keep the field header when a later continuation line may still
            # contain an unrelated URI.
            retained_lines.append(prefix + ending)

    if matching_entries and not unrelated_entries:
        return [], matching_entries
    return retained_lines, matching_entries


def _migrate_deb822_sources(content: str, repository_url: str) -> tuple[str, int]:
    retained_parts: list[str] = []
    stanza: list[str] = []
    matching_entries = 0

    def retain_or_remove_stanza() -> None:
        nonlocal matching_entries
        if not stanza:
            return

        migrated_stanza, matches = _migrate_deb822_stanza(stanza, repository_url)
        if matches:
            matching_entries += matches
        retained_parts.extend(migrated_stanza)
        stanza.clear()

    for line in content.splitlines(keepends=True):
        if line.rstrip("\r\n").strip(" \t"):
            stanza.append(line)
        else:
            retain_or_remove_stanza()
            retained_parts.append(line)
    retain_or_remove_stanza()

    return "".join(retained_parts), matching_entries


def migrate_cran_apt_source(
    content: str,
    path: str,
    repository_url: str,
    include_content: bool = True,
) -> dict[str, object]:
    """Remove CRAN entries while retaining all unrelated source content."""
    try:
        if path.lower().endswith(".sources"):
            migrated_content, matching_entries = _migrate_deb822_sources(
                content, repository_url
            )
        else:
            migrated_content, matching_entries = _migrate_one_line_sources(
                content, repository_url
            )
    except (TypeError, ValueError) as error:
        raise AnsibleFilterError(
            f"Unable to inspect APT source {path}: {error}"
        ) from error

    result: dict[str, object] = {
        "migration_required": migrated_content != content,
        "matching_entries": matching_entries,
    }
    if include_content:
        result["content"] = migrated_content
    return result


class FilterModule:
    """Expose role-specific Jinja filters."""

    def filters(self) -> dict[str, object]:
        return {"migrate_cran_apt_source": migrate_cran_apt_source}
