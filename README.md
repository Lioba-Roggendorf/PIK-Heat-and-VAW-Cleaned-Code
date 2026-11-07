# Does Extreme Heat Increase Violence Against Women? (main analysis, publishable version)

Lioba Roggendorf, 2026

This folder contains the complete main analysis (phase 2) as one reproducible pipeline:
from the raw LivWell data to every number and plot in the results.

## Folder structure

```
main_analysis_publishable_version/
├── Makefile                 runs the whole pipeline
├── code/                    one script per step, in the order they run
├── inputs/
│   ├── raw/                 data that comes from outside the project
│   └── processed/           cleaned datasets, created by the pipeline
└── outputs/
    ├── plots/               all figures
    ├── logs/                the full printout of every step
    └── main_results_summary.txt   the main numbers from all steps in one file
```

## How to run it

In a terminal, inside this folder:

```
make
```

That runs every step in order. `make` only re-runs a step when its script or its input
changed, so running it again right away does nothing. Other options:

```
make -B                          # force every step to run again
make step3                       # run one step (and any earlier step it needs)
make PYTHON=/path/to/python      # use a specific python, e.g. a conda environment
```

Python packages needed: pandas, numpy, matplotlib, seaborn, geopandas, statsmodels, scipy.
Step 5 needs R (it installs the robustbase package itself if it is missing).
If R is not installed, step 5 is skipped and everything else still runs.

## The steps

| Step | Script | Original file | Reads | Creates |
|---|---|---|---|---|
| 1 | `01_understanding_livWell.py` | `Step1_Understanding_LivWell/understanding_livWell.py` | `raw/livwell.csv` | `processed/clean_livwell.csv` |
| 2 | `02_making_moderator_dataset.py` | `phase2/moderator_exploration/making_moderator_dataset.py` | `raw/livwell.csv` | `processed/cleaned_moderator_livwell.csv` |
| 3 | `03_analysis2.py` | `phase2/analysis2.py` | `processed/clean_livwell.csv` | Model 4, map (Figure 2), assumption plots (Figures A1–A3), bootstrap, 2% trim, `processed/threepluslivwell.csv` |
| 4 | `04_robustness_outliers.py` | `phase2/robustness_outliers.py` | `processed/clean_livwell.csv` | Model 4 without flagged outliers |
| 5 | `05_mmrobustness.R` | `phase2/mmrobustness.R` | `processed/threepluslivwell.csv` | MM-estimation |
| 6 | `06_moderators_within_region.py` | `phase2/moderator_exploration/moderators.py` | `processed/cleaned_moderator_livwell.csv` | moderator analyses within regions |
| 7 | `07_results_plots.py` | `phase2/results_plots.py` | `processed/clean_livwell.csv` | within-region plot (Figure 5): `plots/results_within_region_heat_effect.png` |
| 8 | `08_summarise_results.py` | new | `outputs/logs/` | `outputs/main_results_summary.txt` |
| 9 | `09_moderators_BETWEEN_region.py` | new | `processed/cleaned_moderator_livwell.csv` | moderator analyses between regions of the same country-survey (one fixed effect per country-survey), `plots/within_country_coefplot.png` (Figure 7) |
| 11 | `11_analysis2_without_SSA.py` | copy of step 3 | `processed/clean_livwell.csv` | main analysis without sub-Saharan Africa, CSV with `_noSSA` in the name |
| 12 | `12_report_figures.py` | new | `processed/` CSVs | report Figures 1, 3, 4, 6 and 8 in `plots/` (Georgia, project colours) |

Steps 1-7 are the original scripts. Only their file paths were changed, and plots
that are not in the report were removed.

## Data

- `inputs/raw/livwell.csv`: the LivWell dataset
  (https://www.pik-potsdam.de/en/output/projects/all/579).
- `inputs/raw/ne_110m_admin_0_countries.zip`: Natural Earth 1:110m country borders, for the
  maps. The original scripts downloaded it from
  https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip.
  A local copy is kept so the pipeline does not depend on that link
  (if the file is missing, `make` downloads it again from there).

## Notes on reproducibility

- The cluster bootstraps in steps 3 and 11 use `np.random.seed(42)`, and the
  MM-estimation in step 5 uses `set.seed(42)`, so their numbers stay the same on every run.
- The MM-estimation in step 5 does not converge (as noted in `analysis2.py`).
