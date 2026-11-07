# Figures for the report
# Lioba Roggendorf

"""
Five figures of the report, in the document's font (Georgia)
and in the same colours as all other plots of this project.

mechanisms_diagram.png         Figure 1, three pathways from heat to VAW and the moderators tested
model_figure.png               Figure 3, the main model and its terms
empowerment_construction.png   Figure 4, how the empowerment score is built
region_comparison.png          Figure 6, heat effect with / without Sub-Saharan Africa, by world region
moderator_interactions.png     Figure 8, heat effect at different levels of empowerment and urbanicity
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
from matplotlib.colors import to_rgb, to_hex
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
import warnings
warnings.filterwarnings("ignore")

save_plots_here = "../outputs/plots"

# same colours as the rest of the project
orange = "#F8B195"
pink = "#F67280"
brighter_purple = "#C06C84"
darker_purple = "#6C5B7B"
blue = "#355C7D"
text_dark = "#2A2A2A"   # text colour of the document
text_grey = "#666666"
line_grey = "#BBBBBB"
light_grey = "#D9D9D9"


def darker(colour, amount):
    # mixes a colour with the dark text colour, so light colours
    # (orange, pink) are still readable as text on white
    c = to_rgb(colour)
    d = to_rgb(text_dark)
    mixed = []
    for i in range(3):
        mixed.append(c[i] * (1 - amount) + d[i] * amount)
    return to_hex(mixed)


# pick the document font if it is installed
installed_fonts = []
for font in fm.fontManager.ttflist:
    installed_fonts.append(font.name)

serif_font = "DejaVu Serif"
for font_name in ["Georgia", "Gelasio"]:
    if font_name in installed_fonts:
        serif_font = font_name
        break
print(f"font used: {serif_font}")

plt.rcParams["font.family"] = serif_font
plt.rcParams["mathtext.fontset"] = "custom"
plt.rcParams["mathtext.rm"] = serif_font
plt.rcParams["mathtext.it"] = serif_font + ":italic"
plt.rcParams["mathtext.bf"] = serif_font + ":bold"
plt.rcParams["axes.edgecolor"] = text_grey
plt.rcParams["text.color"] = text_dark
plt.rcParams["axes.labelcolor"] = text_dark
plt.rcParams["xtick.color"] = text_dark
plt.rcParams["ytick.color"] = text_dark
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.spines.right"] = False
mono_font = "DejaVu Sans Mono"


def add_titles(fig, title, subtitle):
    fig.text(0.02, 0.985, title, fontsize=15, fontweight="bold", va="top", ha="left")
    fig.text(0.02, 0.925, subtitle, fontsize=10.5, color=text_grey, style="italic", va="top", ha="left")


def add_note(fig, note):
    fig.text(0.02, 0.01, note, fontsize=8.5, color=text_grey, va="bottom", ha="left")


def box(ax, x, y, w, h, colour, title, lines, title_colour="white", line_colour="white", title_size=11.5, line_size=9.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2", color=colour, zorder=2))
    ax.text(x + w / 2, y + h - 2.6, title, ha="center", va="center", fontsize=title_size, fontweight="bold",
            color=title_colour, zorder=3)
    for i in range(len(lines)):
        ax.text(x + w / 2, y + h - 6.2 - i * 3.3, lines[i], ha="center", va="center", fontsize=line_size,
                color=line_colour, zorder=3)


def arrow(ax, start, end, colour="#9A9A9A"):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12, color=colour, linewidth=1.3, zorder=1))


################################################################################
# FIGURE 1: mechanisms diagram
################################################################################

fig, ax = plt.subplots(figsize=(11, 7.6))
fig.subplots_adjust(left=0.01, right=0.99, top=0.87, bottom=0.07)
ax.set_xlim(0, 110)
ax.set_ylim(0, 86)
ax.axis("off")

box(ax, 1, 37, 15, 12, blue, "Extreme", ["heat"], title_size=13, line_size=13)
ax.texts[-1].set_fontweight("bold")
box(ax, 94, 37, 15, 12, pink, "Violence", ["against women"], title_size=13, line_size=10.5)

# the pathways are the mediators: the effect of heat runs THROUGH them
pathways = [
    ("1  Stressors", ["income loss in agriculture", "discomfort, irritability", "drinking, hormonal effects"], darker_purple, 58),
    ("2  Enabler", ["displacement", "breakdown of support", "networks and policing"], brighter_purple, 35),
    ("3  Amplifier", ["resource insecurity", "household conflict", "care and water burden"], orange, 12),
]
for title, lines, colour, y in pathways:
    title_colour = text_dark if colour == orange else "white"
    box(ax, 36, y, 34, 16, colour, title, lines, title_colour=title_colour, line_colour=title_colour,
        title_size=11.5, line_size=9.5)
    arrow(ax, (16, 43), (36, y + 8))
    arrow(ax, (70, y + 8), (94, 43))


def moderator_tag(x, y, w, h, colour, lines, target):
    # moderators are NOT on the path: they point at an arrow and change how strong that link is
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1",
                                facecolor="white", edgecolor=colour, linewidth=1.6, zorder=2))
    ax.text(x + w / 2, y + h - 2.2, "Moderators tested", ha="center", va="center", fontsize=9.5,
            fontweight="bold", color=colour, zorder=3)
    ax.text(x + w / 2, y + h / 2 - 1.4, lines, ha="center", va="center", fontsize=9.5, color=text_dark,
            zorder=3, linespacing=1.15)
    start_y = y if target[1] < y else y + h
    ax.add_patch(FancyArrowPatch((target[0], start_y), target, arrowstyle="-|>", mutation_scale=12,
                                 color=colour, linewidth=1.5, linestyle=(0, (4, 2.5)), zorder=4))
    ax.scatter([target[0]], [target[1]], s=28, color=colour, zorder=5)


# points on the pathway -> VAW arrows where the moderators act (x = 82)
moderator_tag(73, 75, 18, 10, darker_purple, "wealth \u00b7 urbanicity\ncooling access", (82, 54.5))
moderator_tag(73, 1, 18, 10, darker(orange, 0.4), "empowerment\nspousal age gap", (82, 31.5))
ax.text(80, 44.3, "not tested\n(no displacement data)", ha="center", va="bottom", fontsize=8.5,
        color=text_grey, style="italic", linespacing=1.1)

# small legend: mediator vs. moderator
ax.add_patch(FancyBboxPatch((2, 17), 5, 3.4, boxstyle="round,pad=0,rounding_size=0.6", color=light_grey, zorder=2))
ax.text(9, 18.7, "Mediator (pathway):\nheat works through it", fontsize=9, va="center", linespacing=1.1)
arrow(ax, (2, 7), (8, 7))
ax.add_patch(FancyArrowPatch((5, 12), (5, 7.3), arrowstyle="-|>", mutation_scale=9, color=text_grey,
                             linewidth=1.3, linestyle=(0, (4, 2.5)), zorder=4))
ax.scatter([5], [7], s=18, color=text_grey, zorder=5)
ax.text(9, 8.5, "Moderator: changes how\nstrong a link is", fontsize=9, va="center", linespacing=1.1)

add_titles(fig, "How heat could lead to violence against women",
           "The pathways carry the effect (mediators); the moderators tested here could make it stronger or weaker")
add_note(fig, "Pathways after Pearson et al. (2026); examples from the Possible Mechanisms section. "
              "Assignment of moderators to pathways is a simplification; several moderators relate to more than one pathway.")
fig.savefig(f"{save_plots_here}/mechanisms_diagram.png", dpi=300)
plt.close(fig)
print("saved: mechanisms_diagram.png")

################################################################################
# FIGURE 3: the main model
################################################################################

# each term: (formula text, colour, description, LivWell variable)
terms = [
    (r"$VAW_{rt}$", blue,
     "“Women who experienced physical violence in the past 12 months (%)”",
     "DV_phys_12m_p"),
    (r"$\beta \cdot Heat_{rt}$", pink,
     "“Share of months in the past 12 months with a positive temperature\nanomaly exceeding 2 SD”",
     "tmp_anom_p2sd_share12"),
    (r"$\gamma \cdot Rain_{rt}$", brighter_purple,
     "“Mean precipitation anomaly, the average monthly deviation from\nthe long run precipitation mean (past 12 months)”",
     "pre_anom_mean12"),
    (r"$\alpha_{r}$", darker_purple,
     "Region fixed effects, absorbing stable, time invariant differences\nbetween regions",
     ""),
    (r"$\tau_{t}$", orange,
     "Year fixed effects, absorbing shocks or trends common to all\nregions in a given year",
     ""),
    (r"$\varepsilon_{rt}$", "#8A8A8A",
     "Error term",
     ""),
]

fig, ax = plt.subplots(figsize=(10, 7.6))
ax.set_xlim(0, 100)
ax.set_ylim(0, 76)
ax.axis("off")

# the equation at the top, one coloured piece after the other
equation_pieces = [
    (r"$VAW_{rt}$", blue),
    (r"$\ =\ $", text_dark),
    (r"$\beta \cdot Heat_{rt}$", pink),
    (r"$\ +\ $", text_dark),
    (r"$\gamma \cdot Rain_{rt}$", brighter_purple),
    (r"$\ +\ $", text_dark),
    (r"$\alpha_{r}$", darker_purple),
    (r"$\ +\ $", text_dark),
    (r"$\tau_{t}$", darker(orange, 0.25)),
    (r"$\ +\ $", text_dark),
    (r"$\varepsilon_{rt}$", "#8A8A8A"),
]

# first measure the total width, then centre the equation
renderer = fig.canvas.get_renderer()
widths = []
for piece, colour in equation_pieces:
    t = ax.text(0, 0, piece, fontsize=24)
    extent = t.get_window_extent(renderer=renderer).transformed(ax.transData.inverted())
    widths.append(extent.width)
    t.remove()

x = 50 - sum(widths) / 2
for i in range(len(equation_pieces)):
    piece, colour = equation_pieces[i]
    ax.text(x, 71, piece, fontsize=24, color=colour, va="center", ha="left")
    x += widths[i]

ax.plot([5, 95], [65.5, 65.5], color=line_grey, linewidth=0.8)

# one row per term
row_y = [60, 51, 41, 31, 23, 15.5]
for i in range(len(terms)):
    label, colour, description, livwell_name = terms[i]
    y = row_y[i]
    label_colour = colour
    if colour in [orange, pink]:
        label_colour = darker(colour, 0.25)
    ax.add_patch(Rectangle((5, y - 1.2), 2.3, 2.3, color=colour))
    ax.text(9.5, y, label, fontsize=15, color=label_colour, va="center")
    ax.text(31, y + 0.8, description, fontsize=11.5, color=text_dark, va="center", linespacing=1.15)
    if livwell_name != "":
        if "\n" in description:
            name_y = y - 3.9
        else:
            name_y = y - 2.2
        ax.text(31, name_y, "LivWell: " + livwell_name, fontsize=9.5, color="#8A8A8A",
                family=mono_font, style="italic", va="center")

ax.plot([5, 95], [10, 10], color=line_grey, linewidth=0.8)
ax.text(50, 6.5, "Standard errors are clustered at the region level.", fontsize=12,
        color=text_grey, style="italic", ha="center", va="center")

fig.savefig(f"{save_plots_here}/model_figure.png", dpi=300, bbox_inches="tight", pad_inches=0.15)
plt.close(fig)
print("saved: model_figure.png")


################################################################################
# FIGURE 4: the empowerment composite
################################################################################

# each domain: (name, box colour, text colour in the box, indicators)
domains = [
    ("Autonomy", darker_purple, "white", [
        ("DP_decide_health_p", "Decides on own health care"),
        ("DP_decide_large_purchase_p", "Decides on large household purchases"),
        ("DP_decide_visits_p", "Decides on visits to family/relatives"),
        ("DP_decide_contraception_p", "Decides on contraceptive use"),
        ("DP_decide_no_contraception_p", "Decides on non-use of contraception"),
    ]),
    ("Human Capital / Education", brighter_purple, "white", [
        ("ED_educ_years_mean", "Mean years of education*"),
        ("ED_litt_p", "Literacy rate"),
    ]),
    ("Information Access", pink, "white", [
        ("EI_internet_week_p", "Weekly internet use"),
        ("EI_news_week_p", "Weekly newspaper use"),
        ("EI_radio_week_p", "Weekly radio use"),
        ("EI_tv_week_p", "Weekly television use"),
    ]),
    ("Economic Empowerment", orange, text_dark, [
        ("DP_decide_money_p", "Decides how own earnings are spent"),
        ("DP_earn_more_equal_p", "Earns more than or equal to partner"),
        ("WK_working_paid_p", "Currently in paid work"),
        ("DP_owns_house_p", "Owns a house (alone or jointly)"),
        ("DP_owns_land_p", "Owns land (alone or jointly)"),
    ]),
]

fig, ax = plt.subplots(figsize=(16, 7.4))
ax.set_xlim(0, 160)
ax.set_ylim(0, 74)
ax.axis("off")

ax.text(80, 71, "Constructing the Women's Empowerment Composite", fontsize=21,
        fontweight="bold", color=text_dark, ha="center", va="center")
ax.text(80, 67, "Mean of four equally-weighted domain scores, each a mean of its DHS/LivWell indicators",
        fontsize=12.5, color=text_grey, style="italic", ha="center", va="center")

# top box
top_left, top_width, top_bottom, top_height = 50, 60, 53.5, 9
ax.add_patch(FancyBboxPatch((top_left, top_bottom), top_width, top_height,
                            boxstyle="round,pad=0,rounding_size=0.8", color=blue))
ax.text(80, 59.6, "Women's Empowerment Composite", fontsize=15, fontweight="bold",
        color="white", ha="center", va="center")
ax.text(80, 55.9, "mean of the 4 domain scores below", fontsize=11, color="#D9E2EA",
        ha="center", va="center")

box_width, box_height, box_bottom = 35, 8, 39
box_lefts = [3, 43, 83, 123]

for i in range(len(domains)):
    name, colour, box_text_colour, indicators = domains[i]
    left = box_lefts[i]
    centre = left + box_width / 2

    # arrow from the top box to the domain box
    domain_arrow = FancyArrowPatch((80, top_bottom), (centre, box_bottom + box_height),
                            arrowstyle="-|>", mutation_scale=9, color="#9A9A9A", linewidth=1)
    ax.add_patch(domain_arrow)

    ax.add_patch(FancyBboxPatch((left, box_bottom), box_width, box_height,
                                boxstyle="round,pad=0,rounding_size=0.8", color=colour))
    ax.text(centre, box_bottom + box_height / 2, name, fontsize=13.5, fontweight="bold",
            color=box_text_colour, ha="center", va="center")

    # short line under the box
    ax.plot([centre, centre], [box_bottom, box_bottom - 1.3], color=colour, linewidth=1.5)

    name_colour = colour
    if colour in [orange, pink]:
        name_colour = darker(colour, 0.3)

    y = 34
    for variable, description in indicators:
        ax.plot([left + 0.6, left + 0.6], [y - 3.4, y + 0.6], color=colour, linewidth=2.2)
        ax.text(left + 2.2, y, variable, fontsize=10.5, fontweight="bold", color=name_colour,
                family=mono_font, va="center")
        ax.text(left + 2.2, y - 2.6, description, fontsize=10.5, color=text_dark, va="center")
        y -= 5.9

fig.savefig(f"{save_plots_here}/empowerment_construction.png", dpi=300, bbox_inches="tight", pad_inches=0.15)
plt.close(fig)
print("saved: empowerment_construction.png")

################################################################################
# data and main model for Figure 6 (same as 03_analysis2.py)
################################################################################

sub_saharan = ["CMR", "MLI", "MWI", "NGA", "SEN", "UGA", "ZMB", "ZWE"]
latin_america = ["COL", "HTI", "PER"]
asia_middle_east = ["KHM", "PHL", "JOR"]


livwell_all = pd.read_csv("../inputs/processed/clean_livwell.csv")
years_per_region = livwell_all.groupby("region_id")["year"].nunique()
valid_regions = years_per_region[years_per_region >= 3].index
livwell_3plus = livwell_all[livwell_all["region_id"].isin(valid_regions)].copy()

model_formula = "dv ~ heat + rain + C(region_id) + C(year)"


def fit(data, formula=model_formula):
    return smf.ols(formula, data=data).fit(cov_type="cluster", cov_kwds={"groups": data["region_id"]})


def estimate(data, formula=model_formula):
    m = fit(data, formula)
    ci = m.conf_int().loc["heat"]
    return {"b": m.params["heat"], "lo": ci[0], "hi": ci[1], "p": m.pvalues["heat"], "n": len(data),
            "countries": data["country"].nunique()}


main = estimate(livwell_3plus)
print(f"main model: {main['b']:.2f}")


def forest(ax, labels, results, colours, main_value=None):
    # one row per estimate: point + 95% CI, label on the left, value on the right
    y_positions = list(range(len(labels)))[::-1]
    for i in range(len(labels)):
        r = results[i]
        y = y_positions[i]
        ax.plot([r["lo"], r["hi"]], [y, y], color=colours[i], linewidth=2.6, solid_capstyle="round", alpha=0.85)
        filled = r["p"] < 0.05
        ax.plot(r["b"], y, marker="o", markersize=9, zorder=3,
                markerfacecolor=colours[i] if filled else "white", markeredgecolor=colours[i], markeredgewidth=2)
        p_text = "p < .001" if r["p"] < 0.001 else f"p = {r['p']:.3f}".replace("0.", ".")
        ax.text(1.01, y, f"{r['b']:.2f}   {p_text}", transform=ax.get_yaxis_transform(),
                va="center", fontsize=9.5, color=text_dark)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels, fontsize=10.5)
    ax.axvline(0, color=text_dark, linewidth=1, linestyle="--", alpha=0.6)
    if main_value is not None:
        ax.axvline(main_value, color=blue, linewidth=1, linestyle=":", alpha=0.8)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Heat coefficient (b) with 95% CI", fontsize=10)


################################################################################
# FIGURE 6: with / without Sub-Saharan Africa, by world region
################################################################################

samples = [
    ("All 14 countries (main model)", livwell_3plus, blue),
    ("Without Sub-Saharan Africa (6)", livwell_3plus[~livwell_3plus["country"].isin(sub_saharan)], pink),
    ("Sub-Saharan Africa only (8)", livwell_3plus[livwell_3plus["country"].isin(sub_saharan)], darker_purple),
    ("Latin America & Caribbean (3)", livwell_3plus[livwell_3plus["country"].isin(latin_america)], brighter_purple),
    ("Southeast Asia & Middle East (3)", livwell_3plus[livwell_3plus["country"].isin(asia_middle_east)], orange),
]
labels = []
results = []
colours = []
for label, data, colour in samples:
    labels.append(label)
    results.append(estimate(data))
    colours.append(colour)

fig, ax = plt.subplots(figsize=(8, 4.3))
fig.subplots_adjust(left=0.33, right=0.82, top=0.80, bottom=0.2)
forest(ax, labels, results, colours, main_value=main["b"])
add_titles(fig, "The heat effect beyond Sub-Saharan Africa",
           "Outside Sub-Saharan Africa the effect is larger; it is concentrated in Latin America")
add_note(fig, "Model 4 (region and year fixed effects, rainfall control) run on each subsample. Filled dots: p < .05; "
              "open dots: not significant.\nDotted line: main model estimate. Number of countries in brackets.")
fig.savefig(f"{save_plots_here}/region_comparison.png", dpi=300)
plt.close(fig)
print("saved: region_comparison.png")
################################################################################
# FIGURE 8: the heat effect at different levels of empowerment and urbanicity
# (same model as 09_moderators_BETWEEN_region.py)
################################################################################

moderators = pd.read_csv("../inputs/processed/cleaned_moderator_livwell.csv")
moderators["country_year"] = moderators["country"].astype(str) + "_" + moderators["year"].astype(str)


def score(df, variables, non_percent_vars):
    scaled = []
    for col in variables:
        if col in non_percent_vars:
            scaled.append(df[col] / df[col].max() * 100)
        else:
            scaled.append(df[col])
    return pd.concat(scaled, axis=1).mean(axis=1, skipna=True)


moderators["edu"] = (moderators["ED_educ_years_mean"] / moderators["ED_educ_years_mean"].max() * 100 + moderators["ED_litt_p"]) / 2
moderators["info"] = score(moderators, ["EI_internet_week_p", "EI_news_week_p", "EI_radio_week_p", "EI_tv_week_p"], [])
moderators["econ"] = score(moderators, ["DP_decide_money_p", "DP_earn_more_equal_p", "WK_working_paid_p",
                                        "DP_owns_house_p", "DP_owns_land_p"], ["WK_working_paid_p"])
moderators["auto"] = score(moderators, ["DP_decide_health_p", "DP_decide_large_purchase_p", "DP_decide_visits_p",
                                        "DP_decide_contraception_p", "DP_decide_no_contraception_p"], [])
moderators["empowerment"] = moderators[["auto", "info", "econ", "edu"]].mean(axis=1, skipna=True)

# Benjamini-Hochberg over the same five moderators as in step 9
five = ["empowerment", "EI_women_elec_p", "DM_age_diff_mean", "WL_wealth_median", "DM_urban_p"]
models = {}
for column in five:
    data = moderators.dropna(subset=[column]).copy()
    data["M_c"] = data[column] - data[column].mean()
    models[column] = (data, smf.ols("dv ~ heat * M_c + rain + C(country_year)", data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["region_id"]}))
raw_p = []
for column in five:
    raw_p.append(models[column][1].pvalues["heat:M_c"])
bh_p = dict(zip(five, multipletests(raw_p, method="fdr_bh")[1]))


def apa_p(p):
    return f"{p:.3f}".lstrip("0")


panels = [("Empowerment", "empowerment", "Empowerment score (0–100)", darker_purple),
          ("Urbanicity", "DM_urban_p", "Women living in urban areas (%)", brighter_purple)]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), sharey=True)
fig.subplots_adjust(left=0.09, right=0.98, top=0.78, bottom=0.23, wspace=0.08)
for k in range(2):
    name, column, xlabel, colour = panels[k]
    ax = axes[k]
    data, m = models[column]
    cov = m.cov_params()
    xs = np.linspace(data[column].quantile(0.05), data[column].quantile(0.95), 60)
    slopes = []
    lower = []
    upper = []
    for x in xs:
        c = x - data[column].mean()
        slope = m.params["heat"] + m.params["heat:M_c"] * c
        se = np.sqrt(cov.loc["heat", "heat"] + c ** 2 * cov.loc["heat:M_c", "heat:M_c"] + 2 * c * cov.loc["heat", "heat:M_c"])
        slopes.append(slope)
        lower.append(slope - 1.96 * se)
        upper.append(slope + 1.96 * se)
    ax.fill_between(xs, lower, upper, color=colour, alpha=0.18, linewidth=0)
    ax.plot(xs, slopes, color=colour, linewidth=2.8)
    ax.axhline(0, color=text_dark, linewidth=1, linestyle="--", alpha=0.6)
    ax.set_xlabel(xlabel, fontsize=10)
    ax.set_title(f"{name}: interaction p = {apa_p(m.pvalues['heat:M_c'])}, after correction p = {apa_p(bh_p[column])}",
                 fontsize=10, color=text_dark, loc="left")
    ax.grid(axis="y", color=light_grey, linewidth=0.6)
axes[0].set_ylabel("Heat effect on VAW (b)", fontsize=10)
add_titles(fig, "Is heat less harmful in more empowered and more urban regions?",
           "The heat effect tends to shrink as empowerment and urbanicity rise, but the uncertainty is large")
add_note(fig, "Heat effect implied by the moderator model (country-survey fixed effects), from the 5th to the 95th "
              "percentile of each moderator. Band: 95% CI.\nNeither interaction is significant after Benjamini-Hochberg correction.")
fig.savefig(f"{save_plots_here}/moderator_interactions.png", dpi=300)
plt.close(fig)
print("saved: moderator_interactions.png")
