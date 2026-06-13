# LLM-based categorization for transactions with category = "Uncategorised" (assignment step c)
import json
from typing import Literal

import pandas as pd
from pydantic import BaseModel, ValidationError

from pipeline.llm_utils import call_gemini_json

ALLOWED_CATEGORIES = [
    "Food", "Shopping", "Travel", "Transport",
    "Utilities", "Cash Withdrawal", "Entertainment", "Other",
]


class CategoryAssignment(BaseModel):
    row_index: int
    category: Literal[
        "Food", "Shopping", "Travel", "Transport",
        "Utilities", "Cash Withdrawal", "Entertainment", "Other",
    ]


def categorize_transactions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["llm_category"] = None
    df["llm_failed"] = False

    to_categorize = df[df["category"] == "Uncategorised"]
    if to_categorize.empty:
        return df

    rows_for_prompt = []
    for idx, row in to_categorize.iterrows():
        rows_for_prompt.append({
            "row_index": int(idx),
            "merchant": str(row["merchant"]),
            "amount": float(row["amount"]),
            "currency": str(row["currency"]),
            "notes": str(row["notes"]) if pd.notna(row["notes"]) else "",
        })

    prompt = (
        "You are categorizing financial transactions for a spending report.\n"
        f"Allowed categories (use EXACTLY one of these strings): {ALLOWED_CATEGORIES}\n"
        "For each transaction, pick the single most appropriate category based on "
        "the merchant name, amount, and notes.\n"
        "Respond with JSON in exactly this shape:\n"
        '{"assignments": [{"row_index": <int>, "category": "<one of the allowed categories>"}, ...]}\n\n'
        f"Transactions:\n{json.dumps(rows_for_prompt)}"
    )

    try:
        raw = call_gemini_json(prompt)
        assignments = raw.get("assignments", [])
    except Exception:
        for idx in to_categorize.index:
            df.at[idx, "llm_failed"] = True
            df.at[idx, "llm_category"] = "Other"
        return df

    category_by_index = {}
    for item in assignments:
        try:
            valid = CategoryAssignment.model_validate(item)
            category_by_index[valid.row_index] = valid.category
        except ValidationError:
            continue

    for idx in to_categorize.index:
        df.at[idx, "llm_category"] = category_by_index.get(idx, "Other")

    return df