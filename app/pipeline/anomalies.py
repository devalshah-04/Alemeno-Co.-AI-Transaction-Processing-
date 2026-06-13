# Anomaly detection rules (assignment step b)
import pandas as pd

# Merchants that should only ever be paid in INR
DOMESTIC_ONLY_MERCHANTS = {"Swiggy", "Ola", "IRCTC"}


def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Default: nothing is flagged yet
    df["is_anomaly"] = False
    df["anomaly_reason"] = None

    # Rule 1: amount > 3x the median amount for that account
    median_by_account = df.groupby("account_id")["amount"].median()

    for idx, row in df.iterrows():
        account_median = median_by_account[row["account_id"]]
        if account_median > 0 and row["amount"] > 3 * account_median:
            df.at[idx, "is_anomaly"] = True
            df.at[idx, "anomaly_reason"] = "amount exceeds 3x account median"

    # Rule 2: USD currency but merchant is domestic-only
    for idx, row in df.iterrows():
        if row["currency"] == "USD" and row["merchant"] in DOMESTIC_ONLY_MERCHANTS:
            if df.at[idx, "is_anomaly"]:
                df.at[idx, "anomaly_reason"] += "; USD currency for domestic-only merchant"
            else:
                df.at[idx, "is_anomaly"] = True
                df.at[idx, "anomaly_reason"] = "USD currency for domestic-only merchant"

    return df