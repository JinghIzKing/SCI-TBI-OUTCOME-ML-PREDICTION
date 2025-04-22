import pandas as pd
from collections import defaultdict

data_file = "combined.csv"
icd_file = "Elixhauser_comorbiditiesICD10.csv"

df = pd.read_csv(data_file, encoding="utf-8", low_memory=False)

# CREATE ELIXHAUSER DICTIONARY
icd10_code = {}
with open(icd_file, "r", encoding="utf-8") as file:
    for line in file:
        category, *codes = line.strip().split(",")
        icd10_code[category] = [code.strip().replace(".", "") for code in codes if code.strip()]

print("Loaded ICD-10 categories:", icd10_code.keys())
print("Values", icd10_code.values())
print("Yay")


print("Read Elixhauser")

# CREATE SCI DICTIONARIES
# READ CSV & CREATE ICD DATAFRAME
df_sci = pd.read_csv("ICD Codes_12.17.24_SCI.csv", encoding="utf-8", low_memory=False)
print(df_sci.head())
new_dict_cat = "Cervical"
new_dict_index = 0

print("Read SCI ICDs")

# SCI DX & DX CATEGORY DICTIONARY
sci_dx = defaultdict(lambda: defaultdict(list))
for df_index, (index, row) in enumerate(df_sci.dropna(how="all").iterrows()):
    print("Can iterate CSV")
    if row.iloc[0].strip() == "Cervical":
        new_dict_cat = "Cervical"
        print("Cervical")
    elif row.iloc[0].strip() == "Lumbar and Sacral":
        new_dict_cat = "Lumbar and Sacral"
        print("Lumbar and Sacral")
    elif row.iloc[0].strip() == "Thoracic":
        new_dict_cat = "Thoracic"
        print("Thoracic")
    elif row.iloc[0].strip() == "Associated Complications":
        new_dict_cat = "Associated Complications & Symptoms"
        print("Associated Complications")
    elif row.iloc[0].strip() == "Associated Symptoms":
        print("Associated Symptoms")
    sci_dx[new_dict_cat][row.iloc[0]] = [code.strip() for code in row[1:].dropna().tolist()]
print(sci_dx)
print(sci_dx.items())

# SCI SYMPTOMS & COMPLICATIONS CATEGORY DICTIONARY
sci_cat = {
    "Neurological Complications": [
        "Paraplegia",
        "Tetraplegia",
        "Spinal Shock",
        "Autonomic Dysreflexia",
        "Autonomic Dysfunction",
        "Reflex Issues",
        "Sensory Loss",
        "Paralysis",
        "Sequelae of SCI"
    ],
    "Musculoskeletal & Mobility Issues": [
        "Muscle Contractures",
        "Spasticity & Muscle Tone Issues",
        "Musculoskeletal deformity (spasticity)",
        "Weakness/Fatigue",
        "Osteoporosis",
        "Spinal Deformity",
        "Spinal Fracture",
        "Skeletal Issues"
    ],
    "Pain & Discomfort": [
        "Chronic Pain",
        "Neuropathic Pain",
        "Pain"
    ],
    "Skin & Pressure-Related Conditions": [
        "Pressure Ulcers",
        "Skin Conditions and Pressure Issues"
    ],
    "Circulatory & Vascular Issues": [
        "DVT",
        "Heterotropic Ossification"
    ],
    "Urological & Gastrointestinal Issues": [
        "Neurogenic Bladder",
        "Neurogenic Bowel",
        "Bladder Dysfunction",
        "Bowel Obstruction",
        "UTI",
        "Bladder & Bowel Dysfunction"
    ],
    "Respiratory & Pulmonary Issues": [
        "Pulmonary Issues",
        "Respiratory Dysfunction"
    ],
    "Post-Surgical & Structural Issues": [
        "Spinal Stenosis",
        "Post-Operative Complications (infection, etc.)"
    ],
    "Mental Health & Psychological Impact": [
        "Mental Health Symptoms",
        "Mental Health Issues",
        "Sleep Disorders"
    ],
    "Other Regulatory Issues": [
        "Temperature Regulation Issues"
    ],
    "Sexual & Reproductive Issues": [
        "Sexual Dysfunction"
    ]
}

# COMBINING DX AND SYMPTOM CATEGORIES
sci_sym_cat_dict = defaultdict(list)
for cat, symptoms in sci_cat.items():
    for symp in symptoms:
        sci_sym_cat_dict[cat] = sci_sym_cat_dict[cat] + sci_dx["Associated Complications & Symptoms"][symp]
print(sci_sym_cat_dict.items())

sci_dx.pop("Associated Complications & Symptoms", None)

# CREATE TBI DICTIONARIES
# READ CSV & CREATE ICD DATAFRAME
df_tbi = pd.read_csv("ICD Codes_12.17.24.csv", low_memory=False)
print(df_tbi.head())
symp_index = 0

# TBI DX DICTIONARY
tbi_dx = defaultdict(list)
for df_index, (index, row) in enumerate(df_tbi.dropna(how="all").iterrows()):
    if(row[0].strip() == "Associated Symptoms"):
        symp_index = df_index + 1
        break
    tbi_dx[row[0]] = [code.strip() for code in row[1:].dropna().tolist()]
print(tbi_dx)
print(tbi_dx.keys())
print(symp_index)

# TBI ASSOCIATED SYMPTOMS DICTIONARY
tbi_symp = defaultdict(list)
for index, row in df_tbi.dropna(how="all").iloc[symp_index:].iterrows():
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
# tbi_combined = tbi_dx
# for cat, symptoms in tbi_symp_cat.items():
#     for symp in symptoms:
#         tbi_combined[cat] = tbi_combined[cat] + tbi_symp[symp]
# print(tbi_combined.keys())
#
# tbi_combined_set = {cat: set(codes) for cat, codes in tbi_combined.items()}

tbi_sym_cat_dict = defaultdict(list)
for cat, symptoms in tbi_symp_cat.items():
    for symp in symptoms:
        tbi_sym_cat_dict[cat] = tbi_sym_cat_dict[cat] + tbi_symp[symp]
print(tbi_sym_cat_dict.items())

# CONVERT DICTIONARIES TO HAVE ICD CODE SETS TO OPTIMIZE RUNTIME
icd10_sets = {k: set(v) for k, v in icd10_code.items()}
sci_dx_sets = {cat: {dx: set(codes) for dx, codes in dx_list.items()}
              for cat, dx_list in sci_dx.items()}
sci_sym_sets = {cat: set(codes) for cat, codes in sci_sym_cat_dict.items()}
tbi_dx_sets = {cat: set(codes) for cat, codes in tbi_dx.items()}
tbi_sym_sets = {cat: set(codes) for cat, codes in tbi_sym_cat_dict.items()}

# SET INITIAL COLUMN VALUES TO 0
for category in icd10_code.keys():
    df[category] = 0
for cat, lst in sci_dx_sets.items():
    df[cat] = 0
    for dx in lst:
        df[dx] = 0
for cat in sci_sym_sets.keys():
    df[cat] = 0
for cat in tbi_dx_sets.keys():
    df[cat] = 0
for cat in tbi_sym_sets.keys():
    df[cat] = 0

# CREATE TBI & SCI MARKERS
is_tbi = False
is_sci = False

# ITERATE ROWS IN COMBINED FILE
icd_columns = [col for col in df.columns if col.startswith("I10_DX")]
for index, row in df[icd_columns].dropna(how="all").iterrows():
    for code in row.dropna():
        # ENCODE ELIXHAUSER
        for chapter, lst in icd10_sets.items():
            for icd in lst:
                if icd[-1] == "x" and icd[0:-1] in code:
                    df.at[index, chapter] = 1
                    break
                elif code == icd:
                    df.at[index, chapter] = 1
                    break
        # ENCODE SCI DX
        for category, dx_list in sci_dx_sets.items():
            for dx, codes in dx_list.items():
                if code in codes:
                    df.at[index, category] = 1
                    df.at[index, dx] = 1
                    is_sci = True
        # GO THROUGH SYMPTOMS TO CODE BROADER SCI CATEGORIES
        for category, codes in sci_sym_sets.items():
            if code in codes:
                df.at[index, category] = 1
        # ENCODE TBI DX
        for category, codes in tbi_dx_sets.items():
            if code in codes:
                df.at[index, category] = 1
                is_tbi = True
        # GO THROUGH SYMPTOMS TO CODE BROADER TBI CATEGORIES
        for category, codes in tbi_sym_sets.items():
            if code in codes:
                df.at[index, category] = 1
    # CHANGE TBI & SCI OVERLAP TO BOTH BASED ON MARKERS
    if is_sci and is_tbi and df.at[index, "source"] != "Both":
        df.at[index, "source"] = "Both"
    is_sci = False
    is_tbi = False

# DROP EXTRA COLUMNS
for i in range(1, 41):
    df.drop(f"I10_DX{i}", axis=1, errors='ignore', inplace=True)

# SAVE RESULT TO CSV
df.to_csv("hot_encoded.csv", index=False)

print("Processing complete. Saved to 'hot_encoded.csv'.")