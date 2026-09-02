"""
Minimal trainer script (LightGBM + SHAP) that reads labeled trades CSV and fits a binary model.
This is a scaffold – adapt feature columns and label logic to your production dataset.

Run:
  pip install -r requirements.txt
  python train.py --input labeled_trades.csv --out-model model_v{timestamp}.txt
"""

import argparse
import time
import json
import pandas as pd
import lightgbm as lgb
import shap
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score, precision_score

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True, help="CSV with labeled trades. Must include 'label' column.")
parser.add_argument("--out-model", required=False, default=None, help="Path to write model file")
args = parser.parse_args()

print("Loading data:", args.input)
df = pd.read_csv(args.input)

# TODO: Replace with your real feature columns
feature_cols = [c for c in df.columns if c not in ("label", "signal_id", "created_at")]
if "label" not in df.columns:
    raise SystemExit("Input CSV must contain 'label' column (1 success, 0 fail)")

X = df[feature_cols]
y = df["label"]

# Time series split
ts = TimeSeriesSplit(n_splits=3)
best_model = None
best_score = -1
for i, (train_idx, val_idx) in enumerate(ts.split(X)):
    print(f"Fold {i+1} - train {len(train_idx)} val {len(val_idx)}")
    Xtr, Xv = X.iloc[train_idx], X.iloc[val_idx]
    ytr, yv = y.iloc[train_idx], y.iloc[val_idx]

    train_data = lgb.Dataset(Xtr, label=ytr)
    val_data = lgb.Dataset(Xv, label=yv, reference=train_data)

    params = {
        'objective': 'binary',
        'metric': 'auc',
        'verbosity': -1,
        'boosting_type': 'gbdt'
    }

    model = lgb.train(
        params,
        train_data,
        num_boost_round=1000,
        valid_sets=[val_data],
        early_stopping_rounds=50,
        verbose_eval=50
    )

    preds = model.predict(Xv)
    auc = roc_auc_score(yv, preds)
    print(f"Fold {i+1} AUC: {auc:.4f}")
    if auc > best_score:
        best_score = auc
        best_model = model

print(f"Best AUC: {best_score:.4f}")

# Compute SHAP on last validation set
try:
    print("Computing SHAP values (may be slow)")
    explainer = shap.TreeExplainer(best_model)
    shap_values = explainer.shap_values(Xv)
    # Save summary data to JSON for the registry
    mean_abs_shap = dict(zip(Xv.columns, (abs(shap_values).mean(axis=0)).tolist()))
    with open('shap_summary.json', 'w') as f:
        json.dump(mean_abs_shap, f)
    print("Saved shap_summary.json")
except Exception as e:
    print("SHAP computation failed:", e)

# save model
out_path = args.out_model or f"model_{int(time.time())}.txt"
best_model.save_model(out_path)
print("Saved model to", out_path)

# print brief metrics
print("Training finished. Best AUC:", best_score)
