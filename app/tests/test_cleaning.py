import pandas as pd
from pipeline.cleaning import normalize_date, clean_dataframe


def test_normalize_date_yyyy_mm_dd():
    assert normalize_date("2024/02/05") == "2024-02-05"


def test_normalize_date_dd_mm_yyyy():
    assert normalize_date("04-09-2024") == "2024-09-04"


def test_normalize_date_unrecognized_format_unchanged():
    assert normalize_date("not-a-date") == "not-a-date"


def test_clean_dataframe_handles_dollar_amount_and_casing():
    df = pd.DataFrame({
        "txn_id": ["TXN1"], "date": ["2024/01/01"], "merchant": ["Amazon"],
        "amount": ["$100.50"], "currency": ["inr"], "status": ["success"],
        "category": [None], "account_id": ["ACC001"], "notes": [None],
    })
    cleaned = clean_dataframe(df)
    assert cleaned.iloc[0]["amount"] == 100.50
    assert cleaned.iloc[0]["currency"] == "INR"
    assert cleaned.iloc[0]["status"] == "SUCCESS"
    assert cleaned.iloc[0]["category"] == "Uncategorised"
    assert cleaned.iloc[0]["date"] == "2024-01-01"


def test_clean_dataframe_removes_exact_duplicates():
    df = pd.DataFrame({
        "txn_id": ["TXN1", "TXN1"], "date": ["2024/01/01", "2024/01/01"],
        "merchant": ["Amazon", "Amazon"], "amount": ["100", "100"],
        "currency": ["INR", "inr"], "status": ["SUCCESS", "success"],
        "category": ["Shopping", "Shopping"], "account_id": ["ACC001", "ACC001"],
        "notes": [None, None],
    })
    cleaned = clean_dataframe(df)
    assert len(cleaned) == 1