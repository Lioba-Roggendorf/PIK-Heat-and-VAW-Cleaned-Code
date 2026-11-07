if (!requireNamespace("robustbase", quietly = TRUE)) install.packages("robustbase", repos = "https://cloud.r-project.org")
library(robustbase)

data <- read.csv("../inputs/processed/threepluslivwell.csv")

set.seed(42)

mm_model <- lmrob(
  dv ~ heat + rain + factor(region_id) + factor(year),
  data = data
)

summary(mm_model)
