# Pipeline for the main analysis:
# Does Extreme Heat Increase Violence Against Women?
# Lioba Roggendorf
#
# How to use it (in a terminal, inside main_analysis_publishable_version/):
#   make                         run the whole pipeline (only re-runs what changed)
#   make -B                      force every step to run again
#   make step3                   run one step (plus any earlier step it needs)
#   make PYTHON=/path/to/python  use a specific python (e.g. a conda environment)
#
# Every script runs from inside code/, so it finds the data with "../inputs/..."
# and saves plots with "../outputs/plots".
# The full printout of every step is saved to outputs/logs/,
# and the last step collects the main numbers into outputs/main_results_summary.txt.

PYTHON  ?= python3
RSCRIPT ?= Rscript

# plots are only saved to files, so plt.show() does not pause the pipeline
export MPLBACKEND = Agg

RAW_DATA  = inputs/raw/livwell.csv
WORLD_MAP = inputs/raw/ne_110m_admin_0_countries.zip
LOGS      = outputs/logs

STEP1 = $(LOGS)/01_understanding_livWell.txt
STEP2 = $(LOGS)/02_making_moderator_dataset.txt
STEP3 = $(LOGS)/03_analysis2.txt
STEP4 = $(LOGS)/04_robustness_outliers.txt
STEP5 = $(LOGS)/05_mmrobustness.txt
STEP6 = $(LOGS)/06_moderators_within_region.txt
STEP7 = $(LOGS)/07_results_plots.txt
STEP9 = $(LOGS)/09_moderators_BETWEEN_region.txt
STEP11 = $(LOGS)/11_analysis2_without_SSA.txt
STEP12 = $(LOGS)/12_report_figures.txt
SUMMARY = outputs/main_results_summary.txt

.PHONY: all step1 step2 step3 step4 step5 step6 step7 step9 step11 step12 summary folders

all: $(SUMMARY) $(STEP12)

step1: $(STEP1)
step2: $(STEP2)
step3: $(STEP3)
step4: $(STEP4)
step5: $(STEP5)
step6: $(STEP6)
step7: $(STEP7)
step9: $(STEP9)
step11: $(STEP11)
step12: $(STEP12)
summary: $(SUMMARY)

folders:
	@mkdir -p inputs/processed outputs/plots $(LOGS)

# A step's printout is first written to a ".running" file and only renamed to
# its final .txt name when the script finished without errors. That way a failed
# step is run again next time, and its error message stays in the .running file.

# --- the world map used for the map plots (only downloaded if it is missing) ---
$(WORLD_MAP):
	curl -L -o $(WORLD_MAP) https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip

# --- STEP 1: clean the raw LivWell data -> inputs/processed/clean_livwell.csv ---
$(STEP1): code/01_understanding_livWell.py $(RAW_DATA) $(WORLD_MAP) | folders
	@echo "Step 1: 01_understanding_livWell.py"
	@cd code && $(PYTHON) -u 01_understanding_livWell.py > ../$@.running 2>&1 \
		&& mv ../$@.running ../$@ \
		|| (tail -n 25 ../$@.running; echo "FAILED, see $@.running"; exit 1)

# --- STEP 2: clean the raw LivWell data with the moderator variables ---
$(STEP2): code/02_making_moderator_dataset.py $(RAW_DATA) | folders
	@echo "Step 2: 02_making_moderator_dataset.py"
	@cd code && $(PYTHON) -u 02_making_moderator_dataset.py > ../$@.running 2>&1 \
		&& mv ../$@.running ../$@ \
		|| (tail -n 25 ../$@.running; echo "FAILED, see $@.running"; exit 1)

# --- STEP 3: main analysis (Model 4), assumption checks, bootstrap, 2% trim ---
$(STEP3): code/03_analysis2.py $(STEP1) $(WORLD_MAP) | folders
	@echo "Step 3: 03_analysis2.py (includes the bootstrap, may take a minute)"
	@cd code && $(PYTHON) -u 03_analysis2.py > ../$@.running 2>&1 \
		&& mv ../$@.running ../$@ \
		|| (tail -n 25 ../$@.running; echo "FAILED, see $@.running"; exit 1)

# --- STEP 4: robustness check, Model 4 without the flagged outliers ---
$(STEP4): code/04_robustness_outliers.py $(STEP1) | folders
	@echo "Step 4: 04_robustness_outliers.py"
	@cd code && $(PYTHON) -u 04_robustness_outliers.py > ../$@.running 2>&1 \
		&& mv ../$@.running ../$@ \
		|| (tail -n 25 ../$@.running; echo "FAILED, see $@.running"; exit 1)

# --- STEP 5: robustness check, MM-estimation in R (skipped if R is not installed) ---
$(STEP5): code/05_mmrobustness.R $(STEP3) | folders
	@echo "Step 5: 05_mmrobustness.R"
	@if command -v $(RSCRIPT) > /dev/null; then \
		cd code && $(RSCRIPT) 05_mmrobustness.R > ../$@.running 2>&1 \
		&& mv ../$@.running ../$@ \
		|| (tail -n 25 ../$@.running; echo "FAILED, see $@.running"; exit 1); \
	else \
		echo "Rscript not found, step 5 was skipped. Install R and run: make -B step5" > $@; \
		cat $@; \
	fi

# --- STEP 6: moderator analyses, within regions ---
$(STEP6): code/06_moderators_within_region.py $(STEP2) | folders
	@echo "Step 6: 06_moderators_within_region.py"
	@cd code && $(PYTHON) -u 06_moderators_within_region.py > ../$@.running 2>&1 \
		&& mv ../$@.running ../$@ \
		|| (tail -n 25 ../$@.running; echo "FAILED, see $@.running"; exit 1)

# --- STEP 7: the three plots for the results section ---
$(STEP7): code/07_results_plots.py $(STEP1) | folders
	@echo "Step 7: 07_results_plots.py"
	@cd code && $(PYTHON) -u 07_results_plots.py > ../$@.running 2>&1 \
		&& mv ../$@.running ../$@ \
		|| (tail -n 25 ../$@.running; echo "FAILED, see $@.running"; exit 1)

# --- STEP 9: moderator analyses, between regions of the same country-survey ---
$(STEP9): code/09_moderators_BETWEEN_region.py $(STEP2) | folders
	@echo "Step 9: 09_moderators_BETWEEN_region.py"
	@cd code && $(PYTHON) -u 09_moderators_BETWEEN_region.py > ../$@.running 2>&1 \
		&& mv ../$@.running ../$@ \
		|| (tail -n 25 ../$@.running; echo "FAILED, see $@.running"; exit 1)

# --- STEP 11: main analysis (as step 3) without sub-Saharan African countries ---
$(STEP11): code/11_analysis2_without_SSA.py $(STEP1) $(WORLD_MAP) | folders
	@echo "Step 11: 11_analysis2_without_SSA.py (includes the bootstrap, may take a minute)"
	@cd code && $(PYTHON) -u 11_analysis2_without_SSA.py > ../$@.running 2>&1 \
		&& mv ../$@.running ../$@ \
		|| (tail -n 25 ../$@.running; echo "FAILED, see $@.running"; exit 1)

# --- STEP 12: report Figures 1, 3, 4, 6 and 8, in Georgia ---
$(STEP12): code/12_report_figures.py $(STEP1) $(STEP2) | folders
	@echo "Step 12: 12_report_figures.py"
	@cd code && $(PYTHON) -u 12_report_figures.py > ../$@.running 2>&1 \
		&& mv ../$@.running ../$@ \
		|| (tail -n 25 ../$@.running; echo "FAILED, see $@.running"; exit 1)

# --- STEP 8: collect the main printouts into one short text file ---
$(SUMMARY): code/08_summarise_results.py $(STEP1) $(STEP2) $(STEP3) $(STEP4) $(STEP5) $(STEP6) $(STEP7) $(STEP9) $(STEP11)
	@echo "Step 8: 08_summarise_results.py"
	@cd code && $(PYTHON) 08_summarise_results.py
	@echo "Done. Main results: $(SUMMARY)"
