"""
Model filtration benchmark table.

Used to compare candidate LLMs based on:
- Index
- Monthly cost
- Throughput
- Score
"""

MODEL_BENCHMARK = [
    {
        "rank": 1,
        "model": "GPT-5.6 Terra",
        "index": 46.0,
        "price_inr_month": 447300,
        "throughput_cps": 57,
        "score": 0.909,
    },
    {
        "rank": 2,
        "model": "Kimi K3",
        "index": 44.9,
        "price_inr_month": 483084,
        "throughput_cps": 4,
        "score": 0.883,
    },
    {
        "rank": 3,
        "model": "",
        "index": 38.3,
        "price_inr_month": 165501,
        "throughput_cps": 266,
        "score": 0.823,
    },
    {
        "rank": 4,
        "model": "Grok 4.5",
        "index": 40.5,
        "price_inr_month": 250488,
        "throughput_cps": 24,
        "score": 0.817,
    },
    {
        "rank": 5,
        "model": "Claude Sonnet 5",
        "index": 40.4,
        "price_inr_month": 284760,
        "throughput_cps": 15,
        "score": 0.814,
    },
    {
        "rank": 6,
        "model": "GPT-5.6 Luna",
        "index": 39.3,
        "price_inr_month": 178920,
        "throughput_cps": 22,
        "score": 0.798,
    },
    {
        "rank": 7,
        "model": "GLM-5.2",
        "index": 39.0,
        "price_inr_month": 121666,
        "throughput_cps": 9,
        "score": 0.791,
    },
    {
        "rank": 8,
        "model": "Qwen3.7 Max",
        "index": 38.9,
        "price_inr_month": 156555,
        "throughput_cps": 5,
        "score": 0.789,
    },
    {
        "rank": 9,
        "model": "MiniMax M3",
        "index": 35.4,
        "price_inr_month": 42941,
        "throughput_cps": 171,
        "score": 0.761,
    },
    {
        "rank": 10,
        "model": "Gemini 3.6 Flash",
        "index": 32.8,
        "price_inr_month": 241542,
        "throughput_cps": 265,
        "score": 0.736,
    },
]


def get_top_models(n=5):
    """Return top N models based on benchmark score."""
    return sorted(
        MODEL_BENCHMARK,
        key=lambda x: x["score"],
        reverse=True,
    )[:n]


if __name__ == "__main__":
    print("Top 5 Candidate Models:")

    for model in get_top_models(5):
        print(
            f"{model['rank']}. "
            f"{model['model']} | "
            f"Score: {model['score']} | "
            f"Index: {model['index']} | "
            f"Throughput: {model['throughput_cps']} c/s"
        )