import subprocess
import logging
from typing import Optional, List


# Configure basic logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("mlkit")


def run_cmd(
    cmd: str | List[str], cwd: Optional[str] = None, check: bool = True
) -> subprocess.CompletedProcess:
    """
    Execute a shell command with consistent logging and error handling.
    """
    if isinstance(cmd, str):
        # logging the command as string
        logger.info(f"Running: {cmd}")
        args = cmd
        shell_mode = True
    else:
        logger.info(f"Running: {' '.join(cmd)}")
        args = cmd
        shell_mode = False

    try:
        result = subprocess.run(
            args, cwd=cwd, check=check, shell=shell_mode, text=True, capture_output=True
        )
        if result.stdout:
            logger.debug(f"STDOUT: {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e.cmd}")
        logger.error(f"STDERR: {e.stderr}")
        raise e
