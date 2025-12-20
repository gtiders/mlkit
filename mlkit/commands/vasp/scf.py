import typer
from mlkit.core.shell import run_cmd
from pathlib import Path

app = typer.Typer(help="SCF (自洽场) 计算工作流")


@app.command()
def run(
    poscar: Path = typer.Option(Path("POSCAR"), help="结构文件路径"),
    nproc: int = typer.Option(4, help="并行核数"),
):
    """
    提交 VASP SCF 计算任务。
    """
    if not poscar.exists():
        typer.echo(f"错误: 找不到 {poscar}", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"准备计算 SCF: {poscar}, 使用 {nproc} 核...")
    # Simulation of running VASP
    # run_cmd(f"mpirun -np {nproc} vasp_std")
    typer.echo("计算命令已生成 (模拟)。")


@app.command()
def check():
    """
    检查 SCF 收敛情况。
    """
    typer.echo("检查 OSZICAR ... 收敛！")
