import pandas as pd
from collections import defaultdict

data_file = "combined.csv"
icd_file = "Elixhauser_comorbiditiesICD10.csv"

df = pd.read_csv(data_file, encoding="utf-8", low_memory=False)

icd10_code = {}
with open(icd_file, "r", encoding="utf-8") as file:
    for line in file:
        category, *codes = line.strip().split(",")
        icd10_code[category] = [code.strip().replace(".", "") for code in codes if code.strip()]

print("Loaded ICD-10 categories:", icd10_code.keys())
print("Values", icd10_code.values())
print("Yay")


print("Read Elixhauser")

# READ CSV & CREATE ICD DATAFRAME
df_sci = pd.read_csv("ICD Codes_12.17.24_SCI.csv", encoding="utf-8", low_memory=False)
print(df.head())
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

# HOT CODING
# SET INITIAL COLUMN VALUES TO 0
for category in icd10_code.keys():
    df[category] = 0
for cat, lst in sci_dx.items():
    df[cat] = 0
    for dx in lst:
        df[dx] = 0
for cat in sci_sym_cat_dict.keys():
    df[cat] = 0

# GO THROUGH ELIXHAUSER COMORBIDITIES AND CODE
icd_columns = [col for col in df.columns if col.startswith("I10_DX")]

for index, row in df[icd_columns].dropna(how="all").iterrows():
    for code in row.dropna():
        for chapter, lst in icd10_code.items():
            for icd in lst:
                if icd[-1] == "x" and icd[0:-1] in code:
                    df.at[index, chapter] = 1
                    break
                elif code == icd:
                    df.at[index, chapter] = 1
                    break

# GO THROUGH DX DICT TO CODE CATEGORIES AND SPECIFIC DISEASE
        for category, dx_list in sci_dx.items():
            for dx, codes in dx_list.items():
                if code in codes:
                    df.at[index, category] = 1
                    df.at[index, dx] = 1

# GO THROUGH SYMPTOMS TO CODE BROADER CATEGORIES
        for category, codes in sci_sym_cat_dict.items():
            if code in codes:
                df.at[index, category] = 1

df.to_csv("sci_coded.csv", index=False)

print("Processing complete. Saved to 'sci_coded.csv'.")