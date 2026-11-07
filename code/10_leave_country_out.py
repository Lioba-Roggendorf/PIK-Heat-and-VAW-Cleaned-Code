# Robustness check: leave Peru out (and leave each country out once)
# Lioba Roggendorf
#
# Why: Peru has 35% of all observations, but heat is 0 in almost all Peruvian
# region-years. It can still influence the heat effect through the year fixed
# effects (which are shared by all countries). So: does the result hold without Peru?

import pandas as pd
import statsmodels.formula.api as smf
import warnings
warnings.filterwarnings("ignore")

livwell_3plus = pd.read_csv("../inputs/processed/threepluslivwell.csv")

model_formula = "dv ~ heat + rain + C(region_id) + C(year)"


def fit_model(data):
    # same model as the main analysis, SE clustered by region
    model = smf.ols(model_formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["region_id"]}
    )
    return model


# ______________________________________________________________________________
# 1. main model, for comparison

main_model = fit_model(livwell_3plus)
main_ci = main_model.conf_int().loc["heat"]
print(f"=== MAIN MODEL (n = {len(livwell_3plus)}, countries = {livwell_3plus['country'].nunique()}) ===")
print(f"Heat: {main_model.params['heat']:.4f} (SE: {main_model.bse['heat']:.4f}, "
      f"t = {main_model.tvalues['heat']:.3f}, p = {main_model.pvalues['heat']:.4f})")
print(f"95% CI: [{main_ci[0]:.4f}, {main_ci[1]:.4f}]")

# ______________________________________________________________________________
# 2. leave Peru out

no_peru = livwell_3plus[livwell_3plus["country"] != "PER"].copy()
no_peru_model = fit_model(no_peru)
no_peru_ci = no_peru_model.conf_int().loc["heat"]

print(f"\n=== WITHOUT PERU (n = {len(no_peru)}, countries = {no_peru['country'].nunique()}) ===")
print(f"Heat: {no_peru_model.params['heat']:.4f} (SE: {no_peru_model.bse['heat']:.4f}, "
      f"t = {no_peru_model.tvalues['heat']:.3f}, p = {no_peru_model.pvalues['heat']:.4f})")
print(f"95% CI: [{no_peru_ci[0]:.4f}, {no_peru_ci[1]:.4f}]")
print(f"R2: {no_peru_model.rsquared:.4f}, adjusted R2: {no_peru_model.rsquared_adj:.4f}")

# how much heat variation does Peru have at all?
peru = livwell_3plus[livwell_3plus["country"] == "PER"]
peru_nonzero = 0
for value in peru["heat"]:
    if value > 0:
        peru_nonzero += 1
print(f"\nPeru: {peru_nonzero} of {len(peru)} region-years have any extreme-heat months")

# ______________________________________________________________________________
# 3. leave each country out once

print("\n=== LEAVE ONE COUNTRY OUT ===")
print(f"{'left out':<10}{'n':>6}{'heat b':>10}{'SE':>8}{'p':>8}")

rows = []
for country in sorted(livwell_3plus["country"].unique()):
    subset = livwell_3plus[livwell_3plus["country"] != country].copy()
    model = fit_model(subset)
    rows.append({
        "left_out": country,
        "n": len(subset),
        "heat_b": model.params["heat"],
        "heat_se": model.bse["heat"],
        "heat_p": model.pvalues["heat"],
    })
    print(f"{country:<10}{len(subset):>6}{model.params['heat']:>10.3f}"
          f"{model.bse['heat']:>8.3f}{model.pvalues['heat']:>8.3f}")

results = pd.DataFrame(rows)
print(f"\nRange of heat coefficients: {results['heat_b'].min():.3f} to {results['heat_b'].max():.3f}")
