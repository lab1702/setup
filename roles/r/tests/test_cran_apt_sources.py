"""Regression tests for the CRAN APT source migration filter.

The filter decides which lines are deleted from root-owned APT sources, so
its parsing is exercised here directly rather than through a playbook: the
cases below cover both source formats without touching /etc/apt, the
network, or requiring root. Run from the repository root with:

    python3 -m unittest discover --start-directory roles/r/tests
"""

from __future__ import annotations

import importlib.util
import pathlib
import unittest

_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "filter_plugins"
    / "cran_apt_sources.py"
)
_SPEC = importlib.util.spec_from_file_location("cran_apt_sources", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
cran_apt_sources = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cran_apt_sources)

migrate = cran_apt_sources.migrate_cran_apt_source

# The configured repository URL from roles/r/defaults/main.yml.
CRAN_URL = "https://cloud.r-project.org/bin/linux/ubuntu"
ARCHIVE_ENTRY = "deb http://archive.ubuntu.com/ubuntu resolute main\n"


class OneLineSourceTests(unittest.TestCase):
    """Entries in .list files, which use the one-line format."""

    def migrate_list(self, content: str, repository_url: str = CRAN_URL):
        return migrate(content, "/etc/apt/sources.list.d/other.list", repository_url)

    def assert_removed(self, entry: str, matching_entries: int = 1) -> None:
        result = self.migrate_list(entry + ARCHIVE_ENTRY)
        self.assertTrue(result["migration_required"])
        self.assertEqual(result["matching_entries"], matching_entries)
        self.assertEqual(result["content"], ARCHIVE_ENTRY)

    def assert_retained(self, entry: str) -> None:
        result = self.migrate_list(entry + ARCHIVE_ENTRY)
        self.assertFalse(result["migration_required"])
        self.assertEqual(result["matching_entries"], 0)
        self.assertEqual(result["content"], entry + ARCHIVE_ENTRY)

    def test_exact_repository_url_is_removed(self) -> None:
        self.assert_removed(f"deb {CRAN_URL} resolute-cran40/\n")

    def test_option_bracket_is_tolerated(self) -> None:
        self.assert_removed(
            f"deb [arch=amd64 signed-by=/usr/share/keyrings/cran.asc] "
            f"{CRAN_URL} resolute-cran40/\n"
        )

    def test_source_entries_are_removed(self) -> None:
        self.assert_removed(f"deb-src {CRAN_URL} resolute-cran40/\n")

    def test_leading_whitespace_and_case_are_tolerated(self) -> None:
        self.assert_removed(f"\tDEB {CRAN_URL} resolute-cran40/\n")

    def test_plain_http_entry_is_removed(self) -> None:
        self.assert_removed("deb http://cloud.r-project.org/bin/linux/ubuntu x/\n")

    def test_trailing_slash_is_normalised(self) -> None:
        self.assert_removed(f"deb {CRAN_URL}/ resolute-cran40/\n")

    def test_default_port_is_normalised(self) -> None:
        self.assert_removed("deb https://cloud.r-project.org:443/bin/linux/ubuntu x/\n")

    def test_any_mirror_serving_the_cran_path_is_removed(self) -> None:
        self.assert_removed("deb https://mirror.example.edu/CRAN/bin/linux/ubuntu x/\n")

    def test_partial_path_segment_is_not_a_mirror(self) -> None:
        self.assert_retained("deb https://mirror.example.edu/xbin/linux/ubuntu x/\n")

    def test_unrelated_repository_is_retained(self) -> None:
        self.assert_retained(
            "deb https://packages.microsoft.com/repos/code stable main\n"
        )

    def test_commented_entry_is_retained(self) -> None:
        self.assert_retained(f"# deb {CRAN_URL} resolute-cran40/\n")

    def test_uri_with_credentials_is_retained(self) -> None:
        # A credentialed URI is not the managed repository, so it is left for
        # an administrator rather than silently deleted.
        self.assert_retained(
            "deb https://user:secret@cloud.r-project.org/bin/linux/ubuntu x/\n"
        )

    def test_windows_line_endings_are_preserved(self) -> None:
        result = self.migrate_list(f"deb {CRAN_URL} resolute-cran40/\r\nkeep me\r\n")
        self.assertTrue(result["migration_required"])
        self.assertEqual(result["content"], "keep me\r\n")

    def test_final_line_without_newline_is_removed(self) -> None:
        result = self.migrate_list(f"deb {CRAN_URL} resolute-cran40/")
        self.assertTrue(result["migration_required"])
        self.assertEqual(result["content"], "")

    def test_single_segment_url_never_suffix_matches(self) -> None:
        # A configured URL like the OS archive's identifies nothing
        # CRAN-specific, so suffix matching must stay off or unrelated
        # repositories -- including the archive itself -- would be deleted.
        result = self.migrate_list(
            "deb https://mirror.example.edu/pub/ubuntu resolute main\n",
            repository_url="https://archive.ubuntu.com/ubuntu",
        )
        self.assertFalse(result["migration_required"])

    def test_matching_entries_are_counted(self) -> None:
        self.assert_removed(
            f"deb {CRAN_URL} resolute-cran40/\ndeb-src {CRAN_URL} resolute-cran40/\n",
            matching_entries=2,
        )


class Deb822SourceTests(unittest.TestCase):
    """Stanzas in .sources files, which use the deb822 format."""

    ARCHIVE_STANZA = (
        "Types: deb\nURIs: http://archive.ubuntu.com/ubuntu\nSuites: resolute\n"
    )

    def migrate_sources(self, content: str):
        return migrate(content, "/etc/apt/sources.list.d/other.sources", CRAN_URL)

    def test_solo_cran_stanza_is_removed_entirely(self) -> None:
        result = self.migrate_sources(
            f"Types: deb\nURIs: {CRAN_URL}\nSuites: resolute-cran40/\n"
        )
        self.assertTrue(result["migration_required"])
        self.assertEqual(result["matching_entries"], 1)
        self.assertEqual(result["content"], "")

    def test_unrelated_stanza_is_retained(self) -> None:
        result = self.migrate_sources(self.ARCHIVE_STANZA)
        self.assertFalse(result["migration_required"])
        self.assertEqual(result["content"], self.ARCHIVE_STANZA)

    def test_only_the_cran_stanza_of_several_is_removed(self) -> None:
        content = f"{self.ARCHIVE_STANZA}\nTypes: deb\nURIs: {CRAN_URL}\nSuites: x/\n"
        result = self.migrate_sources(content)
        self.assertTrue(result["migration_required"])
        self.assertEqual(result["content"], f"{self.ARCHIVE_STANZA}\n")

    def test_shared_stanza_keeps_its_unrelated_uri(self) -> None:
        result = self.migrate_sources(
            f"Types: deb\nURIs: {CRAN_URL} https://other.example/deb\nSuites: x\n"
        )
        self.assertTrue(result["migration_required"])
        self.assertEqual(
            result["content"],
            "Types: deb\nURIs: https://other.example/deb\nSuites: x\n",
        )

    def test_continuation_line_keeps_its_unrelated_uri(self) -> None:
        result = self.migrate_sources(
            f"Types: deb\nURIs: {CRAN_URL}\n https://other.example/deb\nSuites: x\n"
        )
        self.assertTrue(result["migration_required"])
        self.assertEqual(
            result["content"],
            "Types: deb\nURIs: \n https://other.example/deb\nSuites: x\n",
        )

    def test_stanza_whose_continuation_is_all_cran_is_removed(self) -> None:
        result = self.migrate_sources(
            f"Types: deb\nURIs: {CRAN_URL}\n"
            " https://mirror.example.edu/CRAN/bin/linux/ubuntu\nSuites: x\n"
        )
        self.assertTrue(result["migration_required"])
        self.assertEqual(result["matching_entries"], 2)
        self.assertEqual(result["content"], "")

    def test_field_names_are_case_insensitive(self) -> None:
        result = self.migrate_sources(f"Types: deb\nuris: {CRAN_URL}\nSuites: x\n")
        self.assertTrue(result["migration_required"])
        self.assertEqual(result["content"], "")

    def test_comments_inside_a_shared_stanza_are_retained(self) -> None:
        result = self.migrate_sources(
            f"Types: deb\n# a note\nURIs: {CRAN_URL} https://other.example/deb\n"
        )
        self.assertTrue(result["migration_required"])
        self.assertEqual(
            result["content"],
            "Types: deb\n# a note\nURIs: https://other.example/deb\n",
        )

    def test_disabled_stanza_is_left_alone(self) -> None:
        for value in ("0", "disable", "false", "no", "off", "without", "NO"):
            with self.subTest(enabled=value):
                content = f"Enabled: {value}\nTypes: deb\nURIs: {CRAN_URL}\nSuites: x\n"
                result = self.migrate_sources(content)
                self.assertFalse(result["migration_required"])
                self.assertEqual(result["matching_entries"], 0)
                self.assertEqual(result["content"], content)

    def test_explicitly_enabled_stanza_is_migrated(self) -> None:
        result = self.migrate_sources(
            f"Enabled: yes\nTypes: deb\nURIs: {CRAN_URL}\nSuites: x\n"
        )
        self.assertTrue(result["migration_required"])
        self.assertEqual(result["content"], "")


class FilterInterfaceTests(unittest.TestCase):
    """The contract the competing_sources tasks rely on."""

    def test_content_is_omitted_when_not_requested(self) -> None:
        # The symlink pass only needs the verdict, never the rewritten body.
        result = migrate(
            f"deb {CRAN_URL} x/\n",
            "/etc/apt/sources.list.d/other.list",
            CRAN_URL,
            False,
        )
        self.assertTrue(result["migration_required"])
        self.assertNotIn("content", result)

    def test_sources_suffix_selects_the_deb822_parser(self) -> None:
        # A deb822 body under a .list name would parse as one-line entries
        # and match nothing, so the suffix drives the choice.
        body = f"Types: deb\nURIs: {CRAN_URL}\nSuites: x\n"
        self.assertTrue(
            migrate(body, "/etc/apt/sources.list.d/A.SOURCES", CRAN_URL)[
                "migration_required"
            ]
        )
        self.assertFalse(
            migrate(body, "/etc/apt/sources.list.d/a.list", CRAN_URL)[
                "migration_required"
            ]
        )

    def test_unchanged_content_reports_no_migration(self) -> None:
        result = migrate(ARCHIVE_ENTRY, "/etc/apt/sources.list", CRAN_URL)
        self.assertFalse(result["migration_required"])
        self.assertEqual(result["content"], ARCHIVE_ENTRY)

    def test_filter_is_registered_under_its_task_name(self) -> None:
        filters = cran_apt_sources.FilterModule().filters()
        self.assertIn("migrate_cran_apt_source", filters)
        self.assertIs(filters["migrate_cran_apt_source"], migrate)


if __name__ == "__main__":
    unittest.main()
