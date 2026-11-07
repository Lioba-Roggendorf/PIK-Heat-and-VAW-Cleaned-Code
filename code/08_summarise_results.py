# Summary of the main printouts
# Lioba Roggendorf

"""
This is the last step of the pipeline. It does not compute anything new.
It reads the full printouts of steps 1-7 (saved in outputs/logs/)
and copies the most important lines into one short text file:
outputs/main_results_summary.txt

If you want to see everything a script printed, open its file in outputs/logs/.
"""

import os
from datetime import datetime

logs_folder = "../outputs/logs"
plots_folder = "../outputs/plots"
summary_file = "../outputs/main_results_summary.txt"


################################################################################
# helper functions
################################################################################

def read_log(log_name):
    # returns all lines of one log file as a list
    path = os.path.join(logs_folder, log_name)
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    return lines


def lines_starting_with(lines, beginnings):
    # keeps every line that starts with one of the beginnings, in log order
    found = []
    for line in lines:
        clean_line = line.strip()
        for beginning in beginnings:
            if clean_line.startswith(beginning):
                found.append(clean_line)
                break
    return found


def lines_containing(lines, text):
    found = []
    for line in lines:
        if text in line:
            found.append(line.strip())
    return found


def lines_after(lines, marker, how_many):
    # the line with the marker, plus the next how_many lines
    for i in range(len(lines)):
        if marker in lines[i]:
            return lines[i:i + how_many + 1]
    return []


################################################################################
# collect the lines
################################################################################

log1 = read_log("01_understanding_livWell.txt")
log2 = read_log("02_making_moderator_dataset.txt")
log3 = read_log("03_analysis2.txt")
log4 = read_log("04_robustness_outliers.txt")
log5 = read_log("05_mmrobustness.txt")
log6 = read_log("06_moderators_within_region.txt")
log9 = read_log("09_moderators_BETWEEN_region.txt")
log11 = read_log("11_analysis2_without_SSA.txt")

summary = []

summary.append("MAIN RESULTS SUMMARY")
summary.append("Does Extreme Heat Increase Violence Against Women?")
summary.append(f"Pipeline run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
summary.append("Full printouts of every step are in outputs/logs/")
summary.append("")

# --- step 1 ---
summary.append("=" * 80)
summary.append("1. DATA CLEANING (01_understanding_livWell.py)")
summary.append("=" * 80)
summary += lines_starting_with(log1, [
    "Excluding countries",
    "Observations before",
    "Countries before",
    "Countries:",
    "Regions:",
    "Years:",
])
summary.append("")

# --- step 2 ---
summary.append("=" * 80)
summary.append("2. MODERATOR DATASET (02_making_moderator_dataset.py)")
summary.append("=" * 80)
summary += lines_starting_with(log2, [
    "Excluding countries",
    "number of countries",
    "number of regions",
    "Years:",
])
summary.append("")

# --- step 3 ---
summary.append("=" * 80)
summary.append("3. MAIN ANALYSIS, MODEL 4 (03_analysis2.py)")
summary.append("   dv ~ heat + rain + C(region_id) + C(year), SEs clustered by region")
summary.append("=" * 80)
summary.append("Sample (regions with >= 3 years):")
summary += lines_starting_with(log3, [
    "Regions:",
    "Observations/region-years:",
    "Mean years/region:",
    "Median years/region:",
    "Number of countries:",
])

# the country codes are printed one per line after "Number of countries"
country_lines = lines_after(log3, "Number of countries", 30)
countries = []
for line in country_lines[1:]:
    clean_line = line.strip()
    if clean_line == "":
        continue
    # the list ends where the country_counts table starts
    if clean_line.startswith("country"):
        break
    countries.append(clean_line)
summary.append("Countries: " + ", ".join(countries))
summary.append("")

summary.append("Main model:")
summary += lines_starting_with(log3, ["Heat coefficient:"])
summary += lines_containing(log4[:4], "R2:")
summary.append("")

summary.append("Assumption checks:")
summary += lines_starting_with(log3, [
    "Base model AIC",
    "Square model AIC",
    "VIF for heat",
    "Outlier count",
])
summary.append("")

summary.append("Cluster bootstrap (500 reps, resampling whole regions):")
summary += lines_starting_with(log3, [
    "Mean:",
    "Std (bootstrap SE):",
    "95% CI:",
])
summary.append("")

summary.append("2% trimmed DV:")
summary += lines_starting_with(log3, [
    "Original n:",
    "Trimmed n:",
    "Heat (original):",
    "Heat (trimmed):",
])
# the 'heat' rows of the two regression tables: first = main model, second = trimmed
coefficient_header = lines_starting_with(log3, ["coef"])
heat_rows = lines_starting_with(log3, ["heat "])
if len(coefficient_header) > 0 and len(heat_rows) >= 2:
    summary.append("")
    summary.append("                  " + coefficient_header[0])
    summary.append("main model:       " + heat_rows[0])
    summary.append("trimmed model:    " + heat_rows[1])
summary.append("")

# --- step 4 ---
summary.append("=" * 80)
summary.append("4. ROBUSTNESS: EXCLUDING FLAGGED OUTLIERS (04_robustness_outliers.py)")
summary.append("=" * 80)
for line in log4:
    summary.append(line)
summary.append("")

# --- step 5 ---
summary.append("=" * 80)
summary.append("5. ROBUSTNESS: MM-ESTIMATION IN R (05_mmrobustness.R)")
summary.append("=" * 80)
mm_lines = lines_containing(log5, "skipped")
mm_lines += lines_containing(log5, "did not converge")
mm_lines += lines_starting_with(log5, ["heat "])
if len(mm_lines) == 0:
    mm_lines = ["(no heat coefficient found, see outputs/logs/05_mmrobustness.txt)"]
summary += mm_lines
summary.append("")

# --- step 6 ---
summary.append("=" * 80)
summary.append("6. MODERATOR ANALYSES, WITHIN REGIONS (06_moderators_within_region.py)")
summary.append("   dv ~ heat * moderator + rain + C(region_id) + C(year)")
summary.append("=" * 80)
summary += lines_starting_with(log6, ["Heat:"])
summary.append("Interaction terms (heat x moderator):")
summary += lines_containing(log6, "β=")
summary.append("")
summary += lines_after(log6, "mean proportion of violence", 1)
summary.append("")

# --- step 9 ---
summary.append("=" * 80)
summary.append("9. MODERATOR ANALYSES, WITHIN COUNTRY-SURVEYS (09_moderators_BETWEEN_region.py)")
summary.append("   dv ~ heat * M_c + rain + C(country_year), SEs clustered by country")
summary.append("=" * 80)
summary += lines_after(log9, "BASE MODEL, WITHIN COUNTRY-SURVEYS", 1)
summary.append("Interaction terms (heat x moderator):")
summary += lines_containing(log9, "β=")
summary.append("")
summary += lines_after(log9, "BH-CORRECTED P-VALUES", 5)
summary.append("")

# --- step 11 ---
summary.append("=" * 80)
summary.append("11. MAIN ANALYSIS WITHOUT SUB-SAHARAN AFRICA (11_analysis2_without_SSA.py)")
summary.append("   same as step 3, sub-Saharan African countries left out (Peisker, Hoffmann et al., 2026)")
summary.append("=" * 80)
summary += lines_starting_with(log11, [
    "Regions:",
    "Observations/region-years:",
    "Number of countries:",
])
country_lines = lines_after(log11, "Number of countries", 30)
countries = []
for line in country_lines[1:]:
    clean_line = line.strip()
    if clean_line == "":
        continue
    if clean_line.startswith("country"):
        break
    countries.append(clean_line)
summary.append("Countries: " + ", ".join(countries))
summary.append("")
summary += lines_starting_with(log11, ["Heat coefficient:"])
summary.append("")
summary.append("Cluster bootstrap:")
summary += lines_starting_with(log11, ["Mean:", "Std (bootstrap SE):", "95% CI:"])
summary.append("")
summary += lines_starting_with(log11, ["Original n:", "Trimmed n:", "Heat (original):", "Heat (trimmed):"])
summary.append("")

# --- list of plots ---
summary.append("=" * 80)
summary.append("PLOTS SAVED IN outputs/plots/")
summary.append("=" * 80)
for plot_name in sorted(os.listdir(plots_folder)):
    if not plot_name.startswith("."):
        summary.append(plot_name)

################################################################################
# save it
################################################################################

with open(summary_file, "w", encoding="utf-8") as f:
    for line in summary:
        f.write(line + "\n")

print(f"saved: {summary_file}")
