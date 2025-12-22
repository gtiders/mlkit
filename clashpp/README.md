# Clashpp - Portable Rootless Proxy Manager

Clashpp is a lightweight, portable, and rootless proxy manager wrapper for [Mihomo](https://github.com/MetaCubeX/mihomo). It manages the proxy kernel process and handles environment variables for your shell.

## Features

- **Portable**: Everything is contained within the `clashpp` directory.
- **Rootless**: No `sudo` or `systemd` required.
- **Zero Dependency**: Auto-bootstraps `PyYAML` from source (dynamically fetched from PyPI). Works with any standard `python3` (3.6+).
- **Auto-Update**: Fetches the latest compatible Mihomo kernel automatically.
- **Shell Integration**: Simple `clashon` and `clashoff` commands.
- **Multi-Env Support**: Specify custom python interpreter via `--python`.

## Quick Start

1. **Setup Environment**
   Source the shell script to load the functions:

   ```bash
   source clashpp/clashpp.sh
   ```

   *Alternatively, you can install the kernel directly:*

   ```bash
   bash clashpp/clashpp.sh install
   ```

2. **Configure (First Run)**
   Provide your subscription URL to download config and kernel.

   ```bash
   clashupdate --url "YOUR_SUBSCRIPTION_URL"
   ```

3. **Start Proxy**

   ```bash
   clashon
   ```

   *Starts the background process and sets `http_proxy` variables.*

4. **Stop Proxy**

   ```bash
   clashoff
   ```

   *Stops process and unsets variables.*

## Configuration & Usage

### Specifying Python Path

You can use a specific python interpreter for any command using `--python`:

```bash
clashon --python /path/to/venv/bin/python
bash clashpp/clashpp.sh install --python /usr/local/bin/python3.9
```

### Help

Append `--help` to any command to see available options:

```bash
clashon --help
clashupdate --help
bash clashpp/clashpp.sh --help
```

### Manual Kernel Installation

If automatic download fails:

1. Download `mihomo-linux-amd64-compatible-vX.Y.Z.gz`.
2. Extract and rename to `clashpp/bin/mihomo`.
3. `chmod +x clashpp/bin/mihomo`.

## Commands Reference

| Command | Description |
|---|---|
| `clashon` | Start proxy and export env vars. |
| `clashoff` | Stop proxy and unset env vars. |
| `clashui` | Show status and controller info. |
| `clashupdate` | Update subscription or kernel (`--kernel`). |
| `clashinstall` | Install/Reinstall kernel only. |
