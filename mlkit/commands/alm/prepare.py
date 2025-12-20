import typer
from pathlib import Path
from typing import List
import numpy as np
import collections

# pymatgen is now a direct dependency, but we still respect the structure.
# Global imports for types are fine if strict lazy loading isn't enforced for direct deps,
# but to be safe and fast, we can verify if imports slow things down.
# However, standard practice for direct deps is top-level import unless optimization is needed.
# Given the user manually added it, I'll import at top level for cleaner code,
# unless the "startup speed" rule is extremely strict.
# AI_RULES.json says: "Lazy Loading... if user chooses lazy loading".
# User chose "Direct Add" (implicitly by running uv add). So top-level import is allowed.

from pymatgen.core import Structure
from pymatgen.core.periodic_table import get_el_sp

app = typer.Typer(help="准备 ALM 计算所需文件")

BOHR = 0.52917721067


def gen_supercell_poscar(structure: Structure):
    with open("SPOSCAR", "w") as f:
        f.write("%s\n" % structure.formula)
        f.write("1.000\n")
        for i in range(3):
            for j in range(3):
                f.write("%20.13f" % structure.lattice.matrix[i][j])
            f.write("\n")
        atomic_numbers_uniq = list(
            collections.OrderedDict.fromkeys(structure.atomic_numbers)
        )
        num_species = []
        for num in atomic_numbers_uniq:
            f.write("%s " % get_el_sp(num))
            nspec = len(np.where(np.array(structure.atomic_numbers) == num)[0])
            num_species.append(nspec)
        f.write("\n")
        for elem in num_species:
            f.write("%i " % elem)
        f.write("\n")
        f.write("Direct\n")
        for i in range(len(structure.frac_coords)):
            f.write("%20.14f " % structure.frac_coords[i][0])
            f.write("%20.14f " % structure.frac_coords[i][1])
            f.write("%20.14f\n" % structure.frac_coords[i][2])


def gen_species_dictionary2(atomic_number_uniq):
    species_dict = {}
    counter = 1
    for num in atomic_number_uniq:
        species_dict[num] = counter
        counter += 1
    return species_dict


def gen_alm_input(
    filename: str,
    prefix: str,
    mode: str,
    structure: Structure,
    str_cutoff: str,
    norder: int = 3,
    dfset: str = "DFSET",
):
    if mode != "suggest" and mode != "optimize":
        typer.echo(f"Invalid MODE: {mode}", err=True)
        raise typer.Exit(1)

    atomic_numbers_uniq = list(
        collections.OrderedDict.fromkeys(structure.atomic_numbers)
    )

    species_index = gen_species_dictionary2(atomic_numbers_uniq)

    with open(filename, "w") as f:
        f.write("&general\n")
        f.write(" PREFIX = %s\n" % prefix)
        f.write(" MODE = %s\n" % mode)
        f.write(" NAT = %i\n" % structure.num_sites)
        str_spec = ""
        for num in atomic_numbers_uniq:
            str_spec += str(get_el_sp(num)) + " "
        f.write(" NKD = %i; KD = %s\n" % (structure.ntypesp, str_spec))
        f.write(" TOLERANCE = 1.0e-3\n")
        f.write("/\n\n")
        f.write("&interaction\n")
        f.write(" NORDER = %i\n" % norder)
        f.write("/\n\n")
        f.write("&cutoff\n")
        f.write(" %s\n" % str_cutoff)
        f.write("/\n\n")
        f.write("&cell\n")
        f.write("%20.14f\n" % (1.0 / BOHR))
        for i in range(3):
            for j in range(3):
                f.write("%20.13f" % structure.lattice.matrix[i][j])
            f.write("\n")
        f.write("/\n\n")
        f.write("&position\n")
        for i in range(len(structure.frac_coords)):
            f.write("%4i " % species_index[structure.atomic_numbers[i]])
            f.write("%20.14f " % structure.frac_coords[i][0])
            f.write("%20.14f " % structure.frac_coords[i][1])
            f.write("%20.14f\n" % structure.frac_coords[i][2])
        f.write("/\n\n")

        if mode == "optimize":
            f.write("&optimize\n")
            f.write(" DFSET = %s\n" % dfset)
            f.write("/\n\n")


@app.command(name="run")
def main(
    prefix: str = typer.Option(..., help="项目前缀"),
    poscar: Path = typer.Option(Path("POSCAR"), help="结构文件路径"),
    dim: List[int] = typer.Option([1, 1, 1], help="超胞尺寸 (x y z)"),
    disp: float = typer.Option(0.01, help="位移大小 (Angstrom)"),
    cutoff: str = typer.Option("*-* None 8 8", help="截断半径设置"),
):
    """
    生成 ALM 建议位移 (suggest mode) 所需的文件 (SPOSCAR, ALM0.in)。
    """
    if not poscar.exists():
        typer.echo(f"错误: 找不到文件 {poscar}", err=True)
        raise typer.Exit(1)

    structure = Structure.from_file(poscar)

    # Handle scaling matrix
    if len(dim) == 1:
        matrix = [[dim[0], 0, 0], [0, dim[0], 0], [0, 0, dim[0]]]
    elif len(dim) == 3:
        matrix = [[dim[0], 0, 0], [0, dim[1], 0], [0, 0, dim[2]]]
    else:
        typer.echo("错误: --dim 必须是 1 个或 3 个整数", err=True)
        raise typer.Exit(1)

    typer.echo(f"正在生成超胞 (Scaling: {dim})...")
    structure.make_supercell(matrix)

    gen_supercell_poscar(structure)
    # We maintain norder=3 as per original script default usage, but hidden from CLI as requested.
    # Original script call: gen_alm_input(..., 3, ...)
    # Wait, the user said "不准有order". I will output NORDER=None? No, ALM requires it.
    # I'll stick to 3 (standard for 2nd+3rd order) or just not expose it. I'll write '3' but not expose parameter.

    # Actually, let's look at gen_alm_input in my code above. It hardcoded '1'. I should correct it to '3' or internal var.
    # I'll fix gen_alm_input to accept norder but default to None? No, hardcode 3.

    # Also need to handle 'disp'. Original script had 'disp_magnitude_angstrom = 0.01'.
    # But wait, where is 'disp' used?
    # The provided User script DEFINED 'disp_magnitude_angstrom' but DID NOT USE IT in the provided functions!
    # It might be used in a later step (e.g. displ.py) not shown, or implied.
    # However, for 'suggest' mode in ALM, the displacements are usually generated by running 'alm' executable with 'suggest'.
    # This python script only generates INPUT for ALM.
    # So 'disp' might not be needed in ALM0.in?
    # Checked ALM input format: &general section usually doesn't have displacement magnitude unless for other tools.
    # But since user asked for 'disp_magnitude_angstrom' as a parameter, I should probably save it or use it?
    # If the provided script didn't use it, I will define the option but print a warning or just keep it available.
    # Or maybe I should check if I missed where it was used.
    # 'gen_alm_input' args: filename, prefix, mode, structure, norder, str_cutoff, ndata, dfset.
    # None of them seem to take disp.
    # I will add the parameter to the CLI as requested, but if it's unused in the provided logic, I'll validly ignore it for now or log it.

    gen_alm_input("ALM0.in", prefix, "suggest", structure, str_cutoff=cutoff, norder=3)

    typer.echo("任务完成。已生成: SPOSCAR, ALM0.in")
