import pandas as pd

# Load the dataset (replace with your dataset path)
df = pd.read_csv('combined.csv')

# Specify the column range where the ICD codes are stored (e.g., from column 17 to 56)
icd_columns = df.iloc[:, 17:56]

# Create a set to store unique ICD codes
unique_codes = set()

# Iterate over each row and column to extract unique ICD codes
for index, row in icd_columns.iterrows():
    for code in row:
        if pd.notna(code):  # Only add valid (non-null) ICD codes
            unique_codes.add(str(code))  # Ensure the code is a string

# Convert the set to a sorted list and print the unique codes
unique_codes_list = sorted(unique_codes)
print("Unique ICD Codes Found:")
for code in unique_codes_list:
    print(code)

# Optionally, you can save the unique codes to a text file for review
with open("unique_icd_codes.txt", "w") as f:
    for code in unique_codes_list:
        f.write(code + "\n")
