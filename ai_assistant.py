"""
ai_assistant.py
Handles the AI integration part of the challenge (Step 3 & Step 5).

- Uses the Groq API (Llama 3.3) if an API key is available.
- If no API key / no internet, it automatically falls back to a
  rule-based pandas engine so the project NEVER crashes during judging.
"""

import os
import json
import urllib.request
import urllib.error

# Groq ka URL aur Model settings
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"


def _call_groq(prompt, max_tokens=300):
    """Low level call to the Groq API."""
    api_key = os.environ.get("GROQ_API_KEY") or "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"
    api_key = api_key.strip()
    
    if not api_key:
        return None

    payload = {
        "model": GROQ_MODEL,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }

    # Added User-Agent to bypass 403 Forbidden anti-bot checks
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Application/1.0"
    }

    req = urllib.request.Request(
        GROQ_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choices = data.get("choices", [])
            if choices:
                return choices[0]["message"]["content"].strip()
            return None
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, Exception) as e:
        print(f"[Info] Groq API error: {e}, using rule-based fallback.")
        return None


def _dataset_context(df, stats):
    """Builds a richer text summary including a sample preview of raw records."""
    lines = [f"Dataset has {stats['total_records']} rows and columns: {list(df.columns)}."]
    
    # Send a small row sample so the LLM understands formatting and structure
    sample_preview = df.head(3).to_dict(orient="records")
    lines.append(f"Sample data records: {json.dumps(sample_preview)}")
    
    for col, s in stats["numeric_summary"].items():
        lines.append(f"{col}: mean={s['mean']}, max={s['max']}, min={s['min']}, sum={s['sum']}")
    for col, s in stats["categorical_summary"].items():
        lines.append(f"{col}: most frequent value = '{s['most_frequent']}' "
                     f"({s['most_frequent_count']} times), top values = {s['top_5']}")
    return "\n".join(lines)


def answer_question(question, df, stats):
    context = _dataset_context(df, stats)
    prompt = (
        "You are a data analysis assistant. Using ONLY the dataset summary below, "
        "answer the user's question in ONE short, clear sentence with the exact figure/name.\n\n"
        f"Dataset summary:\n{context}\n\nQuestion: {question}\nAnswer:"
    )
    ai_answer = _call_groq(prompt, max_tokens=120)
    if ai_answer:
        return ai_answer, "Groq API (Llama 3.3)"

    return _rule_based_answer(question, df, stats), "Rule-based (offline)"


def _rule_based_answer(question, df, stats):
    """
    Keyword-matching fallback engine using pandas.
    Understands common synonyms and plural forms for column names.
    """
    q = question.lower()
    numeric_cols = list(stats["numeric_summary"].keys())
    categorical_cols = list(stats["categorical_summary"].keys())

    # Included plurals (e.g., categories, products, cities, items)
    numeric_synonym_groups = [
        ["sales", "revenue", "amount", "total", "sum"],
        ["price", "cost"],
        ["age"],
        ["quantity", "qty", "units"],
    ]

    categorical_synonym_groups = [
        ["city", "cities", "location", "region"],
        ["product", "products", "item", "items"],
        ["category", "categories", "type", "types"],
    ]

    def find_column(cols, synonym_groups, exclude_ids=False):
        search_cols = [c for c in cols if not (exclude_ids and c.lower().endswith("id"))]
        for col in search_cols:
            if col.lower() in q:
                return col
        for group in synonym_groups:
            if any(word in q for word in group):
                for col in search_cols:
                    if any(word in col.lower() or col.lower() in word for word in group):
                        return col
        return None

    target_cat_col = find_column(categorical_cols, categorical_synonym_groups)
    target_num_col = find_column(numeric_cols, numeric_synonym_groups, exclude_ids=True)

    # 1. Overall Total / Sum questions (e.g., "total sales amount")
    if any(w in q for w in ["total", "sum", "overall"]) and target_num_col and not any(w in q for w in ["highest", "maximum", "max", "average", "mean"]):
        val = stats["numeric_summary"][target_num_col]["sum"]
        return f"The total {target_num_col} is {val:,.2f}."

    # 2. Average / Mean questions
    if any(w in q for w in ["average", "mean", "typical"]) and target_num_col:
        val = stats["numeric_summary"][target_num_col]["mean"]
        return f"The average {target_num_col} is {val:,.2f}."

    # 3. Maximum / Highest value
    if any(w in q for w in ["highest", "maximum", "max"]) and target_num_col and not target_cat_col:
        val = stats["numeric_summary"][target_num_col]["max"]
        return f"The maximum {target_num_col} is {val:,.2f}."

    # 4. Minimum / Lowest value
    if any(w in q for w in ["minimum", "lowest", "min"]) and target_num_col and not target_cat_col:
        val = stats["numeric_summary"][target_num_col]["min"]
        return f"The minimum {target_num_col} is {val:,.2f}."

    # 5. Grouped Highest (e.g. "highest sales by category")
    if any(w in q for w in ["highest", "maximum", "most", "top"]) and target_cat_col:
        if target_num_col:
            grouped = df.groupby(target_cat_col)[target_num_col].sum()
            top = grouped.idxmax()
            return f"'{top}' has the highest total {target_num_col} ({grouped.max():,.2f})."
        else:
            top = stats["categorical_summary"][target_cat_col]["most_frequent"]
            count = stats["categorical_summary"][target_cat_col]["most_frequent_count"]
            return f"'{top}' appears most frequently in {target_cat_col} ({count} times)."

    # 6. Frequency count
    if any(w in q for w in ["frequent", "appears most", "orders", "count"]) and target_cat_col:
        top = stats["categorical_summary"][target_cat_col]["most_frequent"]
        count = stats["categorical_summary"][target_cat_col]["most_frequent_count"]
        return f"'{top}' appears most frequently in {target_cat_col} ({count} times)."

    # 7. Total rows count
    if any(w in q for w in ["how many rows", "how many records", "total records", "total rows"]):
        return f"The dataset has {stats['total_records']} total records."

    return ("I couldn't map this question to a specific column automatically. "
            "Try mentioning the column name directly (e.g. 'average CustomerAge', "
            "'highest Sales by Product').")


def explain_chart(chart_description, stats):
    """Generates a short natural-language explanation of the chart (Step 5)."""
    prompt = (
        "You are a data analyst. Write ONE short, simple sentence (like for a non-technical audience) "
        f"explaining this chart finding: {chart_description}. "
        "Be specific and mention the key number or percentage if possible."
    )
    ai_text = _call_groq(prompt, max_tokens=100)
    if ai_text:
        return ai_text

    return chart_description  # fallback: use the pre-computed description as-is