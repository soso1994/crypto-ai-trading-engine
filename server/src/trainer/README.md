Trainer README

This directory contains a minimal trainer scaffold used by the retrain pipeline.

1) Prepare a labeled CSV (labeled_trades.csv) with at least the following columns:
   - label (1 for successful trade, 0 for failed)
   - feature columns used for training (numeric)
   - optional: signal_id, created_at

2) Install dependencies (recommended in a virtualenv):
   pip install -r requirements.txt

3) Run training:
   python train.py --input labeled_trades.csv --out-model model_v1.txt

The script produces a LightGBM model file and shap_summary.json with mean absolute SHAP values for feature explainability.

Adapt feature columns and label logic before running in production.
