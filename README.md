# Ubuntu Developer Workstation Setup

## Step 0: Setup up fingerprint Authentication
_If applicable do this after enrolling your fingerprint_

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

## Optional: Setup Claude Code CLI

```bash
curl -fsSL https://claude.ai/install.sh | bash
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
