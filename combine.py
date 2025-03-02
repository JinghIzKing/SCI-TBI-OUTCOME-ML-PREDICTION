import pandas as pd

# List of file paths
files = [
    "patients with TBI and SCI.csv",
    "patients_with_SCI.csv",
    "patients_with_TBI.csv"
]

dfs = []
array = ["Both", "SCI", "TBI"]
for i, f in enumerate(files):
    df = pd.read_csv(f)
    df['source'] = array[i]
    dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)

# Drop columns dynamically using loops
for i in range(1, 26):
    combined_df.drop(f"I10_PR{i}", axis=1, errors='ignore', inplace=True)

for i in range(1, 16):
    combined_df.drop(f"PRDAY{i}", axis=1, errors='ignore', inplace=True)

# Dropping additional columns from a predefined list
remove = "HOSP_BEDSIZE HOSP_LOCTEACH HOSP_REGION H_CONTRL N_DISC_U N_HOSP_U S_DISC_U S_HOSP_U TOTAL_DISC I10_NDX APRDRG_Risk_Mortality APRDRG_Severity"
combined_df.drop(columns=remove.split(), errors='ignore', inplace=True)

combined_df.drop(columns=["DISCWT", "TOTCHG", "AGE_NEONATE"], errors='ignore', inplace=True)

# Replacing values in 'DISPUNIFORM' column efficiently
combined_df.loc[combined_df['DISPUNIFORM'].isin([
    "Died in hospital",
    "Transfer other: includes Skilled Nursing Facility (SNF), Intermediate Care Facility (ICF), and another type of facility"
]), 'DISPUNIFORM'] = "poor"

combined_df.loc[combined_df['DISPUNIFORM'].isin([
    "Transfer to short-term hospital",
    "Home Health Care (HHC)",
    "Routine"
]), 'DISPUNIFORM'] = "good"

combined_df.loc[~combined_df['DISPUNIFORM'].isin(["poor", "good"]), 'DISPUNIFORM'] = "undefined"

combined_df.to_csv("combined.csv", index=False)

combined_df.fillna("", inplace=True)

print(combined_df.head())