"""Parse a simple Quantum ESPRESSO NEB energy table and report a barrier.

QE versions and workflows write slightly different NEB files. This parser is
intentionally permissive: it extracts numeric rows and uses the last numeric
column as the energy. If your file contains several tables, pass a cleaned
two-column file instead.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

FLOAT_RE = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[EeDd][-+]?\d+)?")


def parse_rows(path: Path) -> list[list[float]]:
    rows: list[list[float]] = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip() or line.lstrip().startswith(("#", "!", "@")):
            continue
        values = [
            float(match.group(0).replace("D", "E").replace("d", "e"))
            for match in FLOAT_RE.finditer(line)
        ]
        if len(values) >= 2:
            rows.append(values)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("neb_file", type=Path)
    parser.add_argument(
        "--energy-column",
        type=int,
        default=-1,
        help="Zero-based energy column. Default: last numeric column.",
    )
    args = parser.parse_args()

    rows = parse_rows(args.neb_file)
    if not rows:
        raise SystemExit(f"No numeric rows found in {args.neb_file}")

    energies = [row[args.energy_column] for row in rows]
    reference = energies[0]
    relative = [energy - reference for energy in energies]
    barrier = max(relative)

    print(f"images: {len(energies)}")
    print(f"initial energy: {energies[0]:.8f}")
    print(f"final energy:   {energies[-1]:.8f}")
    print(f"delta E:        {energies[-1] - energies[0]:.8f}")
    print(f"barrier:        {barrier:.8f}")
    print()
    print("| image | energy | relative |")
    print("|---:|---:|---:|")
    for index, (energy, rel) in enumerate(zip(energies, relative), start=1):
        print(f"| {index} | {energy:.8f} | {rel:.8f} |")


if __name__ == "__main__":
    main()
