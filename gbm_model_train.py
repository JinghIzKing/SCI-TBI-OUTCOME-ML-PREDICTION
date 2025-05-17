import pandas as pd
import lightgbm as lgb
import re
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import matplotlib.pylab as plt
import shap
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score

# READ ENCODED DATA
df = pd.read_csv('hot_encoded.csv', encoding="utf-8", low_memory=False)

# FULLY ENCODE CATEGORICAL VARIABLES TO NUMBERS
for col in df.columns:
    if df[col].dtype == "object":
        print(f"Encoding column: {col}")
        df[col] = LabelEncoder().fit_transform(df[col])

# REMOVE UNSUPPORTED SPECIAL CHARACTERS
df.columns = [re.sub(r'[^\w\d_]', '_', col) for col in df.columns]
print(df.columns)

# REMOVE UNDEFINED DATA ENTRIES
df = df[df["DISPUNIFORM"] != 2]

# df.to_csv("gbm_encoded.csv", index=False)

# REWEIGHT DATASET BASED ON AMOUNT OF TBI ONLY, SCI ONLY, AND BOTH
num_tbi = len(df[df["source"] == 2])
num_sci = len(df[df["source"] == 1])
num_both = len(df[df["source"] == 0])
weights = (
    df["source"].map({
        2: 1.0,                 # TBI-only (baseline)
        1: num_tbi/num_sci,     # SCI-only (~8x less)
        0: num_tbi/num_both     # TBI+SCI (~120x less common)
    })
)

# SETTING UP STRATIFIED K-FOLD CROSS VALIDATION WITH 5 FOLDS
print("Starting Stratified K-Fold Cross Validation With 5 Folds")
n_splits = 5
skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
auc_scores = []

# DEFINING FEATURES AND OUTCOME FOR TRAIN/TEST SETS
features = [c for c in df if c not in ["DISPUNIFORM", "KEY_NIS", "TRAN_OUT", "LOS", "DIED"]]
x = df.loc[:, features]
y = df.loc[:, "DISPUNIFORM"]

# UNIVERSAL MODEL PARAMS
params = {
    "objective": "binary",
    "metric": "auc",
    "learning_rate": 0.05,
    "num_leaves": 31,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "lambda_l1": 0.1,
    "lambda_l2": 0.1,
    "verbose": -1,
    "seed": 42
}

# RUNNING STRATIFIED K-FOLD CROSS VALIDATION
for train_index, test_index in skf.split(x, y):
    print("Start of New Fold:")
    x_train, x_test = x.iloc[train_index], x.iloc[test_index]
    y_train, y_test = y[train_index], y[test_index]

    # CREATE TRAIN AND TEST GBM DATASETS
    train_data = lgb.Dataset(x_train, label=y_train, weight=weights.loc[x_train.index])
    test_data = lgb.Dataset(x_test, label=y_test, reference=train_data, weight=weights.loc[x_test.index])

    # TRAIN MODEL ON FOLD
    fold_model = lgb.train(params, train_data, num_boost_round=5000, valid_sets=[test_data],
                           callbacks=[lgb.early_stopping(stopping_rounds=50),])

    # PREDICT TEST SET WITH MODEL
    y_pred = fold_model.predict(x_test)

    # CALCULATE FOLD AUC SCORE AND STORE IN AUC LIST
    auc = roc_auc_score(y_test, y_pred)
    auc_scores.append(auc)
    print(f"Fold AUC: {auc:.4f}")

# CALCULATE AVERAGE ACCURACY ACROSS ALL FOLDS
print("Auc Metrics:", auc_scores)
average_auc = np.mean(auc_scores)
print(f'Average Auc: {average_auc:.4f}')

# FEATURE SELECTION


# CREATE FINAL TRAIN DATA WITH STRATIFIED SAMPLE
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, stratify=y, random_state=42)
print(x_train.shape, x_test.shape, y_train.shape, y_test.shape)

# FINAL MODEL SETUP
train_gbm_dataset = lgb.Dataset(x_train, label=y_train, weight=weights.loc[x_train.index])
test_gbm_dataset = lgb.Dataset(x_test, label=y_test, weight=weights.loc[x_test.index])

# RUN FINAL LIGHTGBM MODEL
init_lgbm_model = lgb.train(params, train_gbm_dataset, valid_sets=[test_gbm_dataset], num_boost_round=10000,
                            callbacks=[lgb.early_stopping(stopping_rounds=50),])

# COMPUTE & VISUALIZE SHAP VALUES FOR FINAL GBM MODEL
shap_gbm_explain = shap.TreeExplainer(init_lgbm_model)
shap_values = shap_gbm_explain.shap_values(x_test)
shap.summary_plot(shap_values, x_test, plot_type="bar")
shap.summary_plot(shap_values, x_test)

# SAVING FINAL SHAP VALUES TO TABLE
shap_df = pd.DataFrame(data={
    'feature': x_test.columns,
    'mean_abs_shap': np.abs(shap_values).mean(axis=0)
}).sort_values(by='mean_abs_shap', ascending=False)

shap_df.to_csv("SHAP_Table3.csv", index=False)

# VISUALIZE FINAL GAIN VALUES FOR DISTRIBUTION OF FEATURE IMPORTANCE
init_lgbm_model.save_model("lightgbm_dispuniform_model_init.txt")
importance = init_lgbm_model.feature_importance(importance_type='gain')
gbm_features = init_lgbm_model.feature_name()
feat_imp_df = pd.DataFrame({
    "feature": gbm_features,
    "importance": importance
}).sort_values(by="importance", ascending=False)
lgb.plot_importance(init_lgbm_model, max_num_features=150, importance_type='gain')
plt.title("Top 150 Important Features")
plt.show()

# SAVING FINAL GAIN TABLE 3
feat_imp_df.to_csv("Gain_Table3.csv", index=False)

# PREDICTING WITH FINAL MODEL
y_train_pred = init_lgbm_model.predict(x_train)
y_test_pred = init_lgbm_model.predict(x_test)

print("AUC Train: {:.4f}\nAUC Test: {:.4f}".format(roc_auc_score(y_train, y_train_pred),
                                                   roc_auc_score(y_test, y_test_pred)))
