# LLM narrative summary (assignment step d)
import pandas as pd
from pipeline.llm_utils import call_gemini_json


def generate_summary(df: pd.DataFrame) -> dict:
    # Compute the hard numbers ourselves - don't ask the LLM to do arithmetic
    total_inr = float(df[df["currency"] == "INR"]["amount"].sum())
    total_usd = float(df[df["currency"] == "USD"]["amount"].sum())

    top = df.groupby("merchant")["amount"].sum().sort_values(ascending=False).head(3)
    top_merchants = [{"merchant": m, "total": float(a)} for m, a in top.items()]

    anomaly_count = int(df["is_anomaly"].sum())

    prompt = (
        "You are a financial analyst writing a short spending report.\n"
        f"Total spend in INR: {total_inr}\n"
        f"Total spend in USD: {total_usd}\n"
        f"Top merchants by total spend: {top_merchants}\n"
        f"Number of anomalous transactions flagged: {anomaly_count}\n\n"
        "Respond with JSON in exactly this shape:\n"
        '{"narrative": "<2-3 sentence spending summary>", "risk_level": "<low, medium, or high>"}'
    )

    try:
        raw = call_gemini_json(prompt)
        narrative = str(raw.get("narrative", ""))
        risk_level = raw.get("risk_level")
        if risk_level not in ("low", "medium", "high"):
            risk_level = "low"
    except Exception:
        narrative = "Narrative summary unavailable due to an AI service error after retries."
        risk_level = "low"

    return {
        "total_spend_inr": total_inr,
        "total_spend_usd": total_usd,
        "top_merchants": top_merchants,
        "anomaly_count": anomaly_count,
        "narrative": narrative,
        "risk_level": risk_level,
    }