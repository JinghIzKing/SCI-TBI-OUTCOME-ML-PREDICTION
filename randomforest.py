import lightgbm as lgb
import pandas as pd
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score 
import numpy as np
import re 
import matplotlib.pyplot as plt

data_file = "updated_combined.csv"

df = pd.read_csv(data_file, low_memory = False)
for i in range(1, 41):
    df.drop(f"I10_DX{i}", axis=1, errors='ignore', inplace=True)

df = df[df['DISPUNIFORM'] != 'undefined']
#df = df.drop(columns= ['DRG', 'DRGVER', 'DRG_NoPOA', 'HOSP_NIS', 'KEY_NIS', 'APRDRG', 'NIS_STRATUM'])
# df.to_csv("updated_combined.csv", index=False)

df.columns = df.columns.str.replace(r'[^\w]', '_', regex=True)  # Replace spaces and special characters
df.rename(columns={df.columns[22]: "CHF"}, inplace=True)


print(df.columns[22], df.columns[97])

X = df.drop(columns = ['DISPUNIFORM'])
y = df['DISPUNIFORM']
print(y)




params = {
    'objective': 'binary',
    'metric': 'binary_error',
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'feature_fraction': 0.9

}

k = KFold(n_splits = 5, shuffle = True, random_state = 42)
feature_importance_df = pd.DataFrame()
feature_importance_df['Feature'] = X.columns

list = df.columns[22 : 107].tolist()
categorical_columns = ['AMONTH', 'AWEEKEND','DIED', 'DQTR', 'FEMALE', 'HCUP_ED', 'HOSP_DIVISION', 'MDC', 'MDC_NoPOA', 'PAY1', 'PL_NCHS', 'RACE','ZIPINC_QRTL', 'source', 'ELECTIVE', 'TRAN_IN', 'TRAN_OUT']

list =  categorical_columns + list
oof_preds = []
oof_labels = []
fold_scores = []




for fold, (train_index, val_index) in enumerate(k.split(X)):
    print(f"Training on fold {fold+1}...")
    X_train, X_val = X.iloc[train_index], X.iloc[val_index]
    y_train, y_val = y.iloc[train_index], y.iloc[val_index]

    X_train = X_train.copy()
    X_val = X_val.copy()
    y_train = y_train.copy()
    y_val = y_val.copy()

    y_train = y_train.map({'poor': 0, 'good': 1})
    y_val = y_val.map({'poor': 0, 'good': 1})

  

    for col in list:
        X_train.loc[:, col] = X_train[col].astype('category')
        X_val.loc[:, col] = X_val[col].astype('category')

    training_data = lgb.Dataset(X_train, label=y_train, categorical_feature=list)
    validation_data = lgb.Dataset(X_val, label=y_val, categorical_feature=list, reference=training_data)

    bst = lgb.train(params, training_data, num_boost_round=1000, valid_sets=[validation_data] )
    
    y_pred = bst.predict(X_val)
    oof_preds.extend(y_pred)
    oof_labels.extend(y_val)

    fold_accuracy = accuracy_score(y_val, (y_pred > 0.5).astype(int))
    fold_scores.append(fold_accuracy)
    print(f"Fold {fold+1} Accuracy: {fold_accuracy:.4f}")


    feature_importance_df[f'Fold_{fold+1}'] = bst.feature_importance(importance_type='gain')


feature_importance_df["Mean_Importance"] = feature_importance_df.iloc[: , 1:].mean(axis=1)
feature_importance_df = feature_importance_df.sort_values(by="Mean_Importance", ascending=False)

plt.figure(figsize=(12,6))
plt.barh(feature_importance_df['Feature'][:20], feature_importance_df['Mean_Importance'][:20])
plt.gca().invert_yaxis()
plt.xlabel("Feature Importance (Gain)")
plt.ylabel("Feature")
plt.title("Top 20 Important Features (LightGBM)")
plt.show()

print(feature_importance_df[['Feature', 'Mean_Importance']])
overall_accuracy = accuracy_score(oof_labels, (np.array(oof_preds) > 0.5).astype(int))
print(f"\nOverall Accuracy Across {k.get_n_splits()} Folds: {overall_accuracy:.4f}")







