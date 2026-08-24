# Ubuntu Developer Workstation Setup

This playbook supports Ubuntu 26.04 on AMD64 and ARM64 systems.
On compatible AMD64 CPUs, it automatically opts in to Ubuntu's AMD64v3
package variant before the playbook's first APT refresh. Older AMD64 CPUs and
ARM64 systems continue to use their baseline packages.
Desktop packages are installed when an X11 or Wayland desktop session is
available. Posit RStudio Desktop, Discord, and Zoom are installed only on AMD64
systems because their configured distribution channels do not publish ARM64
packages. Ruff, ty, uv, uvx, the DuckDB CLI, and Quarto track the latest
GitHub releases for AMD64 and ARM64; their release downloads are verified with
the SHA-256 digests published by GitHub before installation. ChatGPT Desktop
tracks the latest package from OpenAI's APT repository, verified with a signing
key bundled in this repository. Claude Desktop tracks the latest package from
Anthropic's signed APT repository. Discord tracks the latest official stable AMD64
DEB and validates its HTTPS download location and package metadata before
installation. Visual Studio Code tracks the latest stable package from
Microsoft's signed APT repository on AMD64 and ARM64. MEGA Desktop tracks the
latest package from MEGA's signed APT repository on AMD64 and ARM64. Zoom
Workplace tracks the latest package from Zoom's signed, AMD64-only APT
repository. R tracks the latest release from CRAN's signed Ubuntu repository
on AMD64 and ARM64. Posit RStudio Desktop tracks the latest stable release
published in Posit's download metadata (`https://cdn.posit.co/downloads.json`)
and verifies the DEB against the SHA-256 checksum published there. LibreOffice
is installed from the Ubuntu archive on desktop systems.

## Accepted Security Tradeoffs

This repository is intended for a personally managed, single-user workstation
on a trusted home network. The following security review items are accepted for
that use case (items 3 and 4 from the original review were remediated rather
than accepted, so their numbers are unused):

- **Item 1 — Mutable root checkout:** `ansible-pull` follows the repository's
  mutable default branch and executes the checked-out playbook as root. This is
  acceptable while the repository, GitHub account, and merged changes remain
  under the owner's control.
- **Item 2 — Docker group access:** The workstation user is added to the
  `docker` group, which grants root-equivalent access through the Docker daemon.
  This is acceptable because the account and workstation are not shared with
  untrusted users.
- **Item 5 — Implicit workstation user:** When `SUDO_USER` is unavailable, the
  playbook falls back to the account running Ansible, which can be root. This is
  acceptable because the intended invocation is an interactive
  `sudo ansible-pull` by the workstation owner; direct root, cron, or service
  runs knowingly accept root as the target account.
- **Item 6 — Automatic updates:** The playbook tracks current vendor releases
  and performs an APT distribution upgrade. This is acceptable because the
  owner prefers current software and accepts the possibility of package changes,
  service restarts, reboots, or an upstream regression.
- **Item 7 — OpenSSH defaults:** The playbook installs OpenSSH Server without a
  custom hardening policy. This is acceptable while SSH is reachable only from
  the trusted home network, is not forwarded or otherwise exposed publicly, and
  only owner-controlled accounts can authenticate.
- **Item 8 — Discord package transport trust:** Discord publishes its stable
  Linux DEB through an official HTTPS endpoint, but does not publish a signed
  APT repository, detached signature, or checksum for it. The playbook restricts
  downloads to Discord's expected HTTPS hosts and validates the package name,
  version, and architecture, but package authenticity ultimately relies on TLS
  and Discord's download infrastructure. This is acceptable for this
  personally managed workstation.
- **Item 9 — Local service packages:** The playbook installs `glances` and
  `ttyd` with their distribution-default service and privilege behavior, and
  both can expose a local network service (a monitoring web UI and a
  shell-over-HTTP terminal) if their services are enabled. This is acceptable
  on this trusted single-user host because the playbook does not deliberately
  expose either service remotely.

Reassess these decisions before using the playbook on a shared workstation, an
untrusted network, infrastructure managed by multiple people, or a host whose
SSH service is exposed to the internet.

## Step 0: Set up fingerprint Authentication

### If applicable do this after enrolling your fingerprint

```bash
sudo pam-auth-update
```

## Automatic AMD64v3 package selection

Early in the run, the `amd64v3` role asks glibc whether the current AMD64 CPU
supports the complete x86-64-v3 feature level. When it does, the role manages
`/etc/apt/apt.conf.d/99enable-amd64v3` and enables Ubuntu's `amd64v3` package
variant. On an older AMD64 CPU or ARM64 system, the managed opt-in is removed
and future APT package selection remains on the baseline.

You can inspect the same CPU capability yourself:

```bash
ld.so --help | grep -F 'x86-64-v3 (supported, searched)'
```

Once AMD64v3 packages are installed, do not move the installation to a CPU
without x86-64-v3 support. Newer-variant packages cannot run reliably on older
hardware, and removing the APT opt-in does not replace packages that are already
installed. See Ubuntu's [26.04 release notes][ubuntu-2604-amd64v3] and
[supported-architecture documentation][ubuntu-architecture-variants].

[ubuntu-2604-amd64v3]: https://documentation.ubuntu.com/release-notes/26.04/summary-for-lts-users/#architecture-variants-and-amd64v3
[ubuntu-architecture-variants]: https://documentation.ubuntu.com/project/how-ubuntu-is-made/concepts/supported-architectures/#architecture-variants

## Step 1: Install Ansible

```bash
sudo apt update && sudo apt install -y git ansible
```

## Step 2: Run ansible-pull

```bash
sudo ansible-pull -U https://github.com/lab1702/setup.git
```

The playbook adds the workstation user to the `docker` group and, on desktop
systems, the `kvm` group. Log out and back in or reboot before using Docker or
KVM so the new login session receives those memberships. For Docker, running
`newgrp docker` can instead activate the membership in a new shell.

---

## Python and NPM shell configuration

The playbook uses idempotent Ansible tasks to require a virtual environment for
user-level pip installations, configure `~/.npm-global` as the user's NPM
prefix, and add its `bin` directory and `~/go/bin` (for Go-installed tools) to
`PATH`. Existing matching entries in `.bashrc` and `.npmrc` are updated, and
duplicate legacy entries are collapsed.

## Running the test playbooks

The repository tracks regression tests for the shared repository sandbox
(one per keyring format: `chatgpt` covers a deb822 source with a binary
`.gpg` keyring, `claude_desktop` covers a deb822 source with an armored
`.asc` keyring) and for the `amd64v3` role (a full run in an isolated apt
sandbox, a check-mode run, and a current-CPU detection run). The tests
source their repository URLs, fingerprints, and platform values from the
role defaults, so they follow key rotations and support changes
automatically. Run them from the repository root, where `ansible.cfg`
resolves the roles; the repository-metadata tests support `--check` and
the check-mode test requires it:

```bash
ansible-playbook --check roles/chatgpt/tests/check_mode_repository_metadata.yml
```

```bash
ansible-playbook --check roles/claude_desktop/tests/check_mode_repository_metadata.yml
```

```bash
ansible-playbook roles/amd64v3/tests/main.yml
```

```bash
ansible-playbook --check roles/amd64v3/tests/check_mode.yml
```

```bash
ansible-playbook roles/amd64v3/tests/current_cpu.yml
```

## Optional: Setup Git Authentication

Step A:

```bash
git config --global user.name "abc"
```

Step B:

```bash
git config --global user.email "abc@gmail.com"
```

Step C:

```bash
gh auth login
```

Step D:

```bash
gh auth setup-git
git config --global init.defaultBranch main
```
