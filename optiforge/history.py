import json
from datetime import datetime, timezone
from pathlib import Path

HISTORY_FILE = Path(__file__).resolve().parent.parent / "data" / "comparison_history.json"


def _ensure_file():
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]", encoding="utf-8")


def load_history():
    _ensure_file()
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_run(
    *,
    source_code,
    generated_code,
    source_language,
    target_language,
    model,
    test_input,
    benchmark,
    verification,
    recommendation,
):
    history = load_history()

    run = {
        "run_id": len(history) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_language": source_language,
        "target_language": target_language,
        "model": model,
        "test_input": test_input or "",
        "source_code": source_code or "",
        "generated_code": generated_code or "",
        "verification": {
            "verified": bool(verification and verification.verified),
            "passed_tests": int(verification.passed_tests) if verification else 0,
            "total_tests": int(verification.total_tests) if verification else 0,
            "reason": verification.reason if verification else "",
        },
        "benchmark": None,
        "recommendation": {
            "decision": recommendation.decision if recommendation else "UNKNOWN",
            "reason": recommendation.reason if recommendation else "",
        },
    }

    if benchmark is not None:
        run["benchmark"] = {
            "original_average": benchmark.original_average,
            "generated_average": benchmark.generated_average,
            "speedup": benchmark.speedup,
            "improvement_percent": benchmark.improvement_percent,
            "faster": bool(benchmark.faster),
        }

    history.append(run)
    HISTORY_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return run


def render_history():
    history = load_history()

    if not history:
        return (
            "## 📊 Comparison History\n\n"
            "No optimization runs yet."
        )

    rows = [
        "## 📊 Comparison History",
        "",
        f"**{len(history)} run(s) saved**",
        "",
        "| Run | Model | Source → Target | Verification | Runtime | Speedup | Improvement | Decision |",
        "|---:|---|---|---|---:|---:|---:|---|",
    ]

    for run in reversed(history):
        verification = run["verification"]
        benchmark = run["benchmark"]

        verify_text = (
            f"✅ PASS ({verification['passed_tests']}/{verification['total_tests']})"
            if verification["verified"]
            else f"❌ FAIL ({verification['passed_tests']}/{verification['total_tests']})"
        )

        runtime = (
            f"{benchmark['generated_average']:.6f}s"
            if benchmark
            else "—"
        )
        speedup = (
            f"{benchmark['speedup']:.2f}×"
            if benchmark
            else "—"
        )
        improvement = (
            f"{benchmark['improvement_percent']:.2f}%"
            if benchmark
            else "—"
        )

        rows.append(
            f"| {run['run_id']} | {run['model']} | "
            f"{run['source_language'].upper()} → {run['target_language'].upper()} | "
            f"{verify_text} | {runtime} | {speedup} | {improvement} | "
            f"{run['recommendation']['decision']} |"
        )

    return "\n".join(rows)
