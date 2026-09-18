"""Check Debian revisions and repeat-install decisions without installing packages.

Runs the PowerShell and Quarto roles in check mode against local release
metadata and an isolated dpkg database. Requires only loopback networking.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[3]


class DebVersionTests(unittest.TestCase):
    def test_package_revision_and_default_version(self) -> None:
        releases = {}
        for repository, version, filenames in [
            (
                "PowerShell/PowerShell",
                "7.6.6",
                [f"powershell_7.6.6-1.deb_{arch}.deb" for arch in ("amd64", "arm64")],
            ),
            ("quarto-dev/quarto-cli", "1.2.3", ["quarto-1.2.3-linux-amd64.deb"]),
        ]:
            releases[f"/repos/{repository}/releases/latest"] = {
                "tag_name": "v" + version,
                "published_at": "2020-01-01T00:00:00Z",
                "assets": [
                    {
                        "name": filename,
                        "state": "uploaded",
                        "browser_download_url": (
                            f"https://github.com/{repository}/releases/download/"
                            f"v{version}/{filename}"
                        ),
                        "digest": "sha256:" + "a" * 64,
                    }
                    for filename in filenames
                ],
            }

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                payload = json.dumps(releases[self.path]).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, format: str, *args: object) -> None:
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory(prefix="github-deb-version-") as temporary:
                directory = Path(temporary)
                database = directory / "dpkg"
                database.mkdir()
                # The matching revision must be a no-op. The older ARM64
                # package must update. Quarto follows PowerShell to catch
                # an override leaking between consumers of the shared role.
                cases = [
                    ("powershell", "amd64", "7.6.6-1.deb", "7.6.6-1.deb", False),
                    ("powershell", "arm64", "7.5.0-1.deb", "7.6.6-1.deb", True),
                    ("quarto", "amd64", "1.2.3", "1.2.3", False),
                ]
                (database / "status").write_text(
                    "".join(
                        f"Package: {role}\nStatus: install ok installed\n"
                        f"Architecture: {architecture}\nVersion: {installed}\n"
                        # Permit both fixture architectures in one database.
                        "Multi-Arch: same\n"
                        "Maintainer: Test <test@example.invalid>\n"
                        "Description: Package version fixture\n\n"
                        for role, architecture, installed, _, _ in cases
                    )
                )
                binaries = directory / "bin"
                binaries.mkdir()
                probe = binaries / "dpkg-query"
                probe.write_text(
                    "#!/bin/sh\nexec /usr/bin/dpkg-query "
                    f'--admindir={shlex.quote(str(database))} "$@"\n'
                )
                probe.chmod(0o755)
                tasks = []
                for role, architecture, _, target, required in cases:
                    tasks.extend(
                        [
                            {
                                "name": f"Check {role} on {architecture}",
                                "ansible.builtin.include_role": {"name": role},
                                "vars": {"workstation_architecture": architecture},
                            },
                            {
                                "name": f"Validate {role} package version and action",
                                "ansible.builtin.assert": {
                                    "that": [
                                        "github_release_api_available",
                                        "deb_package_installed_query.rc == 0",
                                        (
                                            "deb_package_status_subject == "
                                            f"'{role}:{architecture}={target}'"
                                        ),
                                        f"deb_package_install_required == {required}",
                                        "not deb_package_repair_required",
                                    ]
                                },
                            },
                        ]
                    )
                playbook = directory / "playbook.json"
                playbook.write_text(
                    json.dumps(
                        [
                            {
                                "name": "Check GitHub Debian package versions",
                                "hosts": "localhost",
                                "connection": "local",
                                "gather_facts": False,
                                "vars_files": [str(REPOSITORY / "group_vars/all.yml")],
                                "vars": {
                                    "github_release_api_url": (
                                        f"http://127.0.0.1:{server.server_port}/repos/"
                                        "{{ github_release_repository }}/releases/latest"
                                    ),
                                    "github_release_api_token": "",
                                    "github_release_cache_directory": str(
                                        directory / "cache"
                                    ),
                                    "github_release_cache_owner": str(os.getuid()),
                                    "github_release_cache_group": str(os.getgid()),
                                },
                                "environment": {
                                    "PATH": str(binaries) + ":" + os.environ["PATH"]
                                },
                                "tasks": tasks,
                            }
                        ]
                    )
                )
                result = subprocess.run(
                    ["ansible-playbook", "--check", str(playbook)],
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
                    timeout=90,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stdout[-20000:])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
