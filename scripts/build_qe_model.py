"""Generate diamond defect structures and Quantum ESPRESSO input templates.

Two pathways are generated:

1. ni_to_vc:
   N interstitial near a carbon vacancy moves into that vacancy.

2. vacancy_hop_to_nv:
   A carbon vacancy one hop away moves next to substitutional N, forming NV.

3. ns_to_divacancy:
   Substitutional N moves into one site of an adjacent divacancy pair.

The geometries are intentionally conservative starting guesses. Relax both
endpoints before using the NEB result for any scientific claim.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


BOHR_PER_ANGSTROM = 1.889726125


DIAMOND_BASIS_FRAC = [
    (0.0, 0.0, 0.0),
    (0.0, 0.5, 0.5),
    (0.5, 0.0, 0.5),
    (0.5, 0.5, 0.0),
    (0.25, 0.25, 0.25),
    (0.25, 0.75, 0.75),
    (0.75, 0.25, 0.75),
    (0.75, 0.75, 0.25),
]


@dataclass(frozen=True)
class Site:
    key: tuple[int, int, int, int]
    position: tuple[float, float, float]


@dataclass(frozen=True)
class Atom:
    symbol: str
    position: tuple[float, float, float]
    tag: str


def add(a: Iterable[float], b: Iterable[float]) -> tuple[float, float, float]:
    ax, ay, az = a
    bx, by, bz = b
    return (ax + bx, ay + by, az + bz)


def scale(a: Iterable[float], factor: float) -> tuple[float, float, float]:
    ax, ay, az = a
    return (ax * factor, ay * factor, az * factor)


def midpoint(a: Iterable[float], b: Iterable[float]) -> tuple[float, float, float]:
    ax, ay, az = a
    bx, by, bz = b
    return ((ax + bx) / 2.0, (ay + by) / 2.0, (az + bz) / 2.0)


def interpolate(
    a: Iterable[float], b: Iterable[float], fraction: float
) -> tuple[float, float, float]:
    ax, ay, az = a
    bx, by, bz = b
    return (
        ax + (bx - ax) * fraction,
        ay + (by - ay) * fraction,
        az + (bz - az) * fraction,
    )


def distance(a: Iterable[float], b: Iterable[float]) -> float:
    ax, ay, az = a
    bx, by, bz = b
    return ((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2) ** 0.5


def normalize(a: Iterable[float]) -> tuple[float, float, float]:
    ax, ay, az = a
    norm = (ax**2 + ay**2 + az**2) ** 0.5
    if norm == 0:
        raise ValueError("Cannot normalize a zero-length vector.")
    return (ax / norm, ay / norm, az / norm)


def format_vec(position: Iterable[float]) -> str:
    x, y, z = position
    return f"{x:16.10f} {y:16.10f} {z:16.10f}"


def build_sites(supercell: int, lattice_a: float) -> dict[tuple[int, int, int, int], Site]:
    sites: dict[tuple[int, int, int, int], Site] = {}
    for i in range(supercell):
        for j in range(supercell):
            for k in range(supercell):
                cell_origin = (i * lattice_a, j * lattice_a, k * lattice_a)
                for basis_index, frac in enumerate(DIAMOND_BASIS_FRAC):
                    key = (i, j, k, basis_index)
                    position = add(cell_origin, scale(frac, lattice_a))
                    sites[key] = Site(key=key, position=position)
    return sites


def scenario_ni_to_vc(
    sites: dict[tuple[int, int, int, int], Site], supercell: int
) -> tuple[list[Atom], list[Atom], dict[str, object]]:
    c = supercell // 2
    vacancy_key = (c, c, c, 0)
    bond_a_key = (c, c, c, 4)
    bond_b_key = (c, c, c, 1)

    vacancy_position = sites[vacancy_key].position
    interstitial_position = midpoint(sites[bond_a_key].position, sites[bond_b_key].position)
    target_cn_distance = 1.35

    adjusted_initial_positions: dict[tuple[int, int, int, int], tuple[float, float, float]] = {}
    for bond_key in [bond_a_key, bond_b_key]:
        direction = normalize(
            (
                sites[bond_key].position[0] - interstitial_position[0],
                sites[bond_key].position[1] - interstitial_position[1],
                sites[bond_key].position[2] - interstitial_position[2],
            )
        )
        adjusted_initial_positions[bond_key] = add(
            interstitial_position, scale(direction, target_cn_distance)
        )

    initial: list[Atom] = []
    final: list[Atom] = []
    for key in sorted(sites):
        if key == vacancy_key:
            continue
        site = sites[key]
        initial.append(Atom("C", adjusted_initial_positions.get(key, site.position), f"C_{key}"))
        final.append(Atom("C", site.position, f"C_{key}"))

    initial.append(Atom("N", interstitial_position, "N_interstitial"))
    final.append(Atom("N", vacancy_position, "N_substitutional_after_recombination"))

    metadata = {
        "scenario": "ni_to_vc",
        "meaning": "N interstitial near a carbon vacancy recombines into the vacancy.",
        "vacancy_key": vacancy_key,
        "bond_center_keys_initially_relaxed_outward": [bond_a_key, bond_b_key],
        "initial_target_C_N_distance_angstrom": target_cn_distance,
        "initial_actual_C_N_distance_angstrom": [
            distance(adjusted_initial_positions[bond_a_key], interstitial_position),
            distance(adjusted_initial_positions[bond_b_key], interstitial_position),
        ],
        "initial_N_position_angstrom": interstitial_position,
        "final_N_position_angstrom": vacancy_position,
        "warning": (
            "With only one vacancy, the final state is substitutional nitrogen, "
            "not an NV center. A second adjacent vacancy is needed for NV."
        ),
    }
    return initial, final, metadata


def scenario_vacancy_hop_to_nv(
    sites: dict[tuple[int, int, int, int], Site], supercell: int
) -> tuple[list[Atom], list[Atom], dict[str, object]]:
    c = supercell // 2
    nitrogen_key = (c, c, c, 0)
    final_vacancy_key = (c, c, c, 4)
    initial_vacancy_key = (c, c, c, 1)

    initial: list[Atom] = []
    final: list[Atom] = []
    migrating_tag = f"C_migrates_{final_vacancy_key}_to_{initial_vacancy_key}"

    for key in sorted(sites):
        site = sites[key]
        if key == nitrogen_key:
            initial.append(Atom("N", site.position, "N_substitutional"))
            final.append(Atom("N", site.position, "N_substitutional"))
        elif key == initial_vacancy_key:
            continue
        elif key == final_vacancy_key:
            initial.append(Atom("C", site.position, migrating_tag))
            final.append(Atom("C", sites[initial_vacancy_key].position, migrating_tag))
        else:
            initial.append(Atom("C", site.position, f"C_{key}"))
            final.append(Atom("C", site.position, f"C_{key}"))

    metadata = {
        "scenario": "vacancy_hop_to_nv",
        "meaning": (
            "A neighboring carbon jumps into a vacancy, so the vacancy moves next "
            "to substitutional nitrogen and creates an NV geometry."
        ),
        "nitrogen_key": nitrogen_key,
        "initial_vacancy_key": initial_vacancy_key,
        "final_vacancy_key_next_to_N": final_vacancy_key,
        "migrating_carbon_initial_position_angstrom": sites[final_vacancy_key].position,
        "migrating_carbon_final_position_angstrom": sites[initial_vacancy_key].position,
    }
    return initial, final, metadata


def scenario_ns_to_divacancy(
    sites: dict[tuple[int, int, int, int], Site], supercell: int
) -> tuple[list[Atom], list[Atom], dict[str, object]]:
    c = supercell // 2
    nitrogen_key = (c, c, c, 0)
    first_vacancy_key = (c, c, c, 4)
    second_vacancy_key = (c, c, c, 1)

    nitrogen_initial = sites[nitrogen_key].position
    nitrogen_final = sites[first_vacancy_key].position
    static_vacancy = sites[second_vacancy_key].position

    initial: list[Atom] = []
    final: list[Atom] = []
    for key in sorted(sites):
        site = sites[key]
        if key == nitrogen_key:
            initial.append(Atom("N", nitrogen_initial, "N_substitutional_moves_to_vacancy"))
            final.append(Atom("N", nitrogen_final, "N_substitutional_moves_to_vacancy"))
        elif key in (first_vacancy_key, second_vacancy_key):
            continue
        else:
            initial.append(Atom("C", site.position, f"C_{key}"))
            final.append(Atom("C", site.position, f"C_{key}"))

    metadata = {
        "scenario": "ns_to_divacancy",
        "meaning": (
            "A substitutional nitrogen sits next to two adjacent vacancies. "
            "The nitrogen moves into the nearer vacancy, leaving its original "
            "substitutional site vacant."
        ),
        "nitrogen_key": nitrogen_key,
        "first_vacancy_key": first_vacancy_key,
        "second_vacancy_key": second_vacancy_key,
        "moving_n_initial_position_angstrom": nitrogen_initial,
        "moving_n_final_position_angstrom": nitrogen_final,
        "vacancy_positions_initial_angstrom": [nitrogen_final, static_vacancy],
        "vacancy_positions_final_angstrom": [nitrogen_initial, static_vacancy],
        "warning": (
            "This is a structural pathway hypothesis for visualization and NEB setup. "
            "It does not mean the nitrogen is directly pushed by the electron beam."
        ),
    }
    return initial, final, metadata


def write_xyz(path: Path, atoms: list[Atom], comment: str) -> None:
    lines = [str(len(atoms)), comment]
    for atom in atoms:
        lines.append(f"{atom.symbol} {format_vec(atom.position)}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def qe_common_header(
    *,
    calculation: str,
    prefix: str,
    nat: int,
    cell_length: float,
    charge: int,
    pseudo_dir: str,
    ecutwfc: float,
    ecutrho: float,
) -> str:
    return f"""&CONTROL
  calculation = '{calculation}'
  prefix = '{prefix}'
  outdir = './tmp'
  pseudo_dir = '{pseudo_dir}'
  verbosity = 'high'
  forc_conv_thr = 1.0d-4
/
&SYSTEM
  ibrav = 0
  nat = {nat}
  ntyp = 2
  ecutwfc = {ecutwfc:.1f}
  ecutrho = {ecutrho:.1f}
  occupations = 'fixed'
  nspin = 2
  starting_magnetization(1) = 0.0
  starting_magnetization(2) = 0.5
  tot_charge = {charge}
/
&ELECTRONS
  conv_thr = 1.0d-8
  mixing_beta = 0.3
  electron_maxstep = 200
/
&IONS
  ion_dynamics = 'bfgs'
/
ATOMIC_SPECIES
  C  12.0107  C.pbe-n-kjpaw_psl.1.0.0.UPF
  N  14.0067  N.pbe-n-kjpaw_psl.1.0.0.UPF
K_POINTS gamma
CELL_PARAMETERS angstrom
{cell_length:16.10f} {0.0:16.10f} {0.0:16.10f}
{0.0:16.10f} {cell_length:16.10f} {0.0:16.10f}
{0.0:16.10f} {0.0:16.10f} {cell_length:16.10f}
"""


def atomic_positions_block(atoms: list[Atom]) -> str:
    lines = ["ATOMIC_POSITIONS angstrom"]
    for atom in atoms:
        lines.append(f"  {atom.symbol} {format_vec(atom.position)}")
    return "\n".join(lines) + "\n"


def write_relax_input(
    path: Path,
    *,
    atoms: list[Atom],
    prefix: str,
    cell_length: float,
    charge: int,
    pseudo_dir: str,
    ecutwfc: float,
    ecutrho: float,
) -> None:
    text = qe_common_header(
        calculation="relax",
        prefix=prefix,
        nat=len(atoms),
        cell_length=cell_length,
        charge=charge,
        pseudo_dir=pseudo_dir,
        ecutwfc=ecutwfc,
        ecutrho=ecutrho,
    )
    text += atomic_positions_block(atoms)
    path.write_text(text, encoding="utf-8")


def write_neb_input(
    path: Path,
    *,
    initial: list[Atom],
    final: list[Atom],
    prefix: str,
    cell_length: float,
    charge: int,
    pseudo_dir: str,
    ecutwfc: float,
    ecutrho: float,
    images: int,
) -> None:
    if len(initial) != len(final):
        raise ValueError("Initial and final atom counts must match for NEB.")
    if [atom.symbol for atom in initial] != [atom.symbol for atom in final]:
        raise ValueError("Initial and final atom order/species must match for NEB.")

    header = qe_common_header(
        calculation="scf",
        prefix=prefix,
        nat=len(initial),
        cell_length=cell_length,
        charge=charge,
        pseudo_dir=pseudo_dir,
        ecutwfc=ecutwfc,
        ecutrho=ecutrho,
    )
    # NEB input does not use &IONS from pw.x in the same way.
    header = header.replace("&IONS\n  ion_dynamics = 'bfgs'\n/\n", "")

    lines = [
        "BEGIN",
        "BEGIN_PATH_INPUT",
        "&PATH",
        "  string_method = 'neb'",
        f"  num_of_images = {images}",
        "  nstep_path = 200",
        "  opt_scheme = 'broyden'",
        "  ds = 1.0d0",
        "  k_max = 0.30d0",
        "  k_min = 0.20d0",
        "  CI_scheme = 'auto'",
        "  path_thr = 0.05d0",
        "/",
        "END_PATH_INPUT",
        "BEGIN_ENGINE_INPUT",
        header.rstrip(),
        "BEGIN_POSITIONS",
        "FIRST_IMAGE",
        atomic_positions_block(initial).rstrip(),
        "LAST_IMAGE",
        atomic_positions_block(final).rstrip(),
        "END_POSITIONS",
        "END_ENGINE_INPUT",
        "END",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def write_metadata(path: Path, metadata: dict[str, object]) -> None:
    path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_scenario(
    root: Path,
    name: str,
    initial: list[Atom],
    final: list[Atom],
    metadata: dict[str, object],
    *,
    cell_length: float,
    charge: int,
    pseudo_dir: str,
    ecutwfc: float,
    ecutrho: float,
    images: int,
) -> None:
    scenario_dir = root / name
    scenario_dir.mkdir(parents=True, exist_ok=True)

    write_xyz(scenario_dir / "initial.xyz", initial, f"{name} initial")
    write_xyz(scenario_dir / "final.xyz", final, f"{name} final")
    write_metadata(scenario_dir / "metadata.json", metadata)

    write_relax_input(
        scenario_dir / "relax_initial.in",
        atoms=initial,
        prefix=f"{name}_initial_q{charge}",
        cell_length=cell_length,
        charge=charge,
        pseudo_dir=pseudo_dir,
        ecutwfc=ecutwfc,
        ecutrho=ecutrho,
    )
    write_relax_input(
        scenario_dir / "relax_final.in",
        atoms=final,
        prefix=f"{name}_final_q{charge}",
        cell_length=cell_length,
        charge=charge,
        pseudo_dir=pseudo_dir,
        ecutwfc=ecutwfc,
        ecutrho=ecutrho,
    )
    write_neb_input(
        scenario_dir / "neb.in",
        initial=initial,
        final=final,
        prefix=f"{name}_neb_q{charge}",
        cell_length=cell_length,
        charge=charge,
        pseudo_dir=pseudo_dir,
        ecutwfc=ecutwfc,
        ecutrho=ecutrho,
        images=images,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("qe"))
    parser.add_argument("--supercell", type=int, default=3)
    parser.add_argument("--a", type=float, default=3.567, help="Diamond lattice constant in Angstrom.")
    parser.add_argument("--charge", type=int, default=0)
    parser.add_argument("--images", type=int, default=7)
    parser.add_argument("--pseudo-dir", default="../pseudo")
    parser.add_argument("--ecutwfc", type=float, default=60.0)
    parser.add_argument("--ecutrho", type=float, default=480.0)
    args = parser.parse_args()

    if args.supercell < 3:
        raise SystemExit("Use --supercell 3 or larger so the defect is not too cramped.")
    if args.images < 3:
        raise SystemExit("Use at least 3 NEB images.")

    cell_length = args.supercell * args.a
    sites = build_sites(args.supercell, args.a)
    args.out.mkdir(parents=True, exist_ok=True)

    scenarios = {
        "ni_to_vc": scenario_ni_to_vc(sites, args.supercell),
        "vacancy_hop_to_nv": scenario_vacancy_hop_to_nv(sites, args.supercell),
        "ns_to_divacancy": scenario_ns_to_divacancy(sites, args.supercell),
    }

    for name, (initial, final, metadata) in scenarios.items():
        metadata = {
            **metadata,
            "supercell": f"{args.supercell}x{args.supercell}x{args.supercell}",
            "cell_length_angstrom": cell_length,
            "charge": args.charge,
            "nat": len(initial),
            "quantum_espresso_note": (
                "Relax endpoints first; then update NEB FIRST_IMAGE/LAST_IMAGE "
                "with relaxed coordinates before final production runs."
            ),
        }
        write_scenario(
            args.out,
            name,
            initial,
            final,
            metadata,
            cell_length=cell_length,
            charge=args.charge,
            pseudo_dir=args.pseudo_dir,
            ecutwfc=args.ecutwfc,
            ecutrho=args.ecutrho,
            images=args.images,
        )

    summary = {
        "created_scenarios": sorted(scenarios),
        "supercell": args.supercell,
        "lattice_constant_angstrom": args.a,
        "cell_length_angstrom": cell_length,
        "charge": args.charge,
        "files": [
            "initial.xyz",
            "final.xyz",
            "relax_initial.in",
            "relax_final.in",
            "neb.in",
            "metadata.json",
        ],
    }
    write_metadata(args.out / "build_summary.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
