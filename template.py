from pathlib import Path


ROOT = Path(__file__).resolve().parent


# ============================================================
# FOLDERS
# ============================================================

DIRECTORIES = [
    "config",

    "01_build_database",
    "01_build_database/raw_data",

    "02_extract_schema",

    "03_golden_dataset",

    "04_run_evaluation",
    "04_run_evaluation/results",

    "scratch",
]


# ============================================================
# FILES
# ============================================================

FILES = [
    # Root files
    "main.py",
    "requirements.txt",
    "README.md",

    # Config
    "config/models.py",

    # Stage 1: Build Database
    "01_build_database/raw_data/matches.csv",
    "01_build_database/raw_data/deliveries.csv",
    "01_build_database/build_database.py",
    "01_build_database/ipl_2021_2024.db",

    # Stage 2: Extract Schema
    "02_extract_schema/extract_schema.py",
    "02_extract_schema/schema.sql",

    # Stage 3: Golden Dataset
    "03_golden_dataset/golden_dataset.csv",
    "03_golden_dataset/hard_questions_source.py",
    "03_golden_dataset/build_golden_hard_csv.py",

    # Stage 4: Evaluation
    "04_run_evaluation/evaluator.py",
    "04_run_evaluation/results/eval_results.csv",

    # Scratch
    "scratch/quick_manual_test.py",
]


def create_structure():
    """Create the LLM SQL evaluation project structure."""

    print("\nCreating llm-sql-eval project structure...\n")

    # Create directories
    for directory in DIRECTORIES:
        path = ROOT / directory
        path.mkdir(parents=True, exist_ok=True)
        print(f"[DIR ] {directory}/")

    # Create files only if they don't already exist
    for file in FILES:
        path = ROOT / file

        if not path.exists():
            path.touch()
            print(f"[FILE] {file}")
        else:
            print(f"[SKIP] {file} already exists")

    print("\n" + "=" * 60)
    print("Project structure created successfully!")
    print("=" * 60)

    print(
        """
llm-sql-eval/
│
├── main.py
├── requirements.txt
├── README.md
│
├── config/
│   └── models.py
│
├── 01_build_database/
│   ├── raw_data/
│   │   ├── matches.csv
│   │   └── deliveries.csv
│   ├── build_database.py
│   └── ipl_2021_2024.db
│
├── 02_extract_schema/
│   ├── extract_schema.py
│   └── schema.sql
│
├── 03_golden_dataset/
│   ├── golden_dataset.csv
│   ├── hard_questions_source.py
│   └── build_golden_hard_csv.py
│
├── 04_run_evaluation/
│   ├── evaluator.py
│   └── results/
│       └── eval_results.csv
│
└── scratch/
    └── quick_manual_test.py
"""
    )

    print("Next step:")
    print("    python template.py")
    print()


if __name__ == "__main__":
    create_structure()