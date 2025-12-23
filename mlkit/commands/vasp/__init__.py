import typer

from . import jobs

app = typer.Typer(help="VASP 相关计算工具")

app.add_typer(jobs.app, name="jobs")
