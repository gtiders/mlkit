import typer
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Although pandas/matplotlib are direct dependencies now,
# strictly following "Lazy Loading" rule in AI_RULES:
# "如果用户选择懒加载... 严禁在该文件的顶层 global scope 进行 import"
# BUT user chose "Direct Add" (A). So top level import is ALLOWED.
# Proceeding with top level imports for better developer experience (type hints etc).


def plot_scph_bands(file_path: Path):
    if not file_path.exists():
        typer.echo(f"错误: 文件不存在 {file_path}", err=True)
        raise typer.Exit(1)

    file_name = file_path.stem

    try:
        data = pd.read_csv(
            file_path,
            sep=r"\s+",
            comment="#",
            header=None,
            skip_blank_lines=False,
        )
    except Exception as e:
        typer.echo(f"读取文件失败: {e}", err=True)
        raise typer.Exit(1)

    # Extract unique temperatures
    # Column 0 is Temperature
    try:
        Ts = sorted(set(x for x in data[0] if pd.notna(x)))
    except Exception as e:
        typer.echo(f"数据解析失败: {e}", err=True)
        raise typer.Exit(1)

    cmap = plt.cm.YlOrRd
    colors = cmap(np.linspace(0, 1, len(Ts)))

    plt.figure(figsize=(10, 8))

    # Plot data
    for index, T in enumerate(Ts):
        df = data[data[0] == T]
        # Columns 0=T, 1=Index?, 2...=Frequencies?
        # Script said: for i in range(2, df.shape[1]): plot(df[1], df[i] * factor)
        for i in range(2, df.shape[1]):
            plt.plot(df[1], df[i] * 0.0299792458, color=colors[index])

    plt.xlabel("Index")
    plt.ylabel(
        "Frequency (THz)"
    )  # Added unit based on conversion factor (cm-1 to THz?) 0.0299... is cm-1 to THz usually ~0.029979.
    plt.title(f"Band Structure: {file_name}")

    output_file = Path(f"{file_name}.png")
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    typer.echo(f"图片已保存为: {output_file}")


def main(
    file_path: Path = typer.Argument(..., help="SCPH 能带数据文件路径"),
):
    """
    绘制 SCPH 修正后的声子谱 (Band Structure)。
    自动读取数据并保存为 PNG 图片，不显示弹窗。
    """
    plot_scph_bands(file_path)
