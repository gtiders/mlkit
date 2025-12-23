import typer

from . import xml2xyz

app = typer.Typer(help="通用小工具集合")

app.command(name="xml2xyz")(xml2xyz.main)

