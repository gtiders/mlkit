import json
from pathlib import Path
from typing import Optional

import numpy as np
import typer
from mlkit.core.shell import run_cmd

app = typer.Typer(help="导出 transport 数据并批量绘图")


def _create_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _save_mobility_data(temperatur, transport, carrier_type: str) -> None:
    for idx, T in enumerate(temperatur):
        mobility_dir = Path(f"data/{T}K/mobility")
        _create_directory(mobility_dir)

        mobility_data = transport.get("mobility")
        for key in mobility_data.keys():
            key_doping = []
            key_xx = []
            key_yy = []
            key_zz = []

            for index, dop in enumerate(transport.get("doping")):
                if (carrier_type == "ntype" and dop > 0) or (carrier_type == "ptype" and dop <= 0):
                    continue
                key_doping.append(dop)
                key_xx.append(mobility_data[key][index][idx][0][0])
                key_yy.append(mobility_data[key][index][idx][1][1])
                key_zz.append(mobility_data[key][index][idx][2][2])

            key_doping = np.array(key_doping)
            key_xx, key_yy, key_zz = np.array(key_xx), np.array(key_yy), np.array(key_zz)
            key_avg = (key_xx + key_yy + key_zz) / 3
            data = np.array([key_doping, key_xx, key_yy, key_zz, key_avg]).T

            np.savetxt(
                mobility_dir / f"{carrier_type}_{key}.dat",
                data,
                fmt="%.8e",
                delimiter=",  ",
                header=(
                    f"T={T}K\nx-axis: Carrier concentration (cm^{{-3}})\n"
                    "y-axis: Mobility (cm^2/Vs)\ndoping,  xx,  yy,  zz,  avg"
                ),
            )


def _plot_transport_data(temperatur, transport_file: Path, amset_executable: str, no_mobility: bool) -> None:
    for idx, T in enumerate(temperatur):
        base_dir = Path(f"data/{T}K")
        _create_directory(base_dir)

        for carrier_type, average in [
            ("n-type", True),
            ("p-type", True),
            ("n-type", False),
            ("p-type", False),
        ]:
            plot_dir = base_dir / f"{carrier_type}_{'average' if average else 'not_average'}"
            _create_directory(plot_dir)

            average_flag = "--average" if average else "--no-average"
            carrier_flag = "--n-type" if carrier_type == "n-type" else "--p-type"

            cmd = [
                amset_executable,
                "plot",
                "transport",
                "-t",
                str(idx),
                carrier_flag,
                average_flag,
                *(["--mobility"] if not no_mobility else []),
                "--conductivity",
                "--seebeck",
                "--thermal-conductivity",
                "--power-factor",
                "--directory",
                str(plot_dir),
                "--gnuplot",
                str(transport_file),
            ]

            result = run_cmd(cmd, check=False)
            if result.returncode != 0:
                typer.echo(f"Error running amset for T={T}K, {carrier_type}:", err=True)
                if result.stderr:
                    typer.echo(result.stderr, err=True)


@app.command(name="main")
def main(
    transport_file: Path = typer.Argument(..., exists=True, help="transport JSON 数据文件路径"),
    amset_path: Optional[str] = typer.Option(
        "amset", "--amset-path", help="amset 可执行路径（默认 'amset'）"
    ),
    no_mobility: bool = typer.Option(
        False, "--no-mobility", help="禁用 mobility 数据处理与绘图"
    ),
) -> None:
    """
    导出 transport 数据，调用 amset 生成图像，并按温度输出 mobility 数据。
    """
    try:
        transport = json.loads(transport_file.read_text())
        typer.echo(f"Keys in transport data: {list(transport.keys())}")
    except json.JSONDecodeError:
        typer.echo(f"Error: {transport_file} 不是有效 JSON 文件", err=True)
        raise typer.Exit(code=1)

    temperatur = transport.get("temperatures")
    if temperatur is None:
        typer.echo("Error: transport 数据缺少 'temperatures' 字段", err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Temperatures: {temperatur}")

    amset_exe = amset_path or "amset"
    try:
        run_cmd([amset_exe, "--version"], check=False)
        typer.echo(f"Using amset executable: {amset_exe}")
    except FileNotFoundError:
        typer.echo(f"Warning: 找不到 amset 可执行文件 '{amset_exe}'", err=True)

    _plot_transport_data(temperatur, transport_file, amset_exe, no_mobility)

    if not no_mobility:
        typer.echo("Processing mobility data...")
        _save_mobility_data(temperatur, transport, "ntype")
        _save_mobility_data(temperatur, transport, "ptype")
    else:
        typer.echo("Skipping mobility data (--no-mobility 已启用)")

    typer.echo("如果想获得 scattering rate 数据请修改 amset plot 类的源代码!")

