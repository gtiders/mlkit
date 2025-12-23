from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(help="生成 ShengBTE CONTROL 文件")


@app.command(name="main")
def main(
    poscar: Path = typer.Argument(..., help="POSCAR 文件路径"),
    sx: int = typer.Argument(..., help="超胞尺寸 x (scell[0])"),
    sy: int = typer.Argument(..., help="超胞尺寸 y (scell[1])"),
    sz: int = typer.Argument(..., help="超胞尺寸 z (scell[2])"),
    is_born: bool = typer.Option(False, "--is-born", help="是否启用 Born 有效电荷，需要 OUTCAR"),
    outcar: Optional[Path] = typer.Option(None, "--outcar", help="OUTCAR 路径，启用 --is-born 必填"),
    output: Path = typer.Option(Path("CONTROL"), "-o", "--output", help="输出 CONTROL 文件路径"),
) -> None:
    """
    根据 POSCAR 与超胞尺寸生成 ShengBTE CONTROL 文件。
    """
    # 懒加载依赖以降低启动成本
    import f90nml  # type: ignore
    from pymatgen.core.structure import Structure
    from pymatgen.io.vasp.outputs import Outcar

    if not poscar.is_file():
        raise FileNotFoundError(f"POSCAR not found: {poscar}")

    born = None
    epsilon = None
    if is_born:
        if outcar is None:
            raise ValueError("启用 --is-born 时必须提供 --outcar")
        if not outcar.is_file():
            raise FileNotFoundError(f"OUTCAR not found: {outcar}")
        outcar_obj = Outcar(outcar)
        born = outcar_obj.born
        epsilon = outcar_obj.dielectric_tensor

    structure = Structure.from_file(poscar)
    scell = (sx, sy, sz)

    nml = f90nml.Namelist()

    species = [str(sp) for sp in structure.composition.elements]
    nelements = len(species)
    natoms = len(structure)

    nml["allocations"] = {
        "nelements": nelements,
        "natoms": natoms,
        "ngrid": [15, 15, 15],
    }

    latt = structure.lattice.matrix
    positions = [list(site.frac_coords) for site in structure.sites]
    elem_to_type = {el: i + 1 for i, el in enumerate(species)}
    types = [elem_to_type[str(site.specie)] for site in structure.sites]

    nml["crystal"] = {
        "lfactor": 0.1,
        "lattvec": [list(row) for row in latt],
        "elements": species,
        "types": types,
        "positions": positions,
        "born": born,
        "epsilon": epsilon,
        "scell": list(scell),
    }

    nml["parameters"] = {
        "T_min": 300,
        "T_max": 900,
        "T_step": 100,
        "scalebroad": 0.5,
    }

    nml["flags"] = {
        "convergence": True,
    }

    with output.open("w") as f:
        nml.write(f)

    typer.echo(f"已写出 ShengBTE CONTROL 至 {output}")

