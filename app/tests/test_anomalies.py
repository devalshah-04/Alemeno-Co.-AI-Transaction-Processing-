import pandas as pd
from pipeline.anomalies import detect_anomalies


def test_flags_amount_over_3x_median():
    df = pd.DataFrame({
        "account_id": ["ACC001"] * 4,
        "amount": [100.0, 100.0, 100.0, 1000.0],
        "currency": ["INR"] * 4,
        "merchant": ["Shop"] * 4,
    })
    result = detect_anomalies(df)
    assert result.iloc[3]["is_anomaly"] == True
    assert "median" in result.iloc[3]["anomaly_reason"]
    assert result.iloc[0]["is_anomaly"] == False


def test_flags_usd_on_domestic_only_merchant():
    df = pd.DataFrame({"account_id": ["ACC001"], "amount": [500.0], "currency": ["USD"], "merchant": ["Swiggy"]})
    result = detect_anomalies(df)
    assert result.iloc[0]["is_anomaly"] == True
    assert "domestic" in result.iloc[0]["anomaly_reason"]

def test_no_anomaly_for_normal_transaction():
    df = pd.DataFrame({"account_id": ["ACC001"] * 2, "amount": [100.0, 120.0], "currency": ["INR"] * 2, "merchant": ["Shop"] * 2})
    result = detect_anomalies(df)
    assert not result["is_anomaly"].any()