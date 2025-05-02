library(dplyr)
library(rlang)
library(writexl)

# Load your data
df <- read.csv("hot_encoded.csv")

Pfunction <- function(df, col_name, value) {
  totalTBI <- sum(df$source == "TBI", na.rm = TRUE)
  totalSCI <- sum(df$source == "SCI", na.rm = TRUE)
  totalBoth <- sum(df$source == "Both", na.rm = TRUE)
  
  count_TBI <- df %>%
    filter(source == "TBI", !!sym(col_name) == value) %>%
    summarise(n = n()) %>%
    pull(n)
  
  count_SCI <- df %>%
    filter(source == "SCI", !!sym(col_name) == value) %>%
    summarise(n = n()) %>%
    pull(n)
  
  count_Both <- df %>%
    filter(source == "Both", !!sym(col_name) == value) %>%
    summarise(n = n()) %>%
    pull(n)
  
  n_TBI <- ifelse(length(count_TBI) == 0, 0, count_TBI)
  n_SCI <- ifelse(length(count_SCI) == 0, 0, count_SCI)
  n_Both <- ifelse(length(count_Both) == 0, 0, count_Both)
  
  # Run proportion tests
  test_TBI_SCI <- prop.test(x = c(n_TBI, n_SCI), n = c(totalTBI, totalSCI), correct = FALSE)
  test_TBI_Both <- prop.test(x = c(n_TBI, n_Both), n = c(totalTBI, totalBoth), correct = FALSE)
  test_SCI_Both <- prop.test(x = c(n_SCI, n_Both), n = c(totalSCI, totalBoth), correct = FALSE)
  
  return(data.frame(
    feature = col_name,
    value = value,
    count_TBI = n_TBI,
    count_SCI = n_SCI,
    count_Both = n_Both,
    prop_TBI = n_TBI / totalTBI,
    prop_SCI = n_SCI / totalSCI,
    prop_Both = n_Both / totalBoth,
    p_value_TBI_SCI = test_TBI_SCI$p.value,
    p_value_TBI_Both = test_TBI_Both$p.value,
    p_value_SCI_Both = test_SCI_Both$p.value
  ))
}
Pfuntion_mean <- function(df, col_name) {
  group_TBI <- df[[col_name]][df$source == "TBI"]
  group_SCI <- df[[col_name]][df$source == "SCI"]
  group_Both <- df[[col_name]][df$source == "Both"]

  mean_TBI <- mean(group_TBI, na.rm = TRUE)
  mean_SCI <- mean(group_SCI, na.rm = TRUE)
  mean_Both <- mean(group_Both, na.rm = TRUE)

  test_TBI_SCI <- t.test(group_TBI, group_SCI)
  test_TBI_Both <- t.test(group_TBI, group_Both)
  test_SCI_Both <- t.test(group_SCI, group_Both)

  return(data.frame(
    feature = col_name,
    mean_TBI = mean_TBI,
    mean_SCI = mean_SCI,
    mean_Both = mean_Both,
    p_value_TBI_SCI = test_TBI_SCI$p.value,
    p_value_TBI_Both = test_TBI_Both$p.value,
    p_value_SCI_Both = test_SCI_Both$p.value
  ))
}


# Categorical values to test
gender_features <- list("Male", "Female")
race_features <- list("White", "Black", "Hispanic", "Asian or Pacific Islander", "Native American", "Other")
Mortality_features <- list("Died", "Did not die")
Insurance_features <- list("Medicare", "Medicaid", "Private insurance", "Self-pay", "No charge", "Other")
Location_features <- list(
  "Counties in metro areas of 250,000-999,999 population",
  "Counties in metro areas of 50,000-249,999 population",
  "Micropolitan counties",
  '"Central" counties of metro areas of >=1 million population',
  '"Fringe" counties of metro areas of >=1 million population',
  "Not metropolitan or micropolitan counties"
)

# Run categorical feature analysis
categorical_results <- list()

for (val in gender_features) {
  categorical_results[[length(categorical_results) + 1]] <- Pfunction(df, "FEMALE", val)
}
for (val in race_features) {
  categorical_results[[length(categorical_results) + 1]] <- Pfunction(df, "RACE", val)
}
for (val in Mortality_features) {
  categorical_results[[length(categorical_results) + 1]] <- Pfunction(df, "DIED", val)
}
for (val in Insurance_features) {
  categorical_results[[length(categorical_results) + 1]] <- Pfunction(df, "PAY1", val)
}
for (val in Location_features) {
  categorical_results[[length(categorical_results) + 1]] <- Pfunction(df, "PL_NCHS", val)
}

# Combine into data frame
categorical_df <- do.call(rbind, categorical_results)

# Continuous features
feature_list <- c("AGE", "LOS", "TOTCHG", "PRDAY1")
continuous_df <- do.call(rbind, lapply(feature_list, function(f) Pfuntion_mean(df, f)))

# Write to Excel with two sheets
write_xlsx(
  list(
    "Categorical_Proportions" = categorical_df,
    "Continuous_Means" = continuous_df
  ),
  path = "table111.xlsx"
)
continuous_df