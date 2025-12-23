import typer

from . import write_control

app = typer.Typer(help="ShengBTE 相关工具")

app.command(name="write-control")(write_control.main)

