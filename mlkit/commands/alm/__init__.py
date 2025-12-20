import typer
from . import prepare, scph_bands

app = typer.Typer(help="ALAMODE 相关工具")

app.add_typer(prepare.app, name="prepare")
app.command(name="plot-scph-bands")(scph_bands.main)
