import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import hashlib
import platform

# --- Set all possible random seeds ---
SEED = 42
np.random.seed(SEED)

# --- Generate synthetic data ---
X, y = make_classification(
    n_samples=1000,
    n_features=20,
    n_informative=10,
    random_state=SEED,
    n_clusters_per_class=1  # Simpler patterns
)

# --- Verify data consistency ---
def hash_array(arr):
    return hashlib.md5(arr.tobytes()).hexdigest()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=SEED
)

print(f"Data hashes (should match):")
print(f"X_train: {hash_array(X_train)}")
print(f"y_train: {hash_array(y_train)}")

# --- Deterministic LightGBM setup ---
params = {
    'objective': 'binary',
    'metric': 'auc',
    'seed': SEED,
    'deterministic': True,
    'num_threads': 1,  # Single-threaded
    'feature_fraction': 1.0,  # Disable random feature selection
    'bagging_freq': 0,  # Disable bagging
    'verbosity': -1,
}

# --- Train and evaluate ---
model = lgb.LGBMClassifier(**params)
model.fit(X_train, y_train)

y_pred = model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_pred)

print("\n=== Results ===")
print(f"AUC: {auc:.6f}")  # Higher precision for comparison
print("First 5 predictions:")
print(y_pred[:5].round(6))  # More decimal places

# --- Environment details ---
print("\n=== Environment ===")
print(f"OS: {platform.platform()}")
print(f"LightGBM: {lgb.__version__}")
print(f"NumPy: {np.__version__}")