"""
visualization.py
Generates one clean, modern chart from the dataset.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def generate_chart(df, stats, output_path="charts/chart.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    categorical_cols = list(stats["categorical_summary"].keys())
    numeric_cols = list(stats["numeric_summary"].keys())

    # Smart ID filter: Exclude columns ending in 'id' OR where unique values equal row count (IDs/Indexes)
    clean_numeric_cols = []
    for c in numeric_cols:
        if not c.lower().endswith("id") and df[c].nunique() < (0.95 * len(df)):
            clean_numeric_cols.append(c)

    if categorical_cols and clean_numeric_cols:
        cat_col = min(categorical_cols, key=lambda c: stats["categorical_summary"][c]["unique_count"])
        
        priority_keywords = ["sale", "revenue", "amount", "total", "price", "quantity"]
        num_col = clean_numeric_cols[0]
        for kw in priority_keywords:
            match = next((c for c in clean_numeric_cols if kw in c.lower()), None)
            if match:
                num_col = match
                break

        grouped = df.groupby(cat_col)[num_col].sum().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(10, 5.5))
        bars = ax.bar(grouped.index.astype(str), grouped.values, color="#1f77b4", edgecolor="none", alpha=0.85)

        if len(bars) > 0:
            bars[0].set_color("#d62728")

        ax.set_title(f"Total {num_col} by {cat_col}", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel(cat_col, fontsize=11, labelpad=10)
        ax.set_ylabel(f"Total {num_col}", fontsize=11)
        plt.xticks(rotation=25, ha="right")
        
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height:,.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9, fontweight='semibold')

        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()

        top_cat = grouped.idxmax() if not grouped.empty else "N/A"
        pct = round(grouped.max() / grouped.sum() * 100, 1) if grouped.sum() > 0 else 0
        description = (
            f"Total {num_col} across {cat_col}. "
            f"'{top_cat}' leads with {grouped.max():,.2f} ({pct}% of total)."
        )
        return output_path, description

    else:
        fig, ax = plt.subplots(figsize=(9, 5))
        cat_col = categorical_cols[0] if categorical_cols else df.columns[0]
        counts = df[cat_col].value_counts().head(10)
        ax.bar(counts.index.astype(str), counts.values, color="#2ca02c")
        ax.set_title(f"Frequency distribution: {cat_col}", fontsize=13, fontweight="bold")
        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
        return output_path, f"Frequency count of top values in {cat_col}."