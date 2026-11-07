# Results Visualisations for the Main Model
# Lioba Roggendorf

"""
One plot for the Results section:
1. The within region heat effect (binned partial residual plot)

Uses the same colour palette as analysis2.py and moderators.py.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import OLSInfluence

# same colours as the rest of the project
orange = "#F8B195"
pink = "#F67280"
brighter_purple = "#C06C84"
darker_purple = "#6C5B7B"
blue = "#355C7D"

# a gradient built only from the same five colours, used to tell regions apart
from matplotlib.colors import LinearSegmentedColormap
region_cmap = LinearSegmentedColormap.from_list(
    "project_palette", [orange, pink, brighter_purple, darker_purple, blue]
)

save_plots_here = "../outputs/plots"

################################################################################
# STEP 1: Load and filter, same as analysis2.py
################################################################################

livwell_all = pd.read_csv("../inputs/processed/clean_livwell.csv")

years_per_region = livwell_all.groupby("region_id")["year"].nunique()
min_years = 3
valid_regions = years_per_region[years_per_region >= min_years].index
livwell_3plus = livwell_all[livwell_all["region_id"].isin(valid_regions)].copy()

# main model, same spec as the_holy_grail in analysis2.py
main_model = smf.ols(
    "dv ~ heat + rain + C(region_id) + C(year)", data=livwell_3plus
).fit(cov_type="cluster", cov_kwds={"groups": livwell_3plus["region_id"]})

main_beta = main_model.params["heat"]
main_se = main_model.bse["heat"]

print(f"Main model: heat = {main_beta:.4f} (SE {main_se:.4f})")

################################################################################
# PLOT 1: The within region heat effect (region average comparison)
################################################################################

"""
No transformation of the data at all here. Just the real heat and VAW values,
one dot per region year. A thin line connects each region's own points in
chronological order, so you can see that region's own path across its survey
years. The straight line uses the actual heat coefficient from the main
model (10.31), drawn through the overall average of the data, exactly the
slope reported in the results section.
"""

livwell_3plus = livwell_3plus.sort_values(["region_id", "year"])
region_ids = livwell_3plus["region_id"].unique()
region_color = {
    r: region_cmap(i / max(len(region_ids) - 1, 1)) for i, r in enumerate(region_ids)
}

fig, ax = plt.subplots(figsize=(9, 6))

# one thin line per region, connecting its own points across its survey years,
# each region gets its own shade from the project colour gradient
for region_id, group in livwell_3plus.groupby("region_id"):
    c = region_color[region_id]
    ax.plot(group["heat"], group["dv"], color=c, alpha=0.5, linewidth=1.1, zorder=1)
    ax.scatter(group["heat"], group["dv"], color=c, edgecolor="white",
               linewidth=0.4, alpha=0.85, s=32, zorder=2)

# the actual heat coefficient from the main model, drawn through the data average
mean_heat = livwell_3plus["heat"].mean()
mean_dv = livwell_3plus["dv"].mean()
x_line = np.linspace(livwell_3plus["heat"].min(), livwell_3plus["heat"].max(), 100)
y_line = mean_dv + main_beta * (x_line - mean_heat)
ax.plot(x_line, y_line, color=blue, linewidth=3, zorder=3, solid_capstyle="round",
        path_effects=[pe.Stroke(linewidth=4.5, foreground="white"), pe.Normal()],
        label=f"Main model heat coefficient ({main_beta:.2f})")

ax.set_xlabel("Heat (share of months with extreme temperature anomaly)", fontsize=11)
ax.set_ylabel("VAW prevalence (% of women, past 12 months)", fontsize=11)
ax.text(0.99, 0.02, "Each colour is one region; thin lines connect its own years over time",
        transform=ax.transAxes, ha="right", va="bottom", fontsize=9, color="#555555",
        style="italic")
ax.legend(fontsize=9, loc="upper right")

fig.suptitle("Heat and VAW", fontsize=16, fontweight="bold", color="#2b2b2b", y=1.02)
ax.set_title("Every region year in the data, with each region's own path over time",
             fontsize=10.5, style="italic", color="#555555", pad=12)

fig.tight_layout()
fig.savefig(f"{save_plots_here}/results_within_region_heat_effect.png", dpi=300,
            bbox_inches="tight", pad_inches=0.3)
plt.close(fig)
print("saved: results_within_region_heat_effect.png")

print("\nPlot saved to outputs/plots/")
