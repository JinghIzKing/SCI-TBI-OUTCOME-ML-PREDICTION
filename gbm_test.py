import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import hashlib

# --- Step 1: Load and verify data consistency ---
iris = load_iris()
X, y = iris.data, iris.target

# Convert to DataFrame and hash to verify consistency
X_df = pd.DataFrame(X, columns=iris.feature_names)
y_df = pd.Series(y)
data_hash = hashlib.md5(pd.util.hash_pandas_object(X_df).to_numpy()).hexdigest()
print(f"Data MD5 Hash: {data_hash}")  # Should match on both platforms!

# --- Step 2: Train/test split with fixed seed ---
X_train, X_test, y_train, y_test = train_test_split(
    X_df, y_df, test_size=0.2, random_state=42, stratify=y_df
)

# --- Step 3: Train LightGBM with deterministic settings ---
params = {
    'objective': 'multiclass',
    'num_class': 3,
    'metric': 'multi_logloss',
    'seed': 42,
    'deterministic': True,  # Critical for reproducibility
    'num_threads': 1,       # Disable parallelism
    'verbose': -1,
}

model = lgb.LGBMClassifier(**params)
model.fit(X_train, y_train)

# --- Step 4: Evaluate and compare ---
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"Accuracy: {acc:.4f}")

# --- Step 5: Output environment details ---
import sys
import sklearn
print("\n=== Environment ===")
print(f"LightGBM: {lgb.__version__}")
print(f"Scikit-learn: {sklearn.__version__}")
print(f"Python: {sys.version}")
print(f"NumPy: {np.__version__}")
print(f"Pandas: {pd.__version__}")

# --- Step 6: Verify first 5 predictions ---
print("\nFirst 5 predictions (should match exactly):")
print(y_pred[:5])