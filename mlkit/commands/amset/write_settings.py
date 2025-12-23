import shutil
from pathlib import Path
from typing import Dict

import numpy as np
import typer
import yaml
from pymatgen.io.vasp.outputs import Outcar, Vasprun

app = typer.Typer(help="生成 AMSET settings.yaml")


AMSET_SETTINGS: Dict[str, object] = {
    "doping": [
        -1.0e18,
        -1.5e18,
        -2.0e18,
        -2.5e18,
        -3.0e18,
        -3.5e18,
        -4.0e18,
        -4.5e18,
        -5.0e18,
        -5.5e18,
        -6.0e18,
        -6.5e18,
        -7.0e18,
        -7.5e18,
        -8.0e18,
        -8.5e18,
        -9.0e18,
        -1.0e19,
        -1.05e19,
        -1.1e19,
        -1.15e19,
        -1.2e19,
        -1.25e19,
        -1.3e19,
        -1.35e19,
        -1.4e19,
        -1.45e19,
        -1.5e19,
        -1.75e19,
        -2.0e19,
        -2.5e19,
        -3.0e19,
        -3.5e19,
        -4.0e19,
        -4.5e19,
        -5.0e19,
        -5.5e19,
        -6.0e19,
        -6.5e19,
        -7.0e19,
        -7.5e19,
        -8.0e19,
        -8.5e19,
        -9.0e19,
        -1.0e20,
        -1.5e20,
        -2.0e20,
        -2.5e20,
        -3.0e20,
        -3.5e20,
        -4.0e20,
        -4.5e20,
        -5.0e20,
        -5.5e20,
        -6.0e20,
        -6.5e20,
        -7.0e20,
        -7.5e20,
        -8.0e20,
        -8.5e20,
        -9.0e20,
        -1.0e21,
        -1.5e21,
        -2.0e21,
        -2.5e21,
        -3.0e21,
        -3.5e21,
        -4.0e21,
        -4.5e21,
        -5.0e21,
        -5.5e21,
        -6.0e21,
        -6.5e21,
        -7.0e21,
        -7.5e21,
        -8.0e21,
        -8.5e21,
        -9.0e21,
        -1.0e22,
        1.0e18,
        1.5e18,
        2.0e18,
        2.5e18,
        3.0e18,
        3.5e18,
        4.0e18,
        4.5e18,
        5.0e18,
        5.5e18,
        6.0e18,
        6.5e18,
        7.0e18,
        7.5e18,
        8.0e18,
        8.5e18,
        9.0e18,
        1.0e19,
        1.05e19,
        1.1e19,
        1.15e19,
        1.2e19,
        1.25e19,
        1.3e19,
        1.35e19,
        1.4e19,
        1.45e19,
        1.5e19,
        1.75e19,
        2.0e19,
        2.5e19,
        3.0e19,
        3.5e19,
        4.0e19,
        4.5e19,
        5.0e19,
        5.5e19,
        6.0e19,
        6.5e19,
        7.0e19,
        7.5e19,
        8.0e19,
        8.5e19,
        9.0e19,
        1.0e20,
        1.5e20,
        2.0e20,
        2.5e20,
        3.0e20,
        3.5e20,
        4.0e20,
        4.5e20,
        5.0e20,
        5.5e20,
        6.0e20,
        6.5e20,
        7.0e20,
        7.5e20,
        8.0e20,
        8.5e20,
        9.0e20,
        1.0e21,
        1.5e21,
        2.0e21,
        2.5e21,
        3.0e21,
        3.5e21,
        4.0e21,
        4.5e21,
        5.0e21,
        5.5e21,
        6.0e21,
        6.5e21,
        7.0e21,
        7.5e21,
        8.0e21,
        8.5e21,
        9.0e21,
        1.0e22,
    ],
    "temperatures": 300,
    "scattering_type": "auto",
    "use_projections": False,
    "interpolation_factor": 30,
    "wavefunction_coefficients": "wavefunction.hdf5",
    "deformation_potential": "deform.hdf5",
    "symprec": 1e-5,
    "nworkers": -1,
    "cache_wavefunction": True,
    "file_format": "json",
    "write_input": True,
    "write_mesh": True,
}


def _copy_if_exists(src: Path) -> None:
    if src.exists():
        target_path = Path(".") / src.name
        shutil.copy2(src, target_path)
        print(f"Copied {src} to {target_path.absolute()}")


def _write_settings(
    scf_vasprun: Path,
    wavefunction_hdf5: Path,
    deform_hdf5: Path,
    dfpt_vasprun: Path,
    elastic_outcar: Path,
    pop_frequency: float,
) -> None:
    _copy_if_exists(scf_vasprun)

    high_frequency_dielectric = np.array(Vasprun(dfpt_vasprun).epsilon_static)
    static_dielectric = np.array(Vasprun(dfpt_vasprun).epsilon_ionic) + np.array(
        Vasprun(dfpt_vasprun).epsilon_static
    )
    elastic_outcar_obj = Outcar(elastic_outcar)
    elastic_outcar_obj.read_elastic_tensor()
    elastic_constant = elastic_outcar_obj.data["elastic_tensor"]

    AMSET_SETTINGS["wavefunction_coefficients"] = wavefunction_hdf5.absolute().as_posix()
    AMSET_SETTINGS["deformation_potential"] = deform_hdf5.absolute().as_posix()
    AMSET_SETTINGS["high_frequency_dielectric"] = high_frequency_dielectric.tolist()
    AMSET_SETTINGS["static_dielectric"] = static_dielectric.tolist()
    AMSET_SETTINGS["elastic_constant"] = elastic_constant
    AMSET_SETTINGS["pop_frequency"] = pop_frequency

    with open("settings.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(AMSET_SETTINGS, f, sort_keys=False)


@app.command(name="main")
def main(
    scf_vasprun: Path = typer.Argument(..., help="自洽 vasprun.xml 路径"),
    wavefunction_hdf5: Path = typer.Argument(..., help="AMSET wavefunction.hdf5 路径"),
    deform_hdf5: Path = typer.Argument(..., help="AMSET deform.hdf5 路径"),
    dfpt_vasprun: Path = typer.Argument(..., help="DFPT vasprun.xml 路径（含介电常数）"),
    elastic_outcar: Path = typer.Argument(..., help="DFPT OUTCAR 路径（含弹性张量）"),
    pop_frequency: float = typer.Argument(..., help="极化光学声子频率"),
) -> None:
    """
    根据 VASP/AMSET 输出生成 settings.yaml，doping/temperatures 等保持原脚本默认。
    """
    _write_settings(
        scf_vasprun,
        wavefunction_hdf5,
        deform_hdf5,
        dfpt_vasprun,
        elastic_outcar,
        pop_frequency,
    )
    typer.echo("已生成 settings.yaml")

