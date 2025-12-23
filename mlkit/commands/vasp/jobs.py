import math
import os
import shutil
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional, Union

import typer
from mlkit.core.shell import run_cmd
from pymatgen.core import Structure
from pymatgen.io.vasp.inputs import Incar, Kpoints
from pymatgen.symmetry.kpath import KPathSeek
from ruamel.yaml import YAML

yaml = YAML(typ="rt")

app = typer.Typer(help="VASP 作业准备与提交工具")


class Job:
    def __init__(self) -> None:
        self.config: Dict[str, Any] = self._load_config()
        self.work_dir: Path = self._resolve_work_dir()
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self._write_merged_config()

    def _load_config(self) -> Dict[str, Any]:
        config: Dict[str, Any] = {}
        base_config_path = Path(__file__).parent / "vasp_config.yaml"
        cwd_config_path = Path.cwd() / "vasp_config.yaml"

        if base_config_path.is_file():
            data = yaml.load(base_config_path.read_text(encoding="utf-8")) or {}
            if isinstance(data, dict):
                config.update(data)

        if cwd_config_path.is_file():
            data = yaml.load(cwd_config_path.read_text(encoding="utf-8")) or {}
            if isinstance(data, dict):
                config.update(data)

        env_config_path_env = os.environ.get("INK_VASP_CONFIG")
        if env_config_path_env:
            env_config_path = Path(env_config_path_env)
            if env_config_path.is_file():
                data = yaml.load(env_config_path.read_text(encoding="utf-8")) or {}
                if isinstance(data, dict):
                    config.update(data)

        return config

    def _resolve_work_dir(self) -> Path:
        global_cfg = self.config.get("global") or {}
        work_dir_cfg = global_cfg.get("work_dir")
        return Path(work_dir_cfg) if work_dir_cfg else Path.cwd()

    def _write_merged_config(self) -> None:
        cfg_path = self.work_dir / "vasp_config.yaml"
        with cfg_path.open("w", encoding="utf-8") as f:
            yaml.dump(self.config, f)

    def _calculate_grid_dimensions(self, bnorm: tuple[float, float, float], kpr: float):
        b1, b2, b3 = bnorm
        nkpx = max(1, math.floor(b1 / kpr / 2 / math.pi))
        nkpy = max(1, math.floor(b2 / kpr / 2 / math.pi))
        nkpz = max(1, math.floor(b3 / kpr / 2 / math.pi))
        return nkpx, nkpy, nkpz

    def _write_poscar(self, poscar: Union[Path, str], cwd: Path) -> None:
        target = cwd / "POSCAR"
        structure = Structure.from_file(poscar)
        structure.to_file(target)

    def _write_incar(self, incar: Union[Path, str, Dict[str, Any]], cwd: Path) -> None:
        target = cwd / "INCAR"
        if isinstance(incar, dict):
            incar_obj = Incar.from_dict(incar)
        else:
            incar_obj = Incar.from_file(incar)
        incar_obj.write_file(target)

    def _write_potcar(self, potcar: Union[Path, str], cwd: Path) -> None:
        target = cwd / "POTCAR"
        potcar_text = Path(potcar).read_text()
        target.write_text(potcar_text)

    def _write_kpoints(self, kpoints: Union[str, float, int, Path], cwd: Path, poscar: Path) -> None:
        target = cwd / "KPOINTS"

        if isinstance(kpoints, (float, int)):
            structure = Structure.from_file(poscar)
            bnorm = structure.lattice.reciprocal_lattice.abc
            grid = self._calculate_grid_dimensions(bnorm, float(kpoints))
            kp = Kpoints.gamma_automatic(grid)
            kp.write_file(target)
            return

        if isinstance(kpoints, str) and kpoints == "line":
            structure = Structure.from_file(poscar)
            kpath = KPathSeek(structure, symprec=1e-5)
            kpts, labels = kpath.get_kpoints(line_density=30, coords_are_cartesian=True)
            kp = Kpoints(comment="High-symmetry line path from Seek-path")
            kp.kpts = kpts
            kp.kpts_labels = labels
            kp.style = Kpoints.supported_modes.Line_mode
            kp.write_file(target)
            return

        kpoints_obj = Kpoints.from_file(kpoints)
        kpoints_obj.write_file(target)

    def _write_jobscript(self, jobscript: Union[Path, str], cwd: Path) -> None:
        target = cwd / "jobscript.sh"
        if isinstance(jobscript, Path):
            content = jobscript.read_text()
        else:
            content = jobscript
        target.write_text(content)

    def _resolve_cfg_value(self, arg: Optional[Union[Path, str, float, int, Dict[str, Any]]], section: str, key: str):
        if arg is not None:
            return arg
        section_cfg = self.config.get(section) or {}
        if key not in section_cfg:
            raise ValueError(f"缺少配置: [{section}] {key}")
        return section_cfg[key]

    def _handle_cp(self, section: str, cwd: Path) -> None:
        section_cfg = self.config.get(section) or {}
        cp_cfg = section_cfg.get("cp")
        if not cp_cfg or not isinstance(cp_cfg, dict):
            return

        for src, dst in cp_cfg.items():
            src_path = Path(src)
            if not src_path.is_absolute():
                src_path = self.work_dir / src_path

            dst_path = cwd / dst
            if not src_path.exists():
                typer.echo(f"Warning: Source '{src_path}' 不存在，跳过复制。", err=True)
                continue

            if src_path.is_dir():
                if dst_path.exists():
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
            else:
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dst_path)

    def _submit(self, cwd: Path) -> None:
        pid_file = cwd / "qsub.pid"
        if pid_file.is_file():
            old_pid = pid_file.read_text().strip()
            if old_pid:
                typer.echo(f"发现旧作业 {old_pid}，尝试取消...")
                run_cmd(["qdel", old_pid], cwd=str(cwd), check=False)

        result = run_cmd(["qsub", "jobscript.sh"], cwd=str(cwd))
        new_pid = (result.stdout or "").strip()
        if new_pid:
            pid_file.write_text(new_pid)
            typer.echo(f"已提交作业 {new_pid}，PID 保存到 {pid_file}")

    def _prepare_job(
        self,
        section: str,
        poscar: Optional[Path],
        incar: Optional[Union[Path, Dict[str, Any]]],
        potcar: Optional[Path],
        kpoints: Optional[Union[str, float, int, Path]],
        jobscript: Optional[Union[Path, str]],
    ) -> Path:
        cwd = self.work_dir / section
        cwd.mkdir(parents=True, exist_ok=True)
        self._handle_cp(section, cwd)

        poscar_path = self._resolve_cfg_value(poscar, section, "poscar")
        self._write_poscar(Path(poscar_path), cwd)

        incar_path = self._resolve_cfg_value(incar, section, "incar")
        self._write_incar(incar_path, cwd)

        potcar_path = self._resolve_cfg_value(potcar, section, "potcar")
        self._write_potcar(Path(potcar_path), cwd)

        kpoints_val = self._resolve_cfg_value(kpoints, section, "kpoints")
        self._write_kpoints(kpoints_val, cwd, cwd / "POSCAR")

        jobscript_val = self._resolve_cfg_value(jobscript, section, "jobscript")
        self._write_jobscript(jobscript_val, cwd)
        return cwd

    def _make_command(
        self,
        section: str,
        poscar: Optional[Path],
        incar: Optional[Union[Path, Dict[str, Any]]],
        potcar: Optional[Path],
        kpoints: Optional[Union[str, float, int, Path]],
        jobscript: Optional[Union[Path, str]],
        yes: bool,
    ) -> None:
        cwd = self._prepare_job(section, poscar, incar, potcar, kpoints, jobscript)
        if yes or typer.confirm("提交作业？"):
            self._submit(cwd)

    # command entrypoints
    def relax1(
        self,
        poscar: Optional[Path] = typer.Option(None, "--poscar", help="POSCAR 路径，缺省用配置"),
        incar: Optional[Union[Path, Dict[str, Any]]] = typer.Option(
            None, "--incar", help="INCAR 路径或字典，缺省用配置"
        ),
        potcar: Optional[Path] = typer.Option(None, "--potcar", help="POTCAR 路径，缺省用配置"),
        kpoints: Optional[Union[str, float, int, Path]] = typer.Option(
            None, "--kpoints", help="KPOINTS 路径/'line'/KPR 数值，缺省用配置"
        ),
        jobscript: Optional[Union[Path, str]] = typer.Option(
            None, "--jobscript", help="作业脚本路径或内容，缺省用配置"
        ),
        yes: bool = typer.Option(False, "--yes", "-y", help="无需确认直接提交"),
    ) -> None:
        """准备 relax1 并可提交 PBS 作业"""

        self._make_command("relax1", poscar, incar, potcar, kpoints, jobscript, yes)

    def relax2(
        self,
        poscar: Optional[Path] = typer.Option(None, "--poscar", help="POSCAR 路径，缺省用配置"),
        incar: Optional[Union[Path, Dict[str, Any]]] = typer.Option(
            None, "--incar", help="INCAR 路径或字典，缺省用配置"
        ),
        potcar: Optional[Path] = typer.Option(None, "--potcar", help="POTCAR 路径，缺省用配置"),
        kpoints: Optional[Union[str, float, int, Path]] = typer.Option(
            None, "--kpoints", help="KPOINTS 路径/'line'/KPR 数值，缺省用配置"
        ),
        jobscript: Optional[Union[Path, str]] = typer.Option(
            None, "--jobscript", help="作业脚本路径或内容，缺省用配置"
        ),
        yes: bool = typer.Option(False, "--yes", "-y", help="无需确认直接提交"),
    ) -> None:
        """准备 relax2 并可提交 PBS 作业"""

        self._make_command("relax2", poscar, incar, potcar, kpoints, jobscript, yes)

    def static(
        self,
        poscar: Optional[Path] = typer.Option(None, "--poscar", help="POSCAR 路径，缺省用配置"),
        incar: Optional[Union[Path, Dict[str, Any]]] = typer.Option(
            None, "--incar", help="INCAR 路径或字典，缺省用配置"
        ),
        potcar: Optional[Path] = typer.Option(None, "--potcar", help="POTCAR 路径，缺省用配置"),
        kpoints: Optional[Union[str, float, int, Path]] = typer.Option(
            None, "--kpoints", help="KPOINTS 路径/'line'/KPR 数值，缺省用配置"
        ),
        jobscript: Optional[Union[Path, str]] = typer.Option(
            None, "--jobscript", help="作业脚本路径或内容，缺省用配置"
        ),
        yes: bool = typer.Option(False, "--yes", "-y", help="无需确认直接提交"),
    ) -> None:
        """准备 static 并可提交 PBS 作业"""

        self._make_command("static", poscar, incar, potcar, kpoints, jobscript, yes)

    def dos(
        self,
        poscar: Optional[Path] = typer.Option(None, "--poscar", help="POSCAR 路径，缺省用配置"),
        incar: Optional[Union[Path, Dict[str, Any]]] = typer.Option(
            None, "--incar", help="INCAR 路径或字典，缺省用配置"
        ),
        potcar: Optional[Path] = typer.Option(None, "--potcar", help="POTCAR 路径，缺省用配置"),
        kpoints: Optional[Union[str, float, int, Path]] = typer.Option(
            None, "--kpoints", help="KPOINTS 路径/'line'/KPR 数值，缺省用配置"
        ),
        jobscript: Optional[Union[Path, str]] = typer.Option(
            None, "--jobscript", help="作业脚本路径或内容，缺省用配置"
        ),
        yes: bool = typer.Option(False, "--yes", "-y", help="无需确认直接提交"),
    ) -> None:
        """准备 DOS 并可提交 PBS 作业"""

        self._make_command("dos", poscar, incar, potcar, kpoints, jobscript, yes)

    def band(
        self,
        poscar: Optional[Path] = typer.Option(None, "--poscar", help="POSCAR 路径，缺省用配置"),
        incar: Optional[Union[Path, Dict[str, Any]]] = typer.Option(
            None, "--incar", help="INCAR 路径或字典，缺省用配置"
        ),
        potcar: Optional[Path] = typer.Option(None, "--potcar", help="POTCAR 路径，缺省用配置"),
        kpoints: Optional[Union[str, float, int, Path]] = typer.Option(
            None, "--kpoints", help="KPOINTS 路径/'line'/KPR 数值，缺省用配置"
        ),
        jobscript: Optional[Union[Path, str]] = typer.Option(
            None, "--jobscript", help="作业脚本路径或内容，缺省用配置"
        ),
        yes: bool = typer.Option(False, "--yes", "-y", help="无需确认直接提交"),
    ) -> None:
        """准备能带计算并可提交 PBS 作业"""

        self._make_command("band", poscar, incar, potcar, kpoints, jobscript, yes)

    def fc2(
        self,
        poscar: Optional[Path] = typer.Option(None, "--poscar", help="POSCAR 路径，缺省用配置"),
        incar: Optional[Union[Path, Dict[str, Any]]] = typer.Option(
            None, "--incar", help="INCAR 路径或字典，缺省用配置"
        ),
        potcar: Optional[Path] = typer.Option(None, "--potcar", help="POTCAR 路径，缺省用配置"),
        kpoints: Optional[Union[str, float, int, Path]] = typer.Option(
            None, "--kpoints", help="KPOINTS 路径/'line'/KPR 数值，缺省用配置"
        ),
        jobscript: Optional[Union[Path, str]] = typer.Option(
            None, "--jobscript", help="作业脚本路径或内容，缺省用配置"
        ),
        yes: bool = typer.Option(False, "--yes", "-y", help="无需确认直接提交"),
    ) -> None:
        """准备 fc2 并可提交 PBS 作业"""

        self._make_command("fc2", poscar, incar, potcar, kpoints, jobscript, yes)

    def batch(
        self,
        poscar: Optional[Path] = typer.Option(None, "--poscar", help="POSCAR 路径，缺省用配置"),
        incar: Optional[Union[Path, Dict[str, Any]]] = typer.Option(
            None, "--incar", help="INCAR 路径或字典，缺省用配置"
        ),
        potcar: Optional[Path] = typer.Option(None, "--potcar", help="POTCAR 路径，缺省用配置"),
        kpoints: Optional[Union[str, float, int, Path]] = typer.Option(
            None, "--kpoints", help="KPOINTS 路径/'line'/KPR 数值，缺省用配置"
        ),
        jobscript: Optional[Union[Path, str]] = typer.Option(
            None, "--jobscript", help="作业脚本路径或内容，缺省用配置"
        ),
        yes: bool = typer.Option(False, "--yes", "-y", help="无需确认直接提交"),
    ) -> None:
        """在工作目录批量准备作业"""

        self._make_command("batch", poscar, incar, potcar, kpoints, jobscript, yes)


def _create_lazy_command(method_name: str):
    method = getattr(Job, method_name)

    @wraps(method)
    def wrapper(*args, **kwargs):
        instance = Job()
        return getattr(instance, method_name)(*args, **kwargs)

    import inspect

    sig = inspect.signature(method)
    params = [p for p in sig.parameters.values() if p.name != "self"]
    wrapper.__signature__ = sig.replace(parameters=params)  # type: ignore[attr-defined]
    return wrapper


app.command(name="relax1")(_create_lazy_command("relax1"))
app.command(name="relax2")(_create_lazy_command("relax2"))
app.command(name="static")(_create_lazy_command("static"))
app.command(name="dos")(_create_lazy_command("dos"))
app.command(name="band")(_create_lazy_command("band"))
app.command(name="fc2")(_create_lazy_command("fc2"))
app.command(name="batch")(_create_lazy_command("batch"))

