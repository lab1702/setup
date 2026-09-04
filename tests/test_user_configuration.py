"""Exercise the real user-configuration tasks without exposing npm tokens.

Run from the repository root:
    python3 -m unittest discover --start-directory tests
"""

from __future__ import annotations

import os
import pwd
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

REPOSITORY = Path(__file__).resolve().parents[1]
TASK_NAMES = {
    "Inspect existing user configuration files",
    "Remove duplicate managed user configuration entries",
    "Configure managed user configuration entries",
}
TOKEN = "DUMMY_NPM_TOKEN_MUST_NOT_APPEAR"


class UserConfigurationTests(unittest.TestCase):
    def run_playbook(self, playbook: Path, environment: dict[str, str], *arguments: str) -> str:
        result = subprocess.run(
            ["ansible-playbook", "--diff", "-vvv", *arguments, str(playbook)],
            cwd=REPOSITORY, env=environment,
            capture_output=True, text=True, timeout=90, check=False,
        )
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertNotIn(TOKEN, output)
        return output

    def test_diff_privacy_and_configuration_idempotence(self) -> None:
        source = yaml.safe_load((REPOSITORY / "local.yml").read_text())[0]
        tasks = [task for task in source["tasks"] if task["name"] in TASK_NAMES]
        self.assertEqual(len(tasks), len(TASK_NAMES))
        for duplicate in (False, True):
            with self.subTest(duplicate_prefix=duplicate), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                npmrc = directory / ".npmrc"
                bashrc = directory / ".bashrc"
                initial_npmrc = f"//registry.npmjs.org/:_authToken={TOKEN}\nprefix=/old\n"
                if duplicate:
                    initial_npmrc += "prefix=/duplicate\n"
                initial_bashrc = "export PIP_REQUIRE_VIRTUALENV=0\n"
                npmrc.write_text(initial_npmrc)
                bashrc.write_text(initial_bashrc)
                fixture = [{
                    "name": "Exercise user configuration privacy",
                    "hosts": "localhost",
                    "connection": "local",
                    "gather_facts": False,
                    "vars": {
                        "workstation_user_home": str(directory),
                        "user_name": pwd.getpwuid(os.getuid()).pw_name,
                        "workstation_user_primary_gid": os.getgid(),
                        "workstation_user_configuration_entries": source["vars"][
                            "workstation_user_configuration_entries"
                        ],
                    },
                    "tasks": tasks,
                }]
                playbook = directory / "privacy.yml"
                playbook.write_text(yaml.safe_dump(fixture, sort_keys=False))
                environment = dict(os.environ)
                environment.update(
                    ANSIBLE_LOCAL_TEMP=str(directory / "local"),
                    ANSIBLE_REMOTE_TEMP=str(directory / "remote"),
                    ANSIBLE_NOCOLOR="1",
                )

                preview = self.run_playbook(playbook, environment, "--check")
                self.assertIn("+export PIP_REQUIRE_VIRTUALENV=1", preview)
                self.assertEqual(npmrc.read_text(), initial_npmrc)
                self.assertEqual(bashrc.read_text(), initial_bashrc)

                changed = self.run_playbook(playbook, environment)
                self.assertIn("+export PIP_REQUIRE_VIRTUALENV=1", changed)
                self.assertEqual(
                    npmrc.read_text(),
                    f"//registry.npmjs.org/:_authToken={TOKEN}\nprefix={directory}/.npm-global\n",
                )
                self.assertEqual(npmrc.stat().st_mode & 0o777, 0o600)
                for expected in (
                    "export PIP_REQUIRE_VIRTUALENV=1",
                    'export PATH="$HOME/.npm-global/bin:$PATH"',
                    'export PATH="$HOME/go/bin:$PATH"',
                ):
                    self.assertEqual(bashrc.read_text().splitlines().count(expected), 1)
                self.assertRegex(self.run_playbook(playbook, environment), r"changed=0\s")


if __name__ == "__main__":
    unittest.main()
