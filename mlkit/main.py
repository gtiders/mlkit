import typer
import importlib
import pkgutil
from pathlib import Path
from mlkit import commands
import logging

# Setup Logger
logger = logging.getLogger("mlkit")

app = typer.Typer(
    help="mlkit: The AI-maintained swiss army knife for scientific scripts.",
    no_args_is_help=True,
)


def register_subcommands():
    """
    Dynamically discover and register subcommands from the 'mlkit.commands' package.
    Protocol:
    - Every subdirectory in mlkit/commands/ is a potential sub-app.
    - It must have an __init__.py.
    - It must expose an 'app' object (typer.Typer).
    """
    command_path = Path(commands.__file__).parent

    # Iterate over modules in the commands directory
    for _, name, is_pkg in pkgutil.iter_modules([str(command_path)]):
        if is_pkg:
            try:
                # Import the module: e.g. mlkit.commands.vasp
                module = importlib.import_module(f"mlkit.commands.{name}")

                # Look for 'app' object
                if hasattr(module, "app") and isinstance(module.app, typer.Typer):
                    app.add_typer(module.app, name=name)
                    logger.debug(f"Registered subcommand group: {name}")
                else:
                    logger.warning(
                        f"Module mlkit.commands.{name} does not expose an 'app' Typer object."
                    )
            except Exception as e:
                logger.error(f"Failed to load subcommand {name}: {e}")


@app.callback()
def main_callback(verbose: bool = False):
    """
    Global options for mlkit.
    """
    if verbose:
        logging.getLogger("mlkit").setLevel(logging.DEBUG)


# Register subcommands on module import
try:
    register_subcommands()
except Exception as e:
    logger.error(f"Error during subcommand registration: {e}")

if __name__ == "__main__":
    app()
