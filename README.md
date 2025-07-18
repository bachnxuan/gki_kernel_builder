# GKI Kernel Builder

[![codecov](https://codecov.io/gh/bachnxuan/gki_kernel_builder/graph/badge.svg?token=EYKHK1OOC4)](https://codecov.io/gh/bachnxuan/gki_kernel_builder) [![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?logo=telegram&logoColor=white)](https://t.me/xaga_kernel)

Effortlessly building Android Generic Kernel Image (GKI).

---

## Table of Contents

- [Requirements](#requirements)
- [Setup Kernel Builder](#setup-kernel-builder)
- [Build the kernel](#build-the-kernel)
  - [Quick Start](#quick-start)
  - [CLI Structure](#cli-structure)
  - [Example Commands](#example-commands)
- [GitHub Workflows](#github-workflows)
- [Configuration](#configuration)
- [License](#license)

---

## Requirements

- Ubuntu/Debian-based Linux
- Python 3.12+

Install dependencies:

```bash
sudo apt update
sudo apt install bc bison ccache curl flex git tar wget aria2 jq

python3 -m pip install uv
```

---

## Setup Kernel Builder

1. **Clone the repository**:

   ```bash
   git clone https://github.com/bachnxuan/gki_kernel_builder.git
   cd gki_kernel_builder
   ```

2. **Set up venv**:

   ```bash
   uv sync --frozen --no-install-project
   source .venv/bin/activate
   ```

   Once you are finished working with the project, disable the virtual environment (venv) via `deactivate`.

## Build the kernel

Builds are performed via the custom wrapper script `cli.py`

### Quick Start

To build your kernel with default configuration:

uv run cli.py build

### CLI Structure

The CLI consists of the following commands:

build – Configure and compile the kernel

clean – Clean up build artifacts

View all available options:

```bash
uv run cli.py --help
```

### Example Commands

Build KernelSU NEXT with SUSFS (no LXC):

```bash
uv run cli.py build -k NEXT -s
```

Build SukiSU with verbose logging, SUSFS and LXC disabled:

```bash
uv run cli.py build --verbose --ksu SUKI --no-susfs --no-lxc
```

> [!TIP]
> Use `--verbose` or `-v` to see detailed logs, great for debugging!

---

## GitHub Workflows

1. **Fork** this repo to your GitHub account.

2. **Add secret** `GH_TOKEN`
   - PAT scopes (read and write): `workflow`, `content`
   - Add PAT access to your release and kernel builder repo
   - Repo → Settings → Secrets → Actions → **New secret**.

3. **Optional Telegram secrets**

> [!NOTE]
> Add the below Telegram secrets below when you want to notify completed build on Telegram.
> The Telegram notify feature can be config via `NOTIFY` on workflows_dispatch and workflows_call input.

- `TG_BOT_TOKEN` – Telegram Bot Token
- `TG_CHAT_ID` – Telegram Chat ID

---

## Configuration

> [!WARNING]
> If you build a GKI kernel for devices other than xaga (ESK Kernel), set LXC to false or remove the LXC function entirely.

Customize your build by:

- `config/config.py` – Contains kernel configuration settings.
- `config/manifest.py` – Specifies repository sources and branches.
- `kernel_builder.py` – The main script responsible for orchestrating the build.

> [!NOTE]
> See the dedicated guide for more information: [Kernel Builder Configuration guide](https://github.com/bachnxuan/gki_kernel_builder/tree/master/kernel_builder/config)

---

## License

This project is distributed under the [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html). See `LICENSE` for details.
