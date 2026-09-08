import os
from dotenv import load_dotenv
import gradio as gr

from optiforge.analyzer import analyze_code, analyze_algorithm
from optiforge.transformer import MODEL_OPTIONS
from optiforge.pipeline import optimize


load_dotenv()


LANGUAGES = ["python", "cpp", "java"]


CSS = """
:root {
    --of-orange: #ff8a00;
    --of-orange-soft: #ffad4d;
    --of-bg: #0b0b0b;
    --of-panel: #151515;
    --of-border: #2b2b2b;
}

.gradio-container {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 16px !important;
    background: var(--of-bg) !important;
}

body, .gradio-container, .block, .form, .panel {
    background: var(--of-bg) !important;
}

.block, .form, .panel {
    border-color: var(--of-border) !important;
}

label, .wrap, .prose {
    color: #f2f2f2 !important;
}

input, textarea, select {
    background: var(--of-panel) !important;
    border-color: var(--of-border) !important;
}

button.primary {
    color: #111 !important;
}

button.primary:hover {
    background: var(--of-orange-soft) !important;
    border-color: var(--of-orange-soft) !important;
}

#title {
    text-align: center !important;
    margin: 12px 0 26px 0;
}

#title h1 {
    text-align: center !important;
    margin: 0;
}

#title p {
    text-align: center !important;
    margin: 6px 0 0 0;
    opacity: 0.7;
    font-size: 15px;
}

#optimize {
    max-width: 240px;
    margin: 18px auto;
}

#footer {
    text-align: center;
    opacity: 0.6;
    margin-top: 26px;
}

textarea, .code_editor {
    font-family: Consolas, "Courier New", monospace !important;
}

button.primary {
    background: var(--of-orange) !important;
    border-color: var(--of-orange) !important;
}

.section {
    margin-top: 18px;
}
"""


DEFAULT_SOURCE = """n = int(input())

total = 0
for i in range(1, n + 1):
    total += i

print(total)
"""

DEFAULT_INPUT = "1000000\n"
# Keeps comparison results during the current app session.
# Results are grouped by source language and retained per target language.
COMPARISON_HISTORY = {}


def _md(text: str) -> str:
    return text.replace("`", "\\`")


def render_algorithm(analysis) -> str:
    return f"""### 🧠 Algorithm Analysis

| Property | Result |
|---|---|
| Algorithm | {analysis.algorithm} |
| Approach | {analysis.approach} |
| Time Complexity | {analysis.time_complexity} |
| Space Complexity | {analysis.space_complexity} |
| Optimization Opportunity | {analysis.optimization_opportunity} |
"""


def render_comparison(
    source_language,
    target_language,
    benchmark,
    verification,
    recommendation,
):
    source_key = source_language.lower()
    target_key = target_language.lower()

    if source_key not in COMPARISON_HISTORY:
        COMPARISON_HISTORY[source_key] = {}

    # Store/update the result for this target language.
    COMPARISON_HISTORY[source_key][target_key] = {
        "benchmark": benchmark,
        "verification": verification,
        "recommendation": recommendation,
    }

    rows = []

    # Current source language is always the baseline.
    source_runtime = benchmark.original_average if benchmark is not None else None

    rows.append(
        f"| {source_language.upper()} (Baseline) | "
        f"{source_runtime:.6f} | "
        f"1.00× | "
        f"0.00% | "
        f"PASS | "
        f"Baseline |"
        if source_runtime is not None
        else
        f"| {source_language.upper()} (Baseline) | — | 1.00× | 0.00% | — | Baseline |"
    )

    # Show every target language previously tested.
    for language, data in COMPARISON_HISTORY[source_key].items():
        b = data["benchmark"]
        v = data["verification"]

        if b is None:
            correctness = "PASS" if v and v.verified else "FAIL"
            status = "Verified" if v and v.verified else "Verification failed"

            rows.append(
                f"| {language.upper()} | — | — | — | "
                f"{correctness} | {status} |"
            )
            continue

        correctness = "PASS" if v and v.verified else "FAIL"

        if language == source_key:
            status = "Optimized"
        elif b.faster:
            status = "Faster"
        else:
            status = "Slower"

        rows.append(
            f"| {language.upper()} | "
            f"{b.generated_average:.6f} | "
            f"{b.speedup:.2f}× | "
            f"{b.improvement_percent:.2f}% | "
            f"{correctness} | "
            f"{status} |"
        )

    return (
        "### 🌍 Language Comparison\n\n"
        "| Language | Runtime (s) | Speedup | Improvement | "
        "Correctness | Status |\n"
        "|---|---:|---:|---:|---|---|\n"
        + "\n".join(rows)
    )


def render_verification(result) -> str:
    if result is None:
        return "### 🧪 Verification\n\nNot reached."
    status = "✅ VERIFIED" if result.verified else "❌ NOT VERIFIED"
    return (
        "### 🧪 Verification\n\n"
        f"**{status}** — {result.passed_tests}/{result.total_tests} test case(s) passed.\n\n"
        f"{result.reason}"
    )


def render_performance(benchmark) -> str:
    if benchmark is None:
        return "### ⚡ Performance\n\nBenchmark was not reached."
    return f"""### ⚡ Performance

| Metric | Original | Generated |
|---|---:|---:|
| Average | {benchmark.original_average:.6f}s | {benchmark.generated_average:.6f}s |
| Median | {benchmark.original_median:.6f}s | {benchmark.generated_median:.6f}s |
| Best | {benchmark.original_best:.6f}s | {benchmark.generated_best:.6f}s |
| Worst | {benchmark.original_worst:.6f}s | {benchmark.generated_worst:.6f}s |

**Speedup:** {benchmark.speedup:.2f}×  
**Improvement:** {benchmark.improvement_percent:.2f}%  
**Result:** {"🏆 Generated implementation is faster." if benchmark.faster else "⚠️ Generated implementation is not faster."}
"""


def render_recommendation(result) -> str:
    r = result["recommendation"]
    candidate = r.recommended_candidate

    if candidate is None:
        return f"""### 🏆 OptiForge Recommendation

**Decision:** {r.decision}

{r.reason}
"""

    b = candidate.benchmark
    return f"""### 🏆 OptiForge Recommendation

**Decision:** `{r.decision}`  
**Candidate:** `{candidate.candidate_id}`  
**Model:** `{candidate.model}`  
**Language:** `{candidate.language}`  

**Reason:** {r.reason}

**Measured speedup:** {b.speedup:.2f}×  
**Measured improvement:** {b.improvement_percent:.2f}%

{chr(10).join("- " + x for x in r.strengths)}

{chr(10).join("- ⚠️ " + x for x in r.warnings)}
"""


def optimize_ui(source_code, source_language, target_language, model_name, test_input):
    try:
        if not source_code or not source_code.strip():
            raise ValueError("Enter source code first.")

        if source_language not in LANGUAGES or target_language not in LANGUAGES:
            raise ValueError("Choose valid source and target languages.")

        result = optimize(
            source_code=source_code,
            source_language=source_language,
            target_language=target_language,
            model_display_name=model_name,
            test_input=test_input or "",
        )

        candidate = result["candidate"]
        generated = candidate.source_code if candidate.compiled else ""

        return (
            generated,
            render_comparison(
                source_language,
                target_language,
                result["benchmark"],
                result["verification"],
                result["recommendation"],
            ),
            render_algorithm(result["algorithm"]),
            render_verification(result["verification"]),
            render_performance(result["benchmark"]),
            render_recommendation(result),
            "",
        )

    except Exception as exc:
        return (
            "",
            "### 🌍 Language Comparison\n\nOptimization did not complete.",
            "### 🧠 Algorithm Analysis\n\nUnavailable.",
            "### 🧪 Verification\n\nUnavailable.",
            "### ⚡ Performance\n\nUnavailable.",
            "### 🏆 OptiForge Recommendation\n\n**REJECT** — The operation could not be completed.",
            f"❌ {type(exc).__name__}: {exc}",
        )


with gr.Blocks(title="OptiForge.Ai", css=CSS, theme=gr.themes.Base()) as app:
    gr.Markdown(
        """
        <div id="title">
            <h1> ⚡OptiForge.Ai</h1>
            <p>AI-powered code transformation, verification & performance optimization.</p>
        </div>
        """
    )

    with gr.Row(equal_height=True):
        with gr.Column(scale=1, min_width=0):
            source_code = gr.Code(
                value=DEFAULT_SOURCE,
                language="python",
                label="SOURCE CODE",
                lines=22,
                container=True,
            )

        with gr.Column(scale=1, min_width=0):
            generated_code_box = gr.Code(
                label="GENERATED CODE",
                lines=22,
                interactive=False,
                container=True,
            )

    with gr.Row():
        source_language = gr.Dropdown(
            choices=LANGUAGES,
            value="python",
            label="Source Language",
        )
        target_language = gr.Dropdown(
            choices=LANGUAGES,
            value="cpp",
            label="Target Language",
        )
        model_name = gr.Dropdown(
            choices=list(MODEL_OPTIONS.keys()),
            value="Qwen3 Coder 30B (OpenRouter)",
            label="Model",
        )

    test_input = gr.Textbox(
        value=DEFAULT_INPUT,
        label="Test Input",
        lines=3,
        placeholder="Provide deterministic stdin when your program uses input().",
    )

    optimize_button = gr.Button(
        "Optimize Code",
        variant="primary",
        elem_id="optimize",
    )

    gr.Markdown("## Results")

    comparison_result = gr.Markdown(
        "Run an optimization to see the measured comparison."
    )
    algorithm_result = gr.Markdown(
        "Algorithm analysis will appear here."
    )
    verification_result = gr.Markdown(
        "Verification results will appear here."
    )
    performance_result = gr.Markdown(
        "Benchmark results will appear here."
    )
    recommendation_result = gr.Markdown(
        "Recommendation will appear here."
    )
    error_result = gr.Markdown(visible=False)

    gr.Markdown(
        "<div id='footer'>Built with Gradio</div>"
    )

    optimize_button.click(
        fn=optimize_ui,
        inputs=[
            source_code,
            source_language,
            target_language,
            model_name,
            test_input,
        ],
        outputs=[
            generated_code_box,
            comparison_result,
            algorithm_result,
            verification_result,
            performance_result,
            recommendation_result,
            error_result,
        ],
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app.launch(
        server_name="0.0.0.0",
        server_port=port
    )
    
    
