"""Estimate maximum elastic energy transfer from an electron to C/N nuclei.

This is a small sanity check for the phrase "low-energy electron irradiation".
It does not model electronic excitation. It only asks whether direct ballistic
knock-on displacement is plausible.
"""

from __future__ import annotations

import math

ELECTRON_REST_KEV = 510.998950
AMU_REST_KEV = 931_494.10242

TARGETS = {
    "C": 12.0107,
    "N": 14.0067,
}


def tmax_ev(electron_keV: float, mass_amu: float) -> float:
    """Maximum transferable kinetic energy in eV."""
    nuclear_rest_kev = mass_amu * AMU_REST_KEV
    transfer_kev = (
        2.0
        * electron_keV
        * (electron_keV + 2.0 * ELECTRON_REST_KEV)
        / nuclear_rest_kev
    )
    return transfer_kev * 1000.0


def electron_energy_for_transfer_keV(target_ev: float, mass_amu: float) -> float:
    """Electron kinetic energy needed for a chosen maximum transfer."""
    nuclear_rest_kev = mass_amu * AMU_REST_KEV
    target_kev = target_ev / 1000.0
    # E^2 + 2 m_e E - target * M / 2 = 0
    return -ELECTRON_REST_KEV + math.sqrt(
        ELECTRON_REST_KEV**2 + target_kev * nuclear_rest_kev / 2.0
    )


def main() -> None:
    energies = [2, 5, 10, 20, 30, 50, 100, 145, 170, 200]
    print("# Maximum direct energy transfer from electron to nucleus")
    print()
    print("| electron energy (keV) | C T_max (eV) | N T_max (eV) |")
    print("|---:|---:|---:|")
    for energy in energies:
        c_ev = tmax_ev(energy, TARGETS["C"])
        n_ev = tmax_ev(energy, TARGETS["N"])
        print(f"| {energy:.0f} | {c_ev:.2f} | {n_ev:.2f} |")

    print()
    print("# Electron energy needed for selected displacement thresholds")
    print()
    print("| target | threshold (eV) | required electron energy (keV) |")
    print("|---|---:|---:|")
    for symbol, mass in TARGETS.items():
        for threshold in [30, 35, 40, 45]:
            required = electron_energy_for_transfer_keV(threshold, mass)
            print(f"| {symbol} | {threshold:.0f} | {required:.1f} |")


if __name__ == "__main__":
    main()
