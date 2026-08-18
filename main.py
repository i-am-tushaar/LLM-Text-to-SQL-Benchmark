"""
main.py - Complete LLM Text-to-SQL evaluation pipeline.
"""

import os
import re
import sys
import time
import sqlite3
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import SystemMessage, HumanMessage

ROOT_DIR = Path(__file__).resolve().parent

DB_PATH = ROOT_DIR / "01_build_database" / "ipl_2021_2024.db"
SCHEMA_PATH = ROOT_DIR / "02_extract_schema" / "schema.sql"
GOLDEN_PATH = ROOT_DIR / "03_golden_dataset" / "golden_dataset.csv"
RESULTS_PATH = ROOT_DIR / "04_run_evaluation" / "results" / "eval_results.csv"

from config.models import MODELS

import sys
sys.path.insert(0, str(ROOT_DIR / "04_run_evaluation"))
from evaluator import evaluate_one

load_dotenv(ROOT_DIR / ".env")
API_KEY = os.getenv("OPENROUTER_API_KEY")


def validate_files():
    files = {
        "Database": DB_PATH,
        "Schema": SCHEMA_PATH,
        "Golden Dataset": GOLDEN_PATH,
    }

    missing = [f"{name}: {path}" for name, path in files.items() if not path.exists()]

    if missing:
        print("\nMissing files:")
        for item in missing:
            print(f"  {item}")
        return False

    return True


def load_schema():
    with open(SCHEMA_PATH, encoding="utf-8") as file:
        return file.read().strip()


def load_golden():
    golden = pd.read_csv(GOLDEN_PATH)

    required = {"id", "difficulty", "question", "sql"}
    missing = required - set(golden.columns)

    if missing:
        raise ValueError(f"Golden Dataset missing columns: {sorted(missing)}")

    return golden


def make_llm(slug):
    return ChatOpenRouter(
        model=slug,
        openrouter_api_key=API_KEY,
        temperature=0,
        max_tokens=800,
    )


def clean_sql(raw):
    if not raw:
        return ""

    text = str(raw).strip()

    fence = re.search(
        r"```(?:sql)?\s*(.*?)```",
        text,
        re.DOTALL | re.IGNORECASE,
    )

    if fence:
        text = fence.group(1).strip()

    text = re.sub(
        r"^\s*sql\s*\n",
        "",
        text,
        flags=re.IGNORECASE,
    )

    match = re.search(r"\b(SELECT|WITH)\b", text, re.IGNORECASE)

    if match:
        text = text[match.start():]

    return text.strip().strip("`").rstrip(";").strip("`").strip()


def generate_sql(question, schema, llm):
    system_msg = (
        "You are a Text-to-SQL generator. "
        "Given a SQLite database schema and a natural-language question, "
        "return a single SQL query that answers the question. "
        "Use SQLite syntax. Return only the SQL query."
    )

    user_msg = f"Schema:\n{schema}\n\nQuestion:\n{question}\n\nSQL:"

    response = llm.invoke([
        SystemMessage(content=system_msg),
        HumanMessage(content=user_msg),
    ])

    return clean_sql(response.content)


def run_sql(conn, sql):
    if not sql:
        return None

    try:
        return pd.read_sql_query(sql, conn)
    except Exception:
        return None


def run_eval():
    schema = load_schema()
    golden = load_golden()
    conn = sqlite3.connect(DB_PATH)

    all_rows = []
    scoreboard = {}

    print("\n" + "=" * 60)
    print("LLM TEXT-TO-SQL BENCHMARK")
    print("=" * 60)
    print(f"Questions: {len(golden)} | Models: {len(MODELS)}")

    for model_name, model_slug in MODELS:

        print(f"\nMODEL: {model_name} ({model_slug})")

        try:
            llm = make_llm(model_slug)
        except Exception as error:
            print(f"INIT-ERROR: {error}")
            continue

        correct = 0
        start_time = time.perf_counter()

        for _, row in golden.iterrows():

            qid = row["id"]
            difficulty = row["difficulty"]
            question = row["question"]
            gold_sql = row["sql"]

            gold_df = run_sql(conn, gold_sql)

            if gold_df is None:
                print(f"#{qid} [{difficulty}] GOLD-SQL-ERROR")
                all_rows.append({
                    "model": model_name,
                    "model_slug": model_slug,
                    "id": qid,
                    "difficulty": difficulty,
                    "question": question,
                    "gold_sql": gold_sql,
                    "generated_sql": "",
                    "correct": False,
                    "reason": "gold_sql_error",
                    "latency_seconds": None,
                })
                continue

            request_start = time.perf_counter()

            try:
                generated_sql = generate_sql(
                    question,
                    schema,
                    llm,
                )
                latency = time.perf_counter() - request_start

            except Exception as error:
                latency = time.perf_counter() - request_start

                print(
                    f"#{qid} [{difficulty}] GEN-ERROR: {error} "
                    f"| latency={latency:.2f}s"
                )

                all_rows.append({
                    "model": model_name,
                    "model_slug": model_slug,
                    "id": qid,
                    "difficulty": difficulty,
                    "question": question,
                    "gold_sql": gold_sql,
                    "generated_sql": "",
                    "correct": False,
                    "reason": "generation_error",
                    "latency_seconds": round(latency, 3),
                })

                continue

            generated_df = run_sql(
                conn,
                generated_sql,
            )

            verdict = evaluate_one(
                gold_df,
                generated_df,
                order_sensitive=False,
            )

            if verdict["correct"]:
                correct += 1
                mark = "PASS"
            else:
                mark = "FAIL"

            print(
                f"#{qid} [{difficulty}] {mark} "
                f"| latency={latency:.2f}s"
            )

            all_rows.append({
                "model": model_name,
                "model_slug": model_slug,
                "id": qid,
                "difficulty": difficulty,
                "question": question,
                "gold_sql": gold_sql,
                "generated_sql": generated_sql,
                "correct": verdict["correct"],
                "reason": verdict["reason"],
                "latency_seconds": round(latency, 3),
            })

        total = len(golden)
        total_latency = time.perf_counter() - start_time
        avg_latency = total_latency / total if total else 0
        score = 100 * correct / total if total else 0

        scoreboard[model_name] = {
            "correct": correct,
            "total": total,
            "score": score,
            "avg_latency": avg_latency,
            "total_latency": total_latency,
        }

        print(
            f"SCORE: {correct}/{total} = {score:.1f}% "
            f"| avg latency={avg_latency:.2f}s "
            f"| total={total_latency:.2f}s"
        )

    conn.close()

    print("\n" + "=" * 60)
    print("FINAL SCOREBOARD")
    print("=" * 60)

    for model_name, result in scoreboard.items():
        print(
            f"{model_name:20s} "
            f"{result['correct']}/{result['total']} "
            f"= {result['score']:.1f}% "
            f"| avg latency={result['avg_latency']:.2f}s"
        )

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    pd.DataFrame(all_rows).to_csv(
        RESULTS_PATH,
        index=False,
    )

    print(f"\nResults saved -> {RESULTS_PATH}")


if __name__ == "__main__":

    if not API_KEY:
        print("ERROR: OPENROUTER_API_KEY not found in .env")
        sys.exit(1)

    if not validate_files():
        sys.exit(1)

    run_eval()