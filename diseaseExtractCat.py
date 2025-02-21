import pandas as pd

# Load the dataset (replace with your dataset path)
df = pd.read_csv('combined.csv')

# Specify the column range where the ICD codes are stored (e.g., from column 17 to 56)
icd_columns = df.iloc[:, 17:56]

# Create a set to store unique three-character combinations
unique_three_chars = set()

# Iterate over each row and column to extract the first three characters of the ICD codes
for index, row in icd_columns.iterrows():
    for code in row:
        if pd.notna(code):  # Only process valid (non-null) ICD codes
            code_str = str(code)[:3]  # Extract the first three characters
            unique_three_chars.add(code_str.upper())  # Ensure the combination is in uppercase

# Convert the set to a sorted list
unique_three_chars_list = sorted(unique_three_chars)

# Print the unique three-character combinations
print("Unique Three-Character ICD Code Combinations Found:")
for code in unique_three_chars_list:
    print(code)

# Optionally, you can save the unique combinations to a text file for review
with open("unique_three_char_icd_codes.txt", "w") as f:
    for code in unique_three_chars_list:
        f.write(code + "\n")
