# Sources and literature anchors

This file records the references used to design the model. It is not a complete bibliography.

## Low-energy electron irradiation

Schwartz, Aloni, Ogletree, and Schenkel, "Effects of low-energy electron irradiation on formation of nitrogen-vacancy centers in single-crystal diamond", New Journal of Physics 14, 043024 (2012). DOI: <https://doi.org/10.1088/1367-2630/14/4/043024>

Key point for this project: 2-30 keV electron beams locally induced NV formation without thermal annealing in nitrogen-implanted diamond, but the paper argues for electronic-excitation-driven reconstruction rather than simple thermal annealing or direct knock-on displacement.

OSTI page: <https://www.osti.gov/pages/biblio/1407152>

## DFT formation and migration of NV-related defects

Deak, Aradi, Kaviani, Frauenheim, and Gali, "Formation of NV centers in diamond: A theoretical study based on calculated transitions and migrations of nitrogen and vacancy related defects", Physical Review B 89, 075203 (2014). DOI: <https://doi.org/10.1103/PhysRevB.89.075203>

Key point for this project: calculated transitions and migration pathways of nitrogen/vacancy-related defects are the right theoretical framework for discussing whether irradiation plus annealing creates NV centers.

## Interstitial nitrogen in diamond

Goss, Briddon, Papagiannidis, and Jones, "Interstitial nitrogen and its complexes in diamond", Physical Review B 70, 235208 (2004). DOI: <https://doi.org/10.1103/PhysRevB.70.235208>

Accessible publication summary: <https://www.staff.ncl.ac.uk/j.p.goss/Publications/abs008.htm>

Key point for this project: nitrogen can be displaced into interstitial configurations by irradiation, and isolated/interstitial-complex models are relevant when testing the `N_i -> V_C` idea.

## NV center DFT background

Gali, "Ab initio theory of the nitrogen-vacancy center in diamond", Nanophotonics (2019). DOI: <https://doi.org/10.1515/nanoph-2019-0154>

Key point for this project: PBE is useful for exploratory structure work, but hybrid-functional calculations are needed for reliable defect levels and optical/electronic conclusions.

## Displacement threshold context

The direct electron-to-nucleus energy transfer estimate in `scripts/electron_transfer.py` uses the standard relativistic maximum-transfer expression:

`T_max = 2 E (E + 2 m_e c^2) / (M c^2)`

where `E` is electron kinetic energy and `M c^2` is nuclear rest energy. Use this only as a screening estimate. Direction-dependent displacement thresholds in diamond should be taken from experiment or high-level MD/DFT for final quantitative work.
