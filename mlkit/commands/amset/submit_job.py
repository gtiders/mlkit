from pathlib import Path
from typing import Optional

import typer
from mlkit.core.shell import run_cmd

app = typer.Typer(help="生成并提交 AMSET PBS 作业脚本")


def _write_script(amset_path: str, script_path: Path) -> None:
    content = f"""#!/bin/bash
#PBS -S /bin/bash
#PBS -l walltime=600:00:00
#PBS -q six_hours
#PBS -l nodes=1:ppn=40
#PBS -N amset_run
#PBS -V

cd ${{PBS_O_WORKDIR}}

export OMP_NUM_THREADS=1

{amset_path} run
"""
    script_path.write_text(content, encoding="utf-8")


@app.command(name="main")
def main(
    amset_path: Optional[str] = typer.Option(
        "amset", "--amset-path", help="amset 可执行路径（默认使用 PATH 中的 amset）"
    ),
    script_path: Path = typer.Option(Path("amset_jobs"), help="生成的脚本文件名"),
) -> None:
    """
    生成 AMSET PBS 作业脚本并调用 qsub 提交。
    """
    _write_script(amset_path or "amset", script_path)
    typer.echo(f"已创建作业脚本 '{script_path}'，使用 amset: {amset_path}")

    result = run_cmd(["qsub", str(script_path)], cwd=".")
    if result.stdout:
        typer.echo(result.stdout.strip())
    if result.stderr:
        typer.echo(result.stderr.strip(), err=True)
    typer.echo(f"返回码: {result.returncode}")

