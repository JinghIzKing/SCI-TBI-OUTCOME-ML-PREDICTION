import pandas as pd
from collections import defaultdict

# READ CSV & CREATE ICD DATAFRAME
df = pd.read_csv("ICD Codes_12.17.24.csv", low_memory=False)
print(df.head())
symp_index = 0

# TBI DX DICTIONARY
tbi_dx = defaultdict(list)
for df_index, (index, row) in enumerate(df.dropna(how="all").iterrows()):
    if(row[0].strip() == "Associated Symptoms"):
        symp_index = df_index + 1
        break
    tbi_dx[row[0]] = [code.strip() for code in row[1:].dropna().tolist()]
print(tbi_dx)
print(tbi_dx.keys())
print(symp_index)

# TBI ASSOCIATED SYMPTOMS DICTIONARY
tbi_symp = defaultdict(list)
for index, row in df.dropna(how="all").iloc[symp_index:].iterrows():
    tbi_symp[row[0]] = [code.strip() for code in row[1:].dropna().tolist()]
print(tbi_symp)
print(tbi_symp.keys())

# TBI SYMPTOM CATEGORIES DICTIONARY
tbi_symp_cat = {
    "Surgical Interventions" : ["Bolt placement", "EVD", "decompressive hemicrani"],
    "Structural Pathology" : ["CSF rhinorrhea", "skull fracture", "open head injury"],
    "Infectious Pathology" : ["meningitis", "encephalitis", "brain abscess", "osteomylitis"],
    "Hematologic Pathology" : ["Acute traumatic coagulopathy", "DVT", "PE"],
    "Neurological Pathology Acute" : ["Hearing", "Vision", "Other", "Neurologic"],
    "Neurological Pathology Chronic/Progressive" : ["brain death", "Post-concussion syndrome", "Paroxysmal sympathetic hyperactivity", "Cerebral Edema", "hydro", "Seizures", "persistent vegetative state"],
    "Emotional/Behavioral/Cognitive" : ["Cognitive/Linguistic", "Emotional/Behavioral", "Sleep", "abuse"]
}

# COMBINING DX AND SYMPTOM CATEGORIES
tbi_combined = tbi_dx
for cat, symptoms in tbi_symp_cat.items():
    for symp in symptoms:
        tbi_combined[cat] = tbi_combined[cat] + tbi_symp[symp]
print(tbi_combined.keys())

# --------------- ONE HOT CODE ----------------

# READ COMBINED CSV & CREATE DATAFRAME
df = pd.read_csv("sci_coded.csv", low_memory=False)

# CREATE TBI COLUMNS AND INITIALIZE TO ZERO
for cat in tbi_combined.keys():
    df[cat] = 0

tbi_combined_set = {cat: set(codes) for cat, codes in tbi_combined.items()}

# ITERATE THROUGH AND ONE HOT CODE
for index, row in df.dropna(how="all").iterrows():
    for cat, codes in tbi_combined_set.items():
        if any(icd in codes for icd in row if icd):
            df.at[index, cat] = 1

df.to_csv("updated_combined.csv", index=False)

print("Processing complete. Saved to 'updated_combined.csv'.")