"""
main.py
AI-Powered Data Analysis Assistant
Track A - Explorer Challenge

Run:
    python main.py dataset.csv
or just:
    python main.py
(it will use dataset.csv in the same folder by default)
"""

import sys
from analysis import load_dataset, show_basic_info, compute_statistics, print_statistics
from visualization import generate_chart
from ai_assistant import answer_question, explain_chart


def get_csv_path():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return "dataset.csv"


def main():
    print("\n🤖  AI-Powered Data Analysis Assistant")
    print("Track A - Explorer Challenge\n")

    # ---------- Step 1: Load Dataset ----------
    csv_path = get_csv_path()
    try:
        df = load_dataset(csv_path)
    except FileNotFoundError:
        print(f"Error: could not find '{csv_path}'. Please check the file path.")
        return
    except Exception as e:
        print(f"Error while reading the CSV: {e}")
        return

    show_basic_info(df)

    # ---------- Step 2: Analyze Dataset ----------
    stats = compute_statistics(df)
    print_statistics(stats)

    # ---------- Step 3: Answer Natural Language Questions ----------
    print("=" * 55)
    print("ASK QUESTIONS ABOUT THE DATASET")
    print("(Type 'done' when the judges are finished asking)")
    print("=" * 55)

    question_count = 1
    while True:
        question = input(f"\nQ{question_count}: ").strip()
        if question.lower() in ("done", "exit", "quit", ""):
            break
        answer, source = answer_question(question, df, stats)
        print(f"Answer ({source}): {answer}")
        question_count += 1

    # ---------- Step 4: Generate Chart ----------
    print("\nGenerating chart...")
    chart_path, chart_description = generate_chart(df, stats)
    print(f"Chart saved to: {chart_path}")

    # ---------- Step 5: Explain the Result ----------
    explanation = explain_chart(chart_description, stats)
    print("\n" + "=" * 55)
    print("AI EXPLANATION")
    print("=" * 55)
    print(explanation)
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
