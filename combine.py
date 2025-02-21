import pandas as pd

# List of file paths
files = [
    "patients with TBI and SCI.csv",
    "patients_with_SCI.csv",
    "patients_with_TBI.csv"
]

dfs = []
array = ["TBI", "SCI", "Both"]
for i, f in enumerate(files):
    df = pd.read_csv(f)
    df['source'] = array[i]
    dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)

combined_df.to_csv("combined.csv", index=False)

print(combined_df.head())