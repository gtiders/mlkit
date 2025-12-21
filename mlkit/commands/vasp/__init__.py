import typer
from . import scf, xml2xyz

app = typer.Typer(help="VASP 相关计算工具")

# We can either attach sub-apps or commands directly.
# "mlkit vasp scf" -> usage: mlkit vasp [OPTIONS] COMMAND [ARGS]...
# So 'scf' should be a command under 'vasp'.

app.add_typer(scf.app, name="scf")
app.command(name="xml2xyz")(xml2xyz.main)
