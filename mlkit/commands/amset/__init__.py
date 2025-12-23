import typer

from . import export_data, submit_job, write_settings

app = typer.Typer(help="AMSET 相关工具集")

app.command(name="submit-job")(submit_job.main)
app.command(name="export-data")(export_data.main)
app.command(name="write-settings")(write_settings.main)

