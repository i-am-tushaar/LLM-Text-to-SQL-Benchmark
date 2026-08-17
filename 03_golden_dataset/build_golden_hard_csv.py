"""
Build golden_dataset.csv from hard_questions_source.py.

Input:
    hard_questions_source.py

Output:
    golden_dataset.csv

SQL queries are normalized into a single line so that
the complete query is easy to read inside the CSV.
"""

import csv
from pathlib import Path

from hard_questions_source import GOLDEN


# Output CSV location
OUTPUT_FILE = Path(__file__).resolve().parent / "golden_dataset.csv"


def clean_sql(sql):
    """Convert multi-line SQL into a clean single-line query."""
    return " ".join(sql.split())


def build_csv():
    """Convert GOLDEN questions into a CSV file."""

    fieldnames = [
        "id",
        "difficulty",
        "question",
        "sql",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_ALL,
        )

        writer.writeheader()

        for item in GOLDEN:
            writer.writerow(
                {
                    "id": item["id"],
                    "difficulty": item["difficulty"],
                    "question": item["question"].strip(),
                    "sql": clean_sql(item["sql"]),
                }
            )

    print("=" * 60)
    print("Golden dataset created successfully!")
    print("=" * 60)
    print(f"Output file    : {OUTPUT_FILE}")
    print(f"Total questions: {len(GOLDEN)}")
    print("=" * 60)


if __name__ == "__main__":
    build_csv()