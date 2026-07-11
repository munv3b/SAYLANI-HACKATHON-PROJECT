# 🤖 AI-Powered Data Analysis Assistant

**Track A – Explorer (Beginner to Intermediate)**
A Python command-line tool that reads any CSV dataset, automatically analyzes it,
answers natural-language questions, generates a meaningful chart, and explains
the findings — with a real Groq API call, and an offline rule-based fallback
so it never breaks during judging.

## 📁 Project Structure

```
project/
├── main.py            # Entry point - runs the full flow
├── analysis.py         # Load CSV, dataset info, statistics
├── visualization.py     # Auto-generates the best chart for the data
├── ai_assistant.py      # Claude API integration + rule-based fallback
├── dataset.csv          # Sample dataset (200 sales records)
├── requirements.txt
├── README.md
└── charts/              # Generated chart is saved here
```

## ⚙️ Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. (Optional but recommended) Set your Groq API key so the AI Q&A
   and explanation use real LLM answers instead of the offline fallback:

   **Windows (PowerShell):**
   ```
   $env:Groq_API_KEY="your-key-here"
   ```
   **Mac/Linux:**
   ```
   export Groq_API_KEY="your-key-here"
   ```

   > If no key is set, or there's no internet, the app automatically
   > switches to a rule-based pandas engine — it still works, it just
   > won't phrase answers in fully natural language.

## ▶️ How to Run

```
python main.py dataset.csv
```

(or simply `python main.py` — it defaults to `dataset.csv` in this folder)

### What happens:
1. Loads the CSV and prints rows, columns, dtypes, missing values.
2. Automatically computes stats (mean, max, min, most frequent category, etc.)
3. Prompts you to type questions one at a time (judges ask 3 fixed questions).
   Type `done` when finished.
4. Generates one clean, labeled bar chart saved to `charts/chart.png`.
5. Prints a short AI-generated explanation of the chart.

### Example Questions (using the sample dataset)
- "Which product generated the highest sales?"
- "What is the average CustomerAge?"
- "Which city has the maximum orders?"
- "Which category appears most frequently?"

## 🧠 How the AI Q&A Works

For every question, the app builds a compact text summary of the dataset
statistics and sends it to Claude, asking for one short, factual answer.
If the API call fails (no key / no internet), it falls back to a
rule-based engine that matches keywords in the question to dataset
columns using pandas `groupby`/`value_counts` — so the demo never crashes
in front of judges.

## 📊 About the Chart

`visualization.py` automatically picks the most meaningful chart for
the dataset: it groups a numeric "total" column (like Sales) by the
best categorical column and produces a labeled, colored bar chart.
If the dataset has no clear numeric total, it falls back to a
frequency chart or histogram — so it works with **any** CSV,
not just this sample one.

## 📝 Notes for Judges / Evaluation

- The sample `dataset.csv` (200 rows) simulates a retail sales dataset:
  Product, Category, City, Price, Quantity, CustomerAge, Sales.
- Swap in any other CSV and the tool adapts automatically — column
  detection is dynamic, not hardcoded to this dataset.
- Every function is short and commented so it's easy to explain live.
