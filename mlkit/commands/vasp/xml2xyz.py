import typer
from pathlib import Path
from ase.io import read
from ase.io.extxyz import write_extxyz
from typing import List

app = typer.Typer(help="VASP 文件格式转换工具")

def process_file(file_path: Path) -> List:
    """读取单个文件并返回 Atoms 对象列表"""
    try:
        # read returns a list if index is specified, or single Atoms if not but here we want generic read
        # For vasprun.xml, read usually returns the last image or list if index=':'.
        # Using index=':' to capture all frames if trajectory, or single frame.
        # But 'read(path)' on vasprun.xml typically reads the last frame by default in ASE.
        # If user wants trajectory, maybe we should use index=':'.
        # Let's assume user wants to collect structures. 
        # Original script: result_forces.append(read(path)) -> implies single structure per file (or last frame).
        # We will stick to `read(path)` to match user script logic.
        atoms = read(file_path)
        return [atoms]
    except Exception as e:
        typer.echo(f"读取失败 {file_path}: {e}", err=True)
        return []

@app.command(name="run")
def main(
    input_path: Path = typer.Argument(..., help="输入文件或目录路径"),
    output: Path = typer.Option(Path("output.xyz"), "-o", "--output", help="输出 XYZ 文件路径"),
    pattern: str = typer.Option("vasprun.xml", help="目录搜索时的文件名匹配模式"),
):
    """
    将 vasprun.xml 转换为/合并为 extxyz 格式。
    支持输入单个文件或目录（递归搜索）。
    """
    all_atoms = []

    if input_path.is_file():
        typer.echo(f"正在处理单文件: {input_path}")
        all_atoms.extend(process_file(input_path))
    elif input_path.is_dir():
        typer.echo(f"正在目录 '{input_path}' 中递归搜索 '{pattern}'...")
        files = list(input_path.rglob(pattern))
        typer.echo(f"找到 {len(files)} 个文件。")
        
        with typer.progressbar(files, label="处理中") as progress:
            for file_path in progress:
                all_atoms.extend(process_file(file_path))
    else:
        typer.echo(f"错误: 路径不存在 {input_path}", err=True)
        raise typer.Exit(1)

    if not all_atoms:
        typer.echo("警告: 未提取到任何结构数据。", err=True)
        raise typer.Exit(1)

    typer.echo(f"正在写入 {len(all_atoms)} 个结构到 {output}...")
    write_extxyz(output, all_atoms)
    typer.echo("完成。")
