#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml"]
# ///
import os
import sys
import argparse
import subprocess
import shutil
import urllib.request
import urllib.error
import gzip
import time
import socket
import re
import tarfile
from pathlib import Path

# Constants
BASE_DIR = Path(__file__).resolve().parent
BIN_DIR = BASE_DIR / "bin"
CONF_DIR = BASE_DIR / "conf"
LOGS_DIR = BASE_DIR / "logs"
LIBS_DIR = BASE_DIR / "libs"

KERNEL_NAME = "mihomo"
KERNEL_BIN = BIN_DIR / KERNEL_NAME
PID_FILE = BASE_DIR / "run.pid"
CONFIG_RAW = CONF_DIR / "config.yaml"
CONFIG_RUNTIME = CONF_DIR / "runtime.yaml"
SUBSCRIPTION_URL_FILE = CONF_DIR / ".url"

# GitHub Release Info
REPO_OWNER = "MetaCubeX"
REPO_NAME = "mihomo"
ASSET_PATTERN = r"mihomo-linux-amd64-compatible-v.*\.gz"

# Global yaml module placeholder
yaml = None


def log(msg, level="INFO"):
    print(f"[{level}] {msg}")


def error_exit(msg):
    log(msg, "ERROR")
    sys.exit(1)


def get_latest_pyyaml_url():
    """Fetch the latest PyYAML source distribution URL from PyPI."""
    pypi_api_url = "https://pypi.org/pypi/PyYAML/json"
    try:
        with urllib.request.urlopen(pypi_api_url) as response:
            import json

            data = json.loads(response.read().decode())
            latest_version = data["info"]["version"]
            for url_data in data["urls"]:
                if url_data["packagetype"] == "sdist":
                    return url_data["url"]
            error_exit(f"No source distribution found for PyYAML {latest_version}")
    except Exception as e:
        error_exit(f"Failed to fetch PyYAML info from PyPI: {e}")


def ensure_yaml():
    global yaml
    try:
        import yaml as y

        yaml = y
        return
    except ImportError:
        pass

    # Check local libs
    sys.path.append(str(LIBS_DIR))
    try:
        import yaml as y

        yaml = y
        return
    except ImportError:
        pass

    log("PyYAML not found. Bootstrapping...")

    if not LIBS_DIR.exists():
        LIBS_DIR.mkdir()

    pyyaml_url = get_latest_pyyaml_url()
    tgz_path = LIBS_DIR / "pyyaml.tar.gz"
    log(f"Downloading PyYAML from {pyyaml_url}...")
    try:
        with (
            urllib.request.urlopen(pyyaml_url) as response,
            open(tgz_path, "wb") as out_file,
        ):
            shutil.copyfileobj(response, out_file)
    except Exception as e:
        error_exit(f"Failed to download PyYAML: {e}")

    log("Extracting PyYAML...")
    try:
        with tarfile.open(tgz_path, "r:gz") as tar:
            # We need to extract the 'lib/yaml' dir from inside the tar
            # Structure is usually PyYAML-6.0.1/lib/yaml

            # Helper to filter members
            members_to_extract = []
            for member in tar.getmembers():
                if "/lib/yaml" in member.name:
                    members_to_extract.append(member)

            if not members_to_extract:
                error_exit("Could not find lib/yaml in PyYAML archive.")

            # Extract to temp, then move? Or extract directly
            # We want libs/yaml/ -> content
            # Tar extracts full path: PyYAML-6.0.1/lib/yaml/...

            tar.extractall(path=LIBS_DIR, members=members_to_extract)

            # Move out of nested dir
            # Find the lib/yaml dir
            extracted_root = None
            for item in LIBS_DIR.iterdir():
                if item.is_dir() and item.name.startswith("PyYAML"):
                    extracted_root = item
                    break

            if extracted_root:
                lib_yaml = extracted_root / "lib" / "yaml"
                target_yaml = LIBS_DIR / "yaml"
                if target_yaml.exists():
                    shutil.rmtree(target_yaml)
                shutil.move(str(lib_yaml), str(target_yaml))
                shutil.rmtree(extracted_root)  # Cleanup source dir

        tgz_path.unlink()
        log("PyYAML bootstrapped successfully.")

        # Retry import
        import yaml as y

        yaml = y

    except Exception as e:
        error_exit(f"Failed to bootstrap PyYAML: {e}")


def check_dependencies():
    """Check for required system dependencies."""
    if not shutil.which("gzip"):
        error_exit("gzip is required but not found.")


def get_latest_version_tag():
    url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/latest"
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req) as response:
            real_url = response.geturl()
            match = re.search(r"/tag/(v[\d\.]+)", real_url)
            if match:
                return match.group(1)
            else:
                error_exit(f"Could not parse version tag from URL: {real_url}")
    except Exception as e:
        error_exit(f"Failed to fetch latest version info: {e}")


def install_or_update(force=False):
    if KERNEL_BIN.exists() and not force:
        log("Kernel already exists. Use --update to force update.")
        return

    log("Checking for latest version...")
    tag = get_latest_version_tag()
    log(f"Latest version found: {tag}")

    filename = f"mihomo-linux-amd64-compatible-{tag}.gz"
    download_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{tag}/{filename}"

    dest_gz = BIN_DIR / filename

    log(f"Downloading {download_url}...")
    try:
        with (
            urllib.request.urlopen(download_url) as response,
            open(dest_gz, "wb") as out_file,
        ):
            shutil.copyfileobj(response, out_file)
    except Exception as e:
        error_exit(f"Download failed: {e}")

    log("Extracting...")
    try:
        with gzip.open(dest_gz, "rb") as f_in:
            with open(KERNEL_BIN, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        KERNEL_BIN.chmod(0o755)
        dest_gz.unlink()
        log("Installation completed.")
    except Exception as e:
        error_exit(f"Extraction failed: {e}")


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def find_available_port(start_port):
    port = start_port
    while is_port_in_use(port):
        port += 1
        if port > 65535:
            error_exit("No available ports found.")
    return port


def load_config(url=None):
    if url:
        log(f"Downloading configuration from {url}...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "clashpp/1.0"})
            with (
                urllib.request.urlopen(req) as response,
                open(CONFIG_RAW, "wb") as out_file,
            ):
                shutil.copyfileobj(response, out_file)
            with open(SUBSCRIPTION_URL_FILE, "w") as f:
                f.write(url)
        except Exception as e:
            error_exit(f"Config download failed: {e}")

    if not CONFIG_RAW.exists():
        error_exit("No configuration file found. Please provide a subscription URL.")

    # Process config using yaml (now available)
    log("Processing configuration...")
    try:
        with open(CONFIG_RAW, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        mixed_port = config.get("mixed-port", 7890)
        ext_ctrl = config.get("external-controller", "127.0.0.1:9090")

        if isinstance(ext_ctrl, str):
            if ":" in ext_ctrl:
                ctrl_port = int(ext_ctrl.split(":")[-1])
            else:
                ctrl_port = 9090
        else:
            ctrl_port = 9090

        if is_port_in_use(mixed_port):
            new_port = find_available_port(mixed_port + 1)
            log(f"Port {mixed_port} is busy, using {new_port} for mixed-port")
            config["mixed-port"] = new_port

        if is_port_in_use(ctrl_port):
            new_port = find_available_port(ctrl_port + 1)
            log(f"Port {ctrl_port} is busy, using {new_port} for external-controller")
            host_part = ext_ctrl.split(":")[0] if ":" in ext_ctrl else "127.0.0.1"
            config["external-controller"] = f"{host_part}:{new_port}"

        with open(CONFIG_RUNTIME, "w", encoding="utf-8") as f:
            yaml.dump(config, f)

        log(f"Configuration generated at {CONFIG_RUNTIME}")
        return config

    except Exception as e:
        error_exit(f"Config processing failed: {e}")


def start_proxy():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 0)
            log("Clashpp is already running.")
            return
        except ProcessLookupError:
            log("Stale PID file found. Removing.")
            PID_FILE.unlink()
        except Exception as e:
            error_exit(f"Error checking PID: {e}")

    if not KERNEL_BIN.exists():
        install_or_update()

    config = load_config()

    log("Starting mihomo kernel...")
    log_file = open(LOGS_DIR / "mihomo.log", "w")

    try:
        proc = subprocess.Popen(
            [str(KERNEL_BIN), "-d", str(BASE_DIR), "-f", str(CONFIG_RUNTIME)],
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd=BASE_DIR,
            start_new_session=True,
        )
        PID_FILE.write_text(str(proc.pid))
        log(f"Started successfully. PID: {proc.pid}")

        mixed_port = config.get("mixed-port", 7890)
        print(f"\nProxy is running on port {mixed_port}")
        print("Run the following to verify:")
        print(f"  export https_proxy=http://127.0.0.1:{mixed_port}")
        print("  curl -I https://google.com\n")

    except Exception as e:
        error_exit(f"Failed to start process: {e}")


def stop_proxy():
    if not PID_FILE.exists():
        log("No running process found.")
        return

    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, 15)
        time.sleep(1)
        try:
            os.kill(pid, 0)
            os.kill(pid, 9)
        except ProcessLookupError:
            pass
        log("Stopped successfully.")
    except ProcessLookupError:
        log("Process not found.")
    except Exception as e:
        log(f"Error stopping process: {e}", "WARN")
    finally:
        if PID_FILE.exists():
            PID_FILE.unlink()


def status():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 0)
            print(f"Status: Running (PID {pid})")

            if CONFIG_RUNTIME.exists():
                with open(CONFIG_RUNTIME) as f:
                    c = yaml.safe_load(f)
                    print(f"Mixed Port: {c.get('mixed-port', 'N/A')}")
                    print(f"Controller: {c.get('external-controller', 'N/A')}")
            return
        except ProcessLookupError:
            print("Status: Stale PID file (Process dead)")
            return
    print("Status: Stopped")


def main():
    # Ensure dependencies first
    ensure_yaml()

    parser = argparse.ArgumentParser(description="Clashpp: Portable Rootless Proxy")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("start", help="Start the proxy")
    subparsers.add_parser("stop", help="Stop the proxy")
    subparsers.add_parser("restart", help="Restart the proxy")
    subparsers.add_parser("status", help="Check status")
    subparsers.add_parser("install", help="Install mihomo kernel")
    subparsers.add_parser("env", help="Output export commands for shell")

    update_parser = subparsers.add_parser(
        "update", help="Update kernel or subscription"
    )
    update_parser.add_argument("--url", help="New subscription URL")
    update_parser.add_argument(
        "--kernel", action="store_true", help="Force update kernel"
    )

    args = parser.parse_args()

    check_dependencies()

    if args.command == "start":
        start_proxy()
    elif args.command == "stop":
        stop_proxy()
    elif args.command == "restart":
        stop_proxy()
        start_proxy()
    elif args.command == "status":
        status()
    elif args.command == "install":
        install_or_update(force=True)
    elif args.command == "env":
        if PID_FILE.exists() and CONFIG_RUNTIME.exists():
            try:
                with open(CONFIG_RUNTIME) as f:
                    c = yaml.safe_load(f)
                    port = c.get("mixed-port", 7890)
                    print(f"export http_proxy=http://127.0.0.1:{port}")
                    print(f"export https_proxy=http://127.0.0.1:{port}")
                    print(f"export all_proxy=socks5://127.0.0.1:{port}")
            except Exception:
                pass
    elif args.command == "update":
        if args.kernel:
            install_or_update(force=True)

        url_to_use = args.url
        if not url_to_use and SUBSCRIPTION_URL_FILE.exists():
            url_to_use = SUBSCRIPTION_URL_FILE.read_text().strip()

        if url_to_use:
            load_config(url_to_use)
            if args.command == "update" and not args.kernel:
                if PID_FILE.exists():
                    log("Reloading config by restarting...")
                    stop_proxy()
                    start_proxy()
        elif not args.kernel:
            log(
                "No URL provided and no existing subscription found. Nothing to update."
            )


if __name__ == "__main__":
    main()
