import pandas as pd


data_file = "combined.csv"
icd_file = "Elixhauser_comorbiditiesICD10.csv"


df = pd.read_csv(data_file, dtype=str, low_memory=False)

icd10_code = {}
with open(icd_file, "r", encoding="utf-8") as file:
    for line in file:
        category, *codes = line.strip().split(",")  
        icd10_code[category] = [code.strip().replace(".x", "") for code in codes if code.strip()]

print("Loaded ICD-10 categories:", icd10_code.keys())  

for category in icd10_code.keys():
    df[category] = 0  


icd_columns = [col for col in df.columns if col.startswith("I10_DX")]


for index, row in df[icd_columns].iterrows():
    for code in row.dropna():
        cleaned_code = code.replace(".x", "")  
        for chapter, lst in icd10_code.items():
            if any(cleaned_code == icd for icd in lst):  
                df.at[index, chapter] = 1  

    #"Lumbar and Sacral": ["S34"],
    #"Cervical" : ["S14"],


SCI = {
    "Cervical" : ["S14"],
    "Concussion and edema of cervical spinal cord" : ["S140"],
    "Other and unspecified injuries of cervical spinal cord" : ["S1410"],
    "Central cord syndrome of cervical spinal cord" : ["S1412"],
    "Anterior cord syndrome of cervical spinal cord" : ["S1413"],
    "Brown-Séquard syndrome of cervical spinal cord" : ["S1414"],
    "Other incomplete lesions of cervical spinal cord" : ["S1415"],
    "Injury of nerve root of cervical spine" : ["S142"],
    "Injury of brachial plexus" : ["S143", "S144", "S145", "S148", "S149"],

    "Concussion and edema of lumbar and sacral spinal cord" : ["S3401"],
    "Concussion and edema of sacral spinal cord" : ["S3402"],
    "Other and unspecified injury of lumbar and sacral spinal cord" : ["S3410"], 
    "Complete lesion of lumbar spinal cord" : ["S3411"],
    "Incomplete lesion of lumbar spinal cord": ["S3412"],
    "Other and unspecified injury to sacral spinal cord": ["S3413"],
    "Injury of nerve root of lumbar and sacral spine" : ["S342"],
    "Injuries of Nerves in the Lower Back, Pelvis, and Abdomen" : ["S343", "S344", "S345", "S346", "S348", "S349"],

    "Concussion and edema of thoracic spinal cord" : ["S240"],
    "Other and unspecified injuries of thoracic spinal cord": ["S2410"],
    "Complete lesion of thoracic spinal cord" : ["S2411"],
    "Anterior cord syndrome of thoracic spinal cord": ["S2413"],
    "Brown-Séquard syndrome of thoracic spinal cord" : ["S2414"],
    "Other incomplete lesions of thoracic spinal cord" : ["S2415"],
    "Injury of nerve root of thoracic spine" : ["S242"], 
    "Injury of peripheral nerves of thorax" : ["S243"],
    "Injury of thoracic sympathetic nervous system" : ["S244"],
    "Injury of other specified nerves of thorax" : ["S248"],
    "Injury of unspecified nerve of thorax" : ["S249"],
}

SCI_dic = { "Other and unspecified injuries of cervical spinal cord": ["S141"],
    "Concussion and edema of thoracic spinal cord" : ["S24"],
    "Other and unspecified injuries of thoracic spinal cord" : ["S241"],
    "Concussion and edema of lumbar and sacral spinal cord": ["S241"],
    "Other and unspecified injury of lumbar and sacral spinal cord" : ["S341"]}

SCI_syp = {

    "Neurological Complications": [
        "G8220", "G8221", "G8222",  # Paraplegia
        "G8250", "G8251", "G8252",  # Tetraplegia
        "G950",                    # Spinal Shock
        "I676", "G952",             # Autonomic Dysreflexia
        "N319", "N3281",            # Neurogenic Bladder
        "K5989",                    # Neurogenic Bowel
        "R293", "R292",             # Reflex Issues
        "R200", "R202", "R208", "R209"  # Sensory Loss
    ],
    
    
    "Musculoskeletal & Mobility Issues": [
        "M62830", "M62831", "M62838", "M6250", # Muscle Contractures
        "M625", "G250", "G249", "M159",        # Musculoskeletal Deformity (Spasticity)
        "R531", "R532", "R530",                # Weakness/Fatigue
        "M810", "M8008",                      # Osteoporosis
        "M419", "M4309",                      # Spinal Deformity
        "S12909A", "S12909D", "S22109A", "S22109D", "S32909A", "S32909D", "S32909S",  # Spinal Fracture
        "M899", "M791"                        # Skeletal Issues
    ],
    
    
    "Pain & Discomfort": [
        "G8929",                            # Chronic Pain
        "G639", "G569", "G909"              # Neuropathic Pain
    ],
    
 
    "Skin & Pressure-Related Conditions": [
        "L8910", "L8911", "L8912", "L8913", "L8990",  # Pressure Ulcers
        "L8914", "L8915", "L8990", "L981"            # Skin Conditions and Pressure Issues
    ],
    
 
    "Circulatory & Vascular Issues": [
        "I8290", "I2699",  # DVT (Deep Vein Thrombosis)
        "M870", "M899"     # Heterotopic Ossification
    ],
    

    "Urological & Gastrointestinal Issues": [
        "N393", "N318", "R32", "R1312", "K5900", "K56609", "K589", "K5900", "N159"  # Bladder & Bowel Dysfunction
    ],
    
   
    "Respiratory & Pulmonary Issues": [
        "J989", "R090", "J449", "I279"  # Respiratory Dysfunction (Pulmonary Issues)
    ],
    

    "Post-Surgical & Structural Issues": [
        "M4800", "M4810", "M4830",  # Spinal Stenosis
        "T814", "T8189", "T8410"     # Post-Operative Complications (infection, etc.)
    ],
    

    "Mental Health & Psychological Impact": [
        "F067", "F329", "F419", "F4489",  # Mental Health Issues
        "G4700", "G4710", "R400"         # Sleep Disorders
    ],
    
  
    "Other Regulatory Issues": [
        "T07", "G959" 
    ]
}
  
for category in SCI.keys():
    df[category] = 0 

for index, row in df[icd_columns].iterrows():
    for code in row.dropna():
        for category, codes in SCI.items():
            if any(val in code for val in codes):  # Partial match
                df.at[index, category] = 1 


for category in SCI_syp.keys():
    df[category] = 0 


for index, row in df[icd_columns].iterrows():
    for code in row.dropna():
        for category, codes in SCI_syp.items():
            if code in codes:  # Exact match
                df.at[index, category] = 1
              


for index, row in df[icd_columns].iterrows():
    for code in row.dropna():
        for category, codes in SCI_dic.items():
            if code in codes:  # Exact match
                df.at[index, category] = 1 



df.to_csv("sci_coded.csv", index=False)

print("Processing complete. Saved to 'tbi_coded.csv'.")
