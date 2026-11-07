import pandas as pd
import os
import matplotlib.pyplot as plt
import geopandas as gpd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import linear_reset
from statsmodels.graphics.gofplots import qqplot
import seaborn as sns
from scipy import stats
from scipy.stats import binom
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.outliers_influence import OLSInfluence
from math import comb
import numpy as np


filename = "../inputs/processed/clean_livwell.csv"
save_plots_here = "../outputs/plots"

livwell_all = pd.read_csv(filename)

# sub-Saharan African countries left out (analysed in Peisker, Hoffmann et al., 2026), everything else is the same as 03_analysis2.py
sub_saharan_countries = ["BFA", "CIV", "CMR", "COD", "ETH", "KEN", "LBR", "MLI", "MOZ", "MWI", "NAM", "NGA", "RWA", "SEN", "SLE", "TGO", "TZA", "UGA", "ZAF", "ZMB", "ZWE"]
livwell_all = livwell_all[~livwell_all["country"].isin(sub_saharan_countries)].copy()

print(livwell_all.shape)
print(livwell_all.columns)


years_per_region = (
    livwell_all
    .groupby("region_id")["year"]
    .nunique()
)

print("\n=== YEARS PER REGION SUMMARY ===")
print(years_per_region.describe())


min_years = 3
filterr = (years_per_region >= min_years)
valid_regions = years_per_region[filterr].index

print("valid regions:")
print(valid_regions)

livwell_3plus = livwell_all[
    livwell_all["region_id"].isin(valid_regions)
].copy()

region_years_3plus = (
    livwell_3plus
    .groupby(["region_id", "year"])
    .size()
    .reset_index(name="n_obs")
)


print("\n###FILTERED SAMPLE (≥3 YEARS)###")
print("Regions:", livwell_3plus["region_id"].nunique())
print("Observations/region-years:", len(livwell_3plus))

print("Mean years/region:", years_per_region[valid_regions].mean())
print("Median years/region:", years_per_region[valid_regions].median())


countries_left = sorted(livwell_3plus["country"].unique())

print("\n#################################")
print("COUNTRIES IN FINAL ANALYSIS SAMPLE")
print("###################################")

print(f"Number of countries: {len(countries_left)}\n")

for c in countries_left:
    print(c)


country_counts = (
    livwell_3plus
    .groupby("country")
    .size()
    .reset_index(name="n_obs")
)

print(country_counts.sort_values("n_obs", ascending=False))




orange = "#F8B195"
pink = "#F67280"
brighter_purple = "#C06C84"
darker_purple = "#6C5B7B"
blue = "#355C7D"
colors = [orange, pink, brighter_purple, darker_purple, blue]


the_holy_grail = smf.ols("dv ~ heat + rain + C(region_id) + C(year)", data=livwell_3plus).fit(
    cov_type="cluster", cov_kwds={"groups": livwell_3plus["region_id"]}
)

print('############# heat variance! ################')
print(livwell_3plus.groupby("region_id")["heat"].std().describe())


the_holy_grail_two_degree_poly_version = smf.ols("dv ~ heat + I(heat**2) + rain + C(region_id) + C(year)", data=livwell_3plus).fit(
    cov_type="cluster", cov_kwds={"groups": livwell_3plus["region_id"]}
)
print(f'\n\nBase model AIC: {the_holy_grail.aic},\n Square model AIC: {the_holy_grail_two_degree_poly_version.aic}.\n\n')


heatAndRain = livwell_3plus[["heat", "rain"]]
heatCol = 0
print("VIF Columns:", heatAndRain.columns)
vifHeat = variance_inflation_factor(heatAndRain.values, heatCol)
print(f"VIF for heat: {vifHeat}")

influence = OLSInfluence(the_holy_grail)
cooks, _ = influence.cooks_distance
stdandardizedResiduals = influence.resid_studentized_internal

threshold = 4 / len(livwell_3plus)
print(f"Observations with Cook's distance > {threshold:.4f}:")
print(livwell_3plus[cooks > threshold])

print(f"\nObservations with |standardised residual| > 3:")
print(livwell_3plus[abs(stdandardizedResiduals) > 3])

cooking = livwell_3plus.index[cooks > threshold].tolist()
farfarawaydatapoints = livwell_3plus.index[abs(stdandardizedResiduals) > 3].tolist()
outliers = list(set(cooking + farfarawaydatapoints))
print(f"Outlier count: {len(outliers)}")



print('\nMODEL INCOMING:\n\n')
print(the_holy_grail.summary())
print('\n\n')

print('\nSIGNIFICANCE INCOMING:\n\n')
print(f"Heat coefficient: {the_holy_grail.params['heat']} (SE: {the_holy_grail.bse['heat']}, p = {the_holy_grail.pvalues['heat']})")
print('\n\n')


livwell_3plus.to_csv("../inputs/processed/threepluslivwell_noSSA.csv")

reps = 500

booted_heat_betas = []


regions = np.sort(livwell_3plus["region_id"].unique())
regioncount = len(regions)

booted_heat_betas = []

np.random.seed(42)

print("\nRunning simple cluster bootstrap...")

for boot in range(reps):
    boot_regions = np.random.choice(regions, size=regioncount, replace=True)

    sampled = []
    for region in boot_regions:
        mask = (livwell_3plus["region_id"] == region)
        selected = livwell_3plus[mask]
        sampled.append(selected)

    sampled = pd.concat(sampled, ignore_index=True)
    boot_model = smf.ols(
        "dv ~ heat + rain + C(region_id) + C(year)",
        data=sampled
    ).fit(
        cov_type="cluster",
        cov_kwds={"groups": sampled["region_id"]}
    )


    booted_heat_betas.append(boot_model.params["heat"])

booted_heat_betas = np.array(booted_heat_betas)


print("\nBOOTSTRAP RESULTS (heat coefficient)")
print("------------------------------------")
print(f"Mean: {booted_heat_betas.mean():.4f}")
print(f"Std (bootstrap SE): {booted_heat_betas.std():.4f}")
print(f"95% CI: [{np.percentile(booted_heat_betas, 2.5):.4f}, "
      f"{np.percentile(booted_heat_betas, 97.5):.4f}]")

print("Skew:", pd.Series(booted_heat_betas).skew())
print("Min:", booted_heat_betas.min())
print("Max:", booted_heat_betas.max())


lower = livwell_3plus["dv"].quantile(0.02)
upper = livwell_3plus["dv"].quantile(0.98)

livwell_trimmed = livwell_3plus[
    (livwell_3plus["dv"] >= lower) &
    (livwell_3plus["dv"] <= upper)
].copy()

print("Original n:", len(livwell_3plus))
print("Trimmed n:", len(livwell_trimmed))

trimmed_model = smf.ols(
    "dv ~ heat + rain + C(region_id) + C(year)",
    data=livwell_trimmed
).fit(
    cov_type="cluster",
    cov_kwds={"groups": livwell_trimmed["region_id"]}
)

print(trimmed_model.summary())

print("\nHeat (original):", the_holy_grail.params["heat"])
print("Heat (trimmed): ", trimmed_model.params["heat"])
