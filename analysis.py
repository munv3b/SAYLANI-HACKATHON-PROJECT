"""
analysis.py
Handles: loading the CSV, showing basic dataset info, and computing
useful statistics (Step 1 & Step 2 of the challenge).
"""

import pandas as pd


def load_dataset(path):
    """Reads the CSV file into a pandas DataFrame."""
    df = pd.read_csv(path)
    return df


def show_basic_info(df):
    """Prints number of rows, columns, column names, dtypes, missing values."""
    print("\n" + "=" * 55)
    print("DATASET SUMMARY")
    print("=" * 55)
    print(f"Rows           : {df.shape[0]}")
    print(f"Columns        : {df.shape[1]}")
    print(f"Column Names   : {list(df.columns)}")
    print("\nData Types:")
    print(df.dtypes)
    print("\nMissing Values (per column):")
    print(df.isnull().sum())
    print("=" * 55 + "\n")


def compute_statistics(df):
    """
    Automatically computes useful statistics for both numeric
    and categorical columns. Returns a dictionary summary that is
    later used for Q&A and for the AI explanation.
    """
    stats = {}
    stats["total_records"] = len(df)

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    stats["numeric_summary"] = {}
    for col in numeric_cols:
        stats["numeric_summary"][col] = {
            "mean": round(df[col].mean(), 2),
            "max": df[col].max(),
            "min": df[col].min(),
            "sum": round(df[col].sum(), 2),
        }

    stats["categorical_summary"] = {}
    for col in categorical_cols:
        counts = df[col].value_counts()
        stats["categorical_summary"][col] = {
            "most_frequent": counts.idxmax(),
            "most_frequent_count": int(counts.max()),
            "unique_count": df[col].nunique(),
            "top_5": counts.head(5).to_dict(),
        }

    return stats


def print_statistics(stats):
    print("=" * 55)
    print("AUTOMATIC ANALYSIS")
    print("=" * 55)
    print(f"Total Records: {stats['total_records']}\n")

    print("Numeric Columns:")
    for col, s in stats["numeric_summary"].items():
        print(f"  {col}: mean={s['mean']}, max={s['max']}, min={s['min']}, sum={s['sum']}")

    print("\nCategorical Columns:")
    for col, s in stats["categorical_summary"].items():
        print(f"  {col}: most frequent = '{s['most_frequent']}' ({s['most_frequent_count']} times), "
              f"unique values = {s['unique_count']}")
    print("=" * 55 + "\n")
