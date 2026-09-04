"""Exercise malformed metadata through the actual role against a local HTTP fixture.

Run from the repository root with:

    python3 -m unittest discover --start-directory roles/github_release/tests

Requires Ansible, but no network access beyond loopback, credentials, root,
or installed release binaries. All playbook, cache, and Ansible temporary
files are confined to a temporary directory and removed after the test.
"""

from __future__ import annotations

import copy
import json
import os
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[3]
ETAG = 'W/"fixture-release"'
RELEASE = {
    "tag_name": "v1.2.3",
    "published_at": "2020-01-01T00:00:00Z",
    "assets": [
        {
            "name": "fixture.tar.gz",
            "state": "uploaded",
            "browser_download_url": (
                "https://github.com/example/fixture/releases/download/v1.2.3/fixture.tar.gz"
            ),
            "digest": "sha256:" + "a" * 64,
        }
    ],
}


def malformed_releases() -> dict[str, object]:
    cases: dict[str, object] = {
        "root-null": None,
        "root-number": 7,
        "root-list": [RELEASE],
        "root-string": "release",
        "root-empty": {},
    }
    for field, values in {
        "tag_name": [None, 7, [], {}, ""],
        "assets": [None, 7, "assets", {}, [], [None], [{}], [{"name": None}]],
    }.items():
        for index, value in enumerate(values):
            body = copy.deepcopy(RELEASE)
            body[field] = value
            cases[f"{field}-{index}"] = body
    return cases


class ResolveAssetShapeTests(unittest.TestCase):
    def test_cache_and_live_metadata_shapes(self) -> None:
        requests: list[tuple[str, str | None]] = []
        malformed = malformed_releases()

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                conditional = self.headers.get("If-None-Match")
                requests.append((self.path, conditional))
                if self.path == "/unconditional-304" or (
                    self.path == "/valid" and conditional == ETAG
                ):
                    self.send_response(304)
                    self.end_headers()
                    return
                body = (
                    malformed[self.path.removeprefix("/malformed/")]
                    if self.path.startswith("/malformed/")
                    else RELEASE
                )
                payload = json.dumps(body).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("ETag", ETAG)
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, format: str, *args: object) -> None:
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory(
                prefix="github-release-shape-"
            ) as temporary:
                directory = Path(temporary)
                cache = directory / "cache" / "example--fixture.json"
                expected_requests: list[tuple[str, str | None]] = []
                tasks: list[dict] = []

                def resolve(
                    name: str,
                    path: str = "/valid",
                    *,
                    status: int = 200,
                    available: bool = True,
                    conditional: str | None = None,
                ) -> None:
                    expected_requests.append((path, conditional))
                    tasks.extend(
                        [
                            {
                                "name": name,
                                "ansible.builtin.include_role": {
                                    "name": "github_release",
                                    "tasks_from": "resolve_asset.yml",
                                },
                                "vars": {
                                    "github_release_api_url": (
                                        f"http://127.0.0.1:{server.server_port}{path}"
                                    )
                                },
                            },
                            {
                                "name": "Validate " + name,
                                "ansible.builtin.assert": {
                                    "that": [
                                        f"github_release_metadata.status == {status}",
                                        f"github_release_api_available == {available}",
                                        "not github_release_asset_pending",
                                    ]
                                    + (
                                        [
                                            "github_release_version == '1.2.3'",
                                            "github_release_asset.name == 'fixture.tar.gz'",
                                        ]
                                        if available
                                        else [f"not '{cache}' is exists"]
                                    )
                                },
                            },
                        ]
                    )
                    if not available:
                        tasks.append(
                            {
                                "name": "Keep installed release after " + name,
                                "ansible.builtin.include_role": {
                                    "name": "github_release",
                                    "tasks_from": "unavailable_fallback.yml",
                                },
                                "vars": {"github_release_installed": True},
                            }
                        )

                def remove_cache() -> None:
                    tasks.append(
                        {
                            "name": "Remove cache before fresh-response check",
                            "ansible.builtin.file": {
                                "path": str(cache),
                                "state": "absent",
                            },
                        }
                    )

                resolve("Populate a valid cache")
                resolve("Revalidate a valid cache", status=304, conditional=ETAG)
                malformed_caches = {
                    "root-null": None,
                    "root-number": 7,
                    "root-list": [],
                    **{
                        f"etag-{index}": {"etag": etag, "body": RELEASE}
                        for index, etag in enumerate([None, 7, [], {}, ""])
                    },
                    **{
                        "body-" + name: {"etag": ETAG, "body": body}
                        for name, body in malformed.items()
                    },
                }
                for name, content in malformed_caches.items():
                    tasks.append(
                        {
                            "name": "Seed malformed cache " + name,
                            "ansible.builtin.copy": {
                                "dest": str(cache),
                                "content": json.dumps(content),
                                "mode": "0644",
                            },
                        }
                    )
                    resolve("Discard malformed cache " + name)
                remove_cache()
                for name in malformed:
                    resolve(
                        "Reject malformed fresh metadata " + name,
                        "/malformed/" + name,
                        available=False,
                    )
                resolve(
                    "Reject an unsolicited 304",
                    "/unconditional-304",
                    status=304,
                    available=False,
                )
                resolve("Recover after malformed metadata")
                resolve("Revalidate the recovered cache", status=304, conditional=ETAG)

                playbook = [
                    {
                        "name": "Exercise release metadata shape validation",
                        "hosts": "localhost",
                        "connection": "local",
                        "gather_facts": False,
                        "vars_files": [str(REPOSITORY / "group_vars" / "all.yml")],
                        "vars": {
                            "github_release_display_name": "Metadata shape fixture",
                            "github_release_repository": "example/fixture",
                            "github_release_asset_filename": "fixture.tar.gz",
                            "github_release_cache_directory": str(cache.parent),
                            "github_release_cache_owner": str(os.getuid()),
                            "github_release_cache_group": str(os.getgid()),
                            "github_release_api_token": "",
                        },
                        "tasks": tasks,
                    }
                ]
                playbook_path = directory / "playbook.json"
                playbook_path.write_text(json.dumps(playbook))
                result = subprocess.run(
                    ["ansible-playbook", str(playbook_path)],
                    cwd=REPOSITORY,
                    env={
                        **os.environ,
                        "ANSIBLE_ROLES_PATH": str(REPOSITORY / "roles"),
                        "ANSIBLE_LOCAL_TEMP": str(directory / "local"),
                        "ANSIBLE_REMOTE_TEMP": str(directory / "remote"),
                        "ANSIBLE_NOCOLOR": "1",
                        "NO_PROXY": "127.0.0.1,localhost",
                        "no_proxy": "127.0.0.1,localhost",
                    },
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=300,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout[-20000:])
                self.assertEqual(requests, expected_requests)
                self.assertEqual(
                    json.loads(cache.read_text()), {"etag": ETAG, "body": RELEASE}
                )
                self.assertIn(
                    "typically assets still uploading or a source-only release",
                    result.stdout,
                )
                self.assertIn(
                    "typically an intercepting proxy or a network problem",
                    result.stdout,
                )
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
