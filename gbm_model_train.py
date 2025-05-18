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
fold_gain_df = pd.DataFrame()
i = 1
for train_index, test_index in skf.split(x, y):
    print("Training Fold", i)
    x_train, x_test = x.iloc[train_index], x.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

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

    # STORE FOLD GAIN VALUES
    importance = fold_model.feature_importance(importance_type='gain')
    fold_gbm_features = fold_model.feature_name()
    fold_gain_df['features'] = fold_gbm_features
    fold_gain_df[i] = importance
    print("Fold Feature Order:", fold_gbm_features)
    print("Fold Gain Values", importance)
    i += 1

# CALCULATE AVERAGE ACCURACY ACROSS ALL FOLDS
print("Cross Validation Complete.")
print("Auc Metrics:", auc_scores)
average_auc = np.mean(auc_scores)
print(f'Average Auc: {average_auc:.4f}')

# FEATURE SELECTION
print("Starting Feature Selection:")
fold_gain_df['mean_gain'] = fold_gain_df.drop(columns=['features']).mean(axis=1)
fold_gain_df_sorted = fold_gain_df.sort_values(by='mean_gain', ascending=False)
total_gain = fold_gain_df_sorted['mean_gain'].sum()
fold_gain_df_sorted['cumulative_gain'] = fold_gain_df_sorted['mean_gain'].cumsum() / total_gain
print("Sorted cumsums for all features:", fold_gain_df_sorted)
selected_features = fold_gain_df_sorted[fold_gain_df_sorted['cumulative_gain'] <= 0.95]['features'].tolist()
print("Selected Features:", selected_features)
x = df.loc[:, selected_features]

# CREATE FINAL TRAIN DATA WITH STRATIFIED SAMPLE
print("Starting Final Model Training:")
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, stratify=y, random_state=42)
print(x_train.shape, x_test.shape, y_train.shape, y_test.shape)

# FINAL MODEL SETUP
train_gbm_dataset = lgb.Dataset(x_train, label=y_train, weight=weights.loc[x_train.index])
test_gbm_dataset = lgb.Dataset(x_test, label=y_test, weight=weights.loc[x_test.index])

# RUN FINAL LIGHTGBM MODEL
init_lgbm_model = lgb.train(params, train_gbm_dataset, valid_sets=[test_gbm_dataset], num_boost_round=10000,
                            callbacks=[lgb.early_stopping(stopping_rounds=50),])

# COMPUTE & VISUALIZE SHAP VALUES FOR FINAL GBM MODEL
print("Starting SHAP Calculations:")
shap_gbm_explain = shap.TreeExplainer(init_lgbm_model)
shap_values = shap_gbm_explain.shap_values(x_test)
print("Showing SHAP Plot 1:")
shap.summary_plot(shap_values, x_test, plot_type="bar")
print("Showing SHAP Plot 2:")
shap.summary_plot(shap_values, x_test)

# SAVING FINAL SHAP VALUES TO TABLE
print("Saving SHAP Table:")
shap_df = pd.DataFrame(data={
    'feature': x_test.columns,
    'mean_abs_shap': np.abs(shap_values).mean(axis=0)
}).sort_values(by='mean_abs_shap', ascending=False)

shap_df.to_csv("SHAP_Table3.csv", index=False)

# VISUALIZE FINAL GAIN VALUES FOR DISTRIBUTION OF FEATURE IMPORTANCE
print("Starting Gain Calculations:")
importance = init_lgbm_model.feature_importance(importance_type='gain')
gbm_features = init_lgbm_model.feature_name()
feat_imp_df = pd.DataFrame({
    "feature": gbm_features,
    "importance": importance
}).sort_values(by="importance", ascending=False)
print("Showing Gain Plot 1:")
lgb.plot_importance(init_lgbm_model, max_num_features=150, importance_type='gain')
plt.title("Top 150 Important Features")
plt.show()

# SAVING FINAL GAIN TABLE 3
print("Saving Gain Table:")
feat_imp_df.to_csv("Gain_Table3.csv", index=False)

# PREDICTING WITH FINAL MODEL
y_train_pred = init_lgbm_model.predict(x_train)
y_test_pred = init_lgbm_model.predict(x_test)

print("AUC Train: {:.4f}\nAUC Test: {:.4f}".format(roc_auc_score(y_train, y_train_pred),
                                                   roc_auc_score(y_test, y_test_pred)))

# SAVE FINAL MODEL
print("Saving Final Model:")
init_lgbm_model.save_model("lightgbm_dispuniform_model_init.txt")
print("woohoo :)")
