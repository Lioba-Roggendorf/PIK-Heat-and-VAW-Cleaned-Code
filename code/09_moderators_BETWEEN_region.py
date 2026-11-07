import pandas as pd
import os
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.multitest import multipletests
import numpy as np

# The following code is the moderator analysis after our meeting at the PIK,
# where we decided to compare regions to each other,
# not only regions to themselves, across year.
# NOTE: confounding risk here is greater, this will be exploratory, descriptive.

# The model is now:
# VAW_rct = beta1 * Heat_rct
#           + beta2 * M_rct
#           + beta3 * (Heat_rct x M_rct)
#           + gamma * Rain_rct
#           + lambda_ct
#           + error_rct
#
#   r = region, c = country, t = survey year
#   M = one moderator at a time, centred at its mean
#   lambda_ct = one intercept per country-survey (76, e.g. Uganda 2011)
#
# so, I compare each region to other regions in the SAME country,
# in the SAME survey year (e.g. all regions of Uganda 2011).
# -> it is a within-country comparison: I control for country AND survey year
# together, so everything that differs between countries (like culture, laws,
# how the DHS was run) is removed, and also shocks that hit a whole country
# in that year (like national economic shocks, El Nino years).
#
# So, the question is: in regions that had more extreme heat months than the
# rest of their country that year, is violence against women higher than the
# rest of their country that year?
#
# And the question for the moderation: is this heat-violence relation different
# for regions with higher levels of the moderator (for example, more urban, more empowered... regions)?

# but NOTE, for power: heat varies little between regions of the same
# country-survey, so power is low.


# step 1, just like moderator analysis 06, prepare the data:

filename = "../inputs/processed/cleaned_moderator_livwell.csv"
save_plots_here = "../outputs/plots"

livwell_all = pd.read_csv(filename)


# use the same colours:
orange = "#F8B195"
pink = "#F67280"
brighter_purple = "#C06C84"
darker_purple = "#6C5B7B"
blue = "#355C7D"
colors = [orange, pink, brighter_purple, darker_purple, blue]

"""
________________________________________________________________________________
STEP 1: I do NOT filter for regions with >= 3 years now,
because I compare regions WITHIN countries, not only regions to themselves.
One survey per region is enough -> it still adds variance.

So, just specify the model.
BASE MODEL --> my model is now different! Model 4 only uses within-region
variance, but mine also uses variance between regions of the same country.
So I take out the region control C(region_id) and use C(country_year).
"""

# country-year column: this is now my fixed effect
# (one intercept per country-survey, e.g. "UGA_2011")
livwell_all["country_year"] = (
    livwell_all["country"].astype(str)
    + "_"
    + livwell_all["year"].astype(str)
)

# my model is base_within_country -> base model, but with one fixed effect
# per country-survey instead of region and year fixed effects
base_within_country = smf.ols(
    "dv ~ heat + rain + C(country_year)",
    data=livwell_all
).fit(
    cov_type="cluster",
    cov_kwds={"groups": livwell_all["region_id"]}
)

print("\nBASE MODEL, WITHIN COUNTRY-SURVEYS (reference)")
print(f"Heat: {base_within_country.params['heat']:.4f} (SE: {base_within_country.bse['heat']:.4f}, p = {base_within_country.pvalues['heat']:.4f})")


"""
________________________________________________________________________________
STEP 2: Which variables are useful for the moderators?
"""

# exactly like 06, original moderator analysis
Urbanicity = ['DM_urban_p']
Empowerment_Human_Capital = ['ED_educ_years_mean', 'ED_litt_p']
Empowerment_Information_Access = ['EI_internet_week_p','EI_news_week_p', 'EI_radio_week_p', 'EI_tv_week_p']
Empowerment_Economic = ['DP_decide_money_p', 'DP_earn_more_equal_p', 'WK_working_paid_p', 'DP_owns_house_p', 'DP_owns_land_p']
Empowerment_Autonomy = ['DP_decide_health_p', 'DP_decide_large_purchase_p', 'DP_decide_visits_p', 'DP_decide_contraception_p', 'DP_decide_no_contraception_p']
Partner_Violence_Proportion = ['DV_phys_partner_12m_p', 'DV_phys_12m_p']
Wealth_Moderation = ['WL_wealth_median']
Age_Gap = ['DM_age_diff_mean', 'DM_age_diff_10plus_p']
Cooling_Access = ['EI_women_elec_p']
# exactly like 06, original moderator analysis


"""
________________________________________________________________________________
STEP 3: Make the empowerment score
"""

# exactly like 06, original moderator analysis
education_max = livwell_all['ED_educ_years_mean'].max()
percentage_edu = []
for education in livwell_all['ED_educ_years_mean']:
    proportion = education/education_max
    percentage = proportion * 100
    percentage_edu.append(percentage)

education_score = []
for i in range(len(percentage_edu)):
    total = percentage_edu[i] + livwell_all['ED_litt_p'].iloc[i]
    av = total/2
    education_score.append(av)

livwell_all["education_empowerment_score"] = education_score


def score_maker(df, variables, non_percent_vars):

    list_of_lists = []
    for col in variables:
        proportion_list = []
        if col in non_percent_vars:
            max_val = df[col].max()

            if pd.isna(max_val) or max_val == 0:
                proportion_list = [0 for _ in df[col]]
            else:
                for row in df[col]:
                    proportion_list.append((row / max_val) * 100)

            list_of_lists.append(proportion_list)

        else:
            list_of_lists.append(df[col].tolist())

    score = []

    for i in range(len(list_of_lists[0])):
        available = []
        for listt in list_of_lists:
            value = listt[i]
            if not pd.isna(value):
                available.append(value)

        if len(available) > 0:
            total = 0
            for value in available:
                total += value
            score.append(total / len(available))
        else:
            score.append(np.nan)

    return score


livwell_all["info_empowerment_score"] = score_maker(
    livwell_all,
    Empowerment_Information_Access,
    []
)

livwell_all["economic_empowerment_score"] = score_maker(
    livwell_all,
    Empowerment_Economic,
    ['WK_working_paid_p']
)

livwell_all["autonomy_empowerment_score"] = score_maker(
    livwell_all,
    Empowerment_Autonomy,
    []
)

overall_empowerment = []
for i in range(len(livwell_all["autonomy_empowerment_score"])):

    available_scores = []

    autonomy  = livwell_all["autonomy_empowerment_score"].iloc[i]
    info      = livwell_all["info_empowerment_score"].iloc[i]
    economic  = livwell_all["economic_empowerment_score"].iloc[i]
    education = livwell_all["education_empowerment_score"].iloc[i]

    if not pd.isna(autonomy):
        available_scores.append(autonomy)
    if not pd.isna(info):
        available_scores.append(info)
    if not pd.isna(economic):
        available_scores.append(economic)
    if not pd.isna(education):
        available_scores.append(education)

    if len(available_scores) > 0:
        total = 0
        for s in available_scores:
            total += s
        overall_empowerment.append(total / len(available_scores))
    else:
        overall_empowerment.append(np.nan)

livwell_all['overall_empowerment_score'] = overall_empowerment
# exactly like 06, original moderator analysis


"""
________________________________________________________________________________
STEP 4: ASSUMPTIONS
"""

# only my five moderators now
# (age gap: only the mean, DM_age_diff_mean)
all_moderators = {
    "empowerment": ["overall_empowerment_score"],
    "cooling": Cooling_Access,
    "age_gap_mean": ["DM_age_diff_mean"],
    "wealth": Wealth_Moderation,
    "urbanicity": Urbanicity,
}

# ______________________________________________________________________________
# CHECK 1: within-COUNTRY-SURVEY variance instead of within-region variance,
# because the country-survey fixed effects remove everything that differs between
# country-surveys. What is left to test is how much a moderator differs within a country-survey.

print("#" * 20)
print("CHECK 1: WITHIN-COUNTRY-SURVEY VARIANCE")
print("#" * 20)
print("Mean std close to 0 = moderator barely differs within country-surveys.")
print("Then it can't be tested, because country-survey fixed effects remove the rest.")
print()

for group, moderator_list in all_moderators.items():
    for moderator in moderator_list:

        country_year_stds = []

        for country_year in livwell_all["country_year"].unique():
            # get all rows for this one country-survey
            country_year_rows = livwell_all[livwell_all["country_year"] == country_year]
            moderator_values = country_year_rows[moderator].dropna()

            # need at least 2 data points to compute a std
            if len(moderator_values) >= 2:
                std = moderator_values.std()
                country_year_stds.append(std)

        if len(country_year_stds) == 0:
            print(f"{moderator}: no valid country-surveys found")
        else:
            mean_std = np.mean(country_year_stds)
            print(f"{moderator:<35}  mean within-country-survey std = {mean_std:.4f}")

print('\n')


# ______________________________________________________________________________
# CHECK 2 and CHECK 3 (correlation with heat, VIF)

# exactly like 06, original moderator analysis
print("#" * 20)
print("CHECK 2: CORRELATION WITH HEAT")
print("#" * 20)
print('\n')

for group, moderator_list in all_moderators.items():
    for moderator in moderator_list:

        temp_df = livwell_all[["heat", moderator]].dropna()
        correlation = temp_df["heat"].corr(temp_df[moderator])
        print(f"{moderator:<35}  r = {correlation:.4f}")

print('\n')

print("#" * 20)
print("CHECK 3: VIF")
print("#" * 20)
print("VIF > 5 problem.  VIF > 10 problem problem.")
print()

for group, moderator_list in all_moderators.items():
    for moderator in moderator_list:

        temp_df = livwell_all[["heat", "rain", moderator]].dropna().copy()

        if len(temp_df) == 0:
            print(f"Moderator: {moderator}  --> skipped (no data after dropping NAs)")
            print()
            continue

        temp_df["const"] = 1

        vif_fomrat = temp_df[["heat", "rain", moderator, "const"]].values

        vif_heat      = variance_inflation_factor(vif_fomrat, 0)
        vif_rain      = variance_inflation_factor(vif_fomrat, 1)
        vif_moderator = variance_inflation_factor(vif_fomrat, 2)

        print(f"Moderator: {moderator}")
        print(f"  heat VIF      = {vif_heat:.4f}")
        print(f"  rain VIF      = {vif_rain:.4f}")
        print(f"  moderator VIF = {vif_moderator:.4f}")
        print()
# exactly like 06, original moderator analysis


"""
________________________________________________________________________________
STEP 5: NOW DO THE ANALYSIS
"""

# same function as in 06, but:
# - C(country_year) instead of C(region_id) + C(year)
# - clusters are regions, like the main model
def run_selected_moderations(data, my_moderators):

    print("\n\n")
    print("#"*20)
    print("\n")
    print("MODERATION RESULTS INCOMIIING")
    print("#"*20)

    results = []

    for group, moderator_list in my_moderators.items():

        print(f"\n\n### {group.upper()} ###")
        print("-" * 40)

        for moderator in moderator_list:

            subset = data.dropna(subset=[moderator]).copy()

            # if nothing is left after dropping NAs, skip
            if len(subset) == 0:
                print(f"{moderator:<30} --> skipped (no rows left after dropping NAs)")
                continue

            # need at least 2 years and 2 countries for the fixed effects to work
            if subset["year"].nunique() < 2 or subset["country"].nunique() < 2:
                print(f"{moderator:<30} --> skipped (not enough years or countries left)")
                continue

            # centre the moderator
            subset[moderator + "_c"] = subset[moderator] - subset[moderator].mean()

            n_obs = len(subset)
            n_clusters = subset["region_id"].nunique()

            # country-survey fixed effects, clustered by region
            model = smf.ols(
                f"dv ~ heat * {moderator}_c + rain + C(country_year)",
                data=subset
            ).fit(
                cov_type="cluster",
                cov_kwds={"groups": subset["region_id"]}
            )

            term = f"heat:{moderator}_c"

            estimate = model.params[term]
            se = model.bse[term]
            p_val = model.pvalues[term]

            print(
                f"{moderator:<30} "
                f"β={estimate:>8.4f} "
                f"SE={se:>8.4f} "
                f"p={p_val:>8.4f} "
                f"(n={n_obs}, clusters={n_clusters})"
            )

            results.append({
                "group": group,
                "moderator": moderator,
                "beta": estimate,
                "se": se,
                "p": p_val,
                "heat_at_average": model.params["heat"],  # also keep beta1
                "n": n_obs,
                "clusters": n_clusters
            })

    return results

results = run_selected_moderations(livwell_all, all_moderators)


# correct for testing 5 moderators
p_values = []
for result in results:
    p_values.append(result["p"])

p_bh = multipletests(p_values, method="fdr_bh")[1]

print("\nBH-CORRECTED P-VALUES (5 tests)")
for i in range(len(results)):
    results[i]["p_bh"] = p_bh[i]
    print(f"{results[i]['moderator']:<30} p={results[i]['p']:.4f}  p_BH={p_bh[i]:.4f}")


"""
________________________________________________________________________________
STEP 6: plotsssss
"""

# exactly like 06, original moderator analysis
moderator_labels = []
betas = []
ses = []

for result in results:
    moderator_labels.append(result["moderator"])
    betas.append(result["beta"])
    ses.append(result["se"])

ci_lower = []
ci_upper = []
for i in range(len(betas)):
    ci_lower.append(betas[i] - 1.96 * ses[i])
    ci_upper.append(betas[i] + 1.96 * ses[i])

fig, ax = plt.subplots(figsize=(9, 5))

for i in range(len(moderator_labels)):

    ax.plot(
        [ci_lower[i], ci_upper[i]],
        [i, i],
        color=blue,
        linewidth=2,
        alpha=0.7
    )

    ax.plot(
        betas[i], i,
        marker="o",
        color=pink,
        markersize=8,
        zorder=3
    )

ax.axvline(x=0, color="black", linewidth=1.2, linestyle="--", alpha=0.5, label="no effect")

ax.set_yticks(range(len(moderator_labels)))
ax.set_yticklabels(moderator_labels, fontsize=10)
ax.set_xlabel("Interaction coefficient β  (heat × moderator)  with 95% CI", fontsize=10)
# exactly like 06, original moderator analysis

# clearer labels for the paper (same names as in Table 2)
clearer_names = {
    "overall_empowerment_score": "Empowerment",
    "EI_women_elec_p": "Cooling (electricity access)",
    "DM_age_diff_mean": "Age gap (mean)",
    "WL_wealth_median": "Wealth",
    "DM_urban_p": "Urbanicity",
}
clearer_labels = []
for label in moderator_labels:
    clearer_labels.append(clearer_names[label])
ax.set_yticklabels(clearer_labels, fontsize=10)

ax.set_title("Moderation within country-surveys: heat × moderator interaction", fontsize=11)
ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig(save_plots_here + "/within_country_coefplot.png", dpi=150)
plt.show()
print("saved: within_country_coefplot.png")
