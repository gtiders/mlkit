import typer
from . import (
    scf,
)  # Import submodules to ensure they are registered if using a pattern where they attach to this app.
# OR, better protocol:
# We define the app here, and submodules import it to attach commands.

app = typer.Typer(help="VASP 相关计算工具")

# We can either attach sub-apps or commands directly.
# Let's verify the protocol: "mlkit vasp scf" -> usage: mlkit vasp [OPTIONS] COMMAND [ARGS]...
# So 'scf' should be a command under 'vasp'.

app.add_typer(scf.app, name="scf")
