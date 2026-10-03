import json
import math
from collections import Counter
from statistics import mean, median, pstdev


def safe_float(value, default=0.0):
    if value is None or value == "":
        return float(default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def default_history():
    return [
        {"account_id": "acct_1042", "timestamp": "2024-08-10 09:14:00", "amount": 32.50, "merchant_city": "Boston", "merchant_country": "US", "merchant": "Café Nero"},
        {"account_id": "acct_1042", "timestamp": "2024-08-11 12:02:00", "amount": 18.99, "merchant_city": "Boston", "merchant_country": "US", "merchant": "Subway"},
        {"account_id": "acct_1042", "timestamp": "2024-08-12 18:45:00", "amount": 64.32, "merchant_city": "Boston", "merchant_country": "US", "merchant": "Whole Foods"},
        {"account_id": "acct_1042", "timestamp": "2024-08-13 08:33:00", "amount": 24.10, "merchant_city": "Boston", "merchant_country": "US", "merchant": "Starbucks"},
        {"account_id": "acct_1042", "timestamp": "2024-08-14 22:10:00", "amount": 75.00, "merchant_city": "Boston", "merchant_country": "US", "merchant": "Movie Theater"},
        {"account_id": "acct_1042", "timestamp": "2024-08-15 17:50:00", "amount": 28.44, "merchant_city": "Boston", "merchant_country": "US", "merchant": "Target"},
        {"account_id": "acct_1042", "timestamp": "2024-08-16 11:25:00", "amount": 22.00, "merchant_city": "Boston", "merchant_country": "US", "merchant": "Pharmacy"},
    ]


def default_chat_history():
    return {
        "acct_1042": [
            {"timestamp": "2024-08-12 07:15", "message": "Customer says they are visiting relatives in Boston this week and will mostly stay local."},
            {"timestamp": "2024-08-14 12:22", "message": "Customer reports travel to London next week but no recent card changes."},
            {"timestamp": "2024-08-16 18:00", "message": "Account owner is a frequent Boston shopper with no unusual activity."},
        ]
    }


def detect_anomalies(flagged_tx, df_history):
    if not isinstance(flagged_tx, dict):
        return ["No transaction data available for baseline comparison."], 0.0, "unknown"

    if not isinstance(df_history, (list, tuple)) or not df_history:
        return ["No historical data available for baseline comparison."], 0.0, "unknown"

    amounts = [
        amount
        for row in df_history
        if isinstance(row, dict)
        for amount in [safe_float(row.get("amount"), float("nan"))]
        if math.isfinite(amount)
    ]

    avg_spend = mean(amounts) if amounts else 0.0
    median_spend = median(amounts) if amounts else 0.0
    std_spend = pstdev(amounts) if len(amounts) > 1 else 0.0

    city_counts = Counter(
        str(row["merchant_city"]).strip()
        for row in df_history
        if isinstance(row, dict) and row.get("merchant_city")
    )

    home_city = min(
        city_counts,
        key=lambda city: (-city_counts[city], city.casefold()),
        default="unknown"
    )

    anomalies = []
    flagged_amount = safe_float(flagged_tx.get("amount"), 0.0)
    threshold = max(3 * median_spend, avg_spend + 2 * std_spend, 1.0)

    if flagged_amount > threshold:
        anomalies.append(
            f"Transaction amount ${flagged_amount:.2f} is significantly larger than the normal spending baseline of ${avg_spend:.2f}."
        )

    txn_city = flagged_tx.get("merchant_city")
    if txn_city and home_city and str(txn_city).lower() != str(home_city).lower():
        anomalies.append(
            f"Transaction location ({txn_city}) deviates from the registered home city location ({home_city})."
        )

    if str(flagged_tx.get("channel", "")).lower() == "online" and flagged_amount > 500:
        anomalies.append(
            "Large online purchase tags high-risk vectors due to value scaling outside structural user profiles."
        )

    if not anomalies:
        anomalies.append("No obvious security anomalies were identified in the tracking pipeline data.")

    return anomalies, avg_spend, home_city


def retrieve_relevant_chats(account_id, chat_database):
    if not isinstance(chat_database, dict):
        return []
    messages = chat_database.get(account_id, [])
    return [item.get("message", "") for item in messages if isinstance(item, dict)]


def generate_llm_prompt(flagged_tx, anomalies_found, baseline_spend, home_city, retrieved_context):
    tx = flagged_tx if isinstance(flagged_tx, dict) else {}
    prompt = {
        "task": "Determine whether this transaction is likely fraudulent and provide a structured JSON verdict.",
        "transaction": {
            "account_id": tx.get("account_id"),
            "timestamp": tx.get("timestamp"),
            "amount": safe_float(tx.get("amount"), 0.0),
            "merchant": tx.get("merchant"),
            "merchant_city": tx.get("merchant_city"),
            "merchant_country": tx.get("merchant_country"),
            "channel": tx.get("channel"),
            "currency": tx.get("currency"),
        },
        "baseline": {
            "average_spend": round(float(baseline_spend), 2),
            "home_city": home_city,
        },
        "anomaly_signals": anomalies_found,
        "retrieved_context": retrieved_context,
        "requirements": {
            "response_format": "JSON",
            "fields": ["risk_score", "verdict", "reasoning", "recommended_action", "confidence"],
        },
    }
    return json.dumps(prompt, ensure_ascii=False, indent=2)


def build_analysis(flagged_tx, history, chat_history):
    anomalies, avg_spend, home_city = detect_anomalies(flagged_tx, history)
    relevant_context = retrieve_relevant_chats(flagged_tx.get("account_id"), chat_history)

    from .ai_service import get_ai_analysis

    prompt = generate_llm_prompt(
        flagged_tx=flagged_tx,
        anomalies_found=anomalies,
        baseline_spend=avg_spend,
        home_city=home_city,
        retrieved_context=relevant_context,
    )

    ai_response = get_ai_analysis(prompt)
    result = {
        "account_id": flagged_tx.get("account_id", ""),
        "transaction": flagged_tx,
        "anomalies": anomalies,
        "average_spend": avg_spend,
        "home_city": home_city,
        "risk_score": int(ai_response.get("risk_score", 0)),
        "verdict": ai_response.get("verdict", "LOW_RISK"),
        "reasoning": ai_response.get("reasoning", anomalies),
        "recommended_action": ai_response.get("recommended_action", "Review transaction manually."),
        "confidence": float(ai_response.get("confidence", 0.0)),
        "retrieved_context": relevant_context,
    }

    result["risk_score"] = max(0, min(100, result["risk_score"]))
    return result
