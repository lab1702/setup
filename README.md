# Ubuntu Developer Workstation Setup

This playbook supports Ubuntu 26.04 on AMD64 and ARM64 systems.
Desktop packages are installed when an X11 or Wayland desktop session is
available. Posit RStudio Desktop, Discord, Zoom, and Visual Studio Code are
installed only on AMD64 systems because their configured distribution channels
do not publish ARM64 packages. Ruff, ty, uv, and uvx track the latest GitHub
releases for AMD64 and ARM64; their release archives are verified with the
SHA-256 digests published by GitHub before installation. Zoom Workplace tracks
the latest package from Zoom's signed, AMD64-only APT repository.

## Accepted Security Tradeoffs

This repository is intended for a personally managed, single-user workstation
on a trusted home network. The following security review items are accepted for
that use case:

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

Reassess these decisions before using the playbook on a shared workstation, an
untrusted network, infrastructure managed by multiple people, or a host whose
SSH service is exposed to the internet.

## Step 0: Setup up fingerprint Authentication

### If applicable do this after enrolling your fingerprint

```bash
sudo pam-auth-update
```

## Step 1: Enable AMD64v3 CPU Optimizations (AMD64 only)

Skip this step on ARM64 workstations. On AMD64, confirm that the CPU supports
the x86-64-v3 feature level before enabling this setting.

```bash
echo 'APT::Architecture-Variants "amd64v3";' | sudo tee /etc/apt/apt.conf.d/99enable-amd64v3
sudo apt update && sudo apt upgrade -y
```

## Step 2: Install Ansible

```bash
sudo apt update && sudo apt upgrade -y &&  sudo apt install -y git ansible
```

The Ubuntu `ansible` package includes the required `community.general`
collection. When using `ansible-core` from a repository checkout instead,
install the declared collection dependency for the same account that will run
the playbook:

```bash
sudo ansible-galaxy collection install -r collections/requirements.yml
```

## Step 3: Run ansible-pull

```bash
sudo ansible-pull -U https://github.com/lab1702/setup.git
```

---

## Optional: Setup pip

```bash
echo 'export PIP_REQUIRE_VIRTUALENV=1' >> ~/.bashrc
```

## Optional: Setup NPM

```bash
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
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
