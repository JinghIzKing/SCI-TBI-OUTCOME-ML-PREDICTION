import pandas as pd

# Load CSV
files = "combined.csv"
df = pd.read_csv(files, dtype=str, low_memory=False)

# Ensure all codes are strings before processing
df.fillna("", inplace=True)  # Replace NaN with empty strings

# Drop columns dynamically using loops
for i in range(1, 26):
    df.drop(f"I10_PR{i}", axis=1, errors='ignore', inplace=True)

for i in range(1, 16):
    df.drop(f"PRDAY{i}", axis=1, errors='ignore', inplace=True)

# Dropping additional columns from a predefined list
remove = "HOSP_BEDSIZE HOSP_LOCTEACH HOSP_REGION H_CONTRL N_DISC_U N_HOSP_U S_DISC_U S_HOSP_U TOTAL_DISC I10_NDX"
df.drop(columns=remove.split(), errors='ignore', inplace=True)

df.drop(columns=["DISCWT", "TOTCHG", "AGE_NEONATE"], errors='ignore', inplace=True)

# Replacing values in 'DISPUNIFORM' column efficiently
df.loc[df['DISPUNIFORM'].isin([
    "Died in hospital",
    "Transfer other: includes Skilled Nursing Facility (SNF), Intermediate Care Facility (ICF), and another type of facility"
]), 'DISPUNIFORM'] = "poor"

df.loc[df['DISPUNIFORM'].isin([
    "Transfer to short-term hospital",
    "Home Health Care (HHC)",
    "Routine"
]), 'DISPUNIFORM'] = "good"

df.loc[~df['DISPUNIFORM'].isin(["poor", "good"]), 'DISPUNIFORM'] = "undefined"

# ICD-10 Chapters Dictionary (updated logic)
icd10_chapters = {
    "Infectious and parasitic diseases": ("A00", "B99"),
    "Neoplasms": ("C00", "D49"),
    "Blood & immune disorders": ("D50", "D89"),
    "Endocrine & metabolic diseases": ("E00", "E89"),
    "Mental & behavioral disorders": ("F01", "F99"),
    "Nervous system diseases": ("G00", "G99"),
    "Eye diseases": ("H00", "H59"),
    "Ear diseases": ("H60", "H95"),
    "Circulatory system diseases": ("I00", "I99"),
    "Respiratory system diseases": ("J00", "J99"),
    "Digestive system diseases": ("K00", "K95"),
    "Skin diseases": ("L00", "L99"),
    "Musculoskeletal diseases": ("M00", "M99"),
    "Genitourinary diseases": ("N00", "N99"),
    "Pregnancy & childbirth": ("O00", "O99"),
    "Perinatal conditions": ("P00", "P96"),
    "Congenital abnormalities": ("Q00", "Q99"),
    "Symptoms & abnormal findings": ("R00", "R99"),
    "Injuries & poisoning": ("S00", "T88"),
    "External causes": ("V00", "Y99"),
    "Health status & services": ("Z00", "Z99")
}

# Create one-hot encoding columns initialized to 0
df[list(icd10_chapters.keys())] = 0

# Identify correct ICD-10 code columns dynamically
icd_columns = [col for col in df.columns if col.startswith("I10_DX")]

# Process ICD codes and categorize them into chapters
for index, row in df[icd_columns].iterrows():
    for code in row.dropna():  # Drop empty values
        for chapter, (start, end) in icd10_chapters.items():
            if start <= code <= end:  # Proper range checking
                df.at[index, chapter] = 1

# Save updated CSV
df.to_csv('updated_combined.csv', index=False)
