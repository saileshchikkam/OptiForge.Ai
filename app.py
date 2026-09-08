import os
from dotenv import load_dotenv
import gradio as gr

from optiforge.analyzer import analyze_code, analyze_algorithm
from optiforge.transformer import MODEL_OPTIONS
from optiforge.pipeline import optimize
from optiforge.history import save_run, render_history


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
    background: var(--of-orange) !important;
    border-color: var(--of-orange) !important;
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

.section {
    margin-top: 18px;
}

/* Results use the complete horizontal page width. */
#full_width_result {
    width: 100% !important;
    max-width: none !important;
    margin: 0 !important;
    padding: 0 !important;
}

#full_width_result .prose,
#history,
#algorithm_analysis {
    width: 100% !important;
    max-width: none !important;
}

/* Keep Markdown tables stretched across the result area. */
#full_width_result table {
    width: 100% !important;
    max-width: none !important;
}

/* Three equal result cards under Algorithm Analysis. */
#result_grid {
    width: 100% !important;
    max-width: none !important;
    gap: 16px !important;
    margin-top: 16px !important;
}

#result_card {
    min-width: 0 !important;
    flex: 1 1 0 !important;
    width: 0 !important;
    max-width: none !important;
}

#result_card .prose {
    width: 100% !important;
    max-width: none !important;
}

#result_card table {
    width: 100% !important;
    max-width: none !important;
}

#history {
    margin-top: 28px;
    margin-bottom: 20px;
}

/* Dark mode only. Light mode remains Gradio Default. */
html:not(.of-light) .gradio-container {
    background: var(--of-bg) !important;
}

html:not(.of-light) body,
html:not(.of-light) .gradio-container,
html:not(.of-light) .block,
html:not(.of-light) .form,
html:not(.of-light) .panel {
    background: var(--of-bg) !important;
}

html:not(.of-light) label,
html:not(.of-light) .wrap,
html:not(.of-light) .prose,
html:not(.of-light) h1,
html:not(.of-light) h2,
html:not(.of-light) h3,
html:not(.of-light) h4,
html:not(.of-light) p,
html:not(.of-light) td,
html:not(.of-light) th {
    color: #f2f2f2 !important;
}

html:not(.of-light) input,
html:not(.of-light) textarea,
html:not(.of-light) select {
    background: var(--of-panel) !important;
    color: #f2f2f2 !important;
    border-color: var(--of-border) !important;
}

html:not(.of-light) table,
html:not(.of-light) th,
html:not(.of-light) td {
    border-color: #3a3a3a !important;
}

html:not(.of-light) #result_card {
    background: var(--of-bg) !important;
}
"""



DEFAULT_SOURCE = """
def main():
    n = int(input())
    values = list(map(int, input().split()))

    total = 0
    minimum = values[0]
    maximum = values[0]
    even_count = 0

    longest_increasing_run = 1
    current_run = 1

    for i in range(n):
        value = values[i]

        total += value

        if value < minimum:
            minimum = value

        if value > maximum:
            maximum = value

        if value % 2 == 0:
            even_count += 1

        if i > 0:
            if values[i] > values[i - 1]:
                current_run += 1
            else:
                current_run = 1

            if current_run > longest_increasing_run:
                longest_increasing_run = current_run

    print("Sum:", total)
    print("Minimum:", minimum)
    print("Maximum:", maximum)
    print("Even count:", even_count)
    print("Longest increasing run:", longest_increasing_run)


if __name__ == "__main__":
    main()
"""

DEFAULT_INPUT = "5\n1 2 3 4 5\n"

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
    source_runtime = benchmark.original_average if benchmark is not None else None

    rows = [
        (
            f"| {source_language.upper()} (Baseline) | "
            f"{source_runtime:.6f} | 1.00× | 0.00% | PASS | Baseline |"
            if source_runtime is not None
            else
            f"| {source_language.upper()} (Baseline) | — | 1.00× | 0.00% | — | Baseline |"
        )
    ]

    if benchmark is None:
        correctness = "PASS" if verification and verification.verified else "FAIL"
        status = "Verified" if verification and verification.verified else "Verification failed"
        rows.append(
            f"| {target_language.upper()} | — | — | — | {correctness} | {status} |"
        )
    else:
        correctness = "PASS" if verification and verification.verified else "FAIL"
        status = (
            "Optimized"
            if target_language.lower() == source_language.lower()
            else ("Faster" if benchmark.faster else "Slower")
        )
        rows.append(
            f"| {target_language.upper()} | "
            f"{benchmark.generated_average:.6f} | "
            f"{benchmark.speedup:.2f}× | "
            f"{benchmark.improvement_percent:.2f}% | "
            f"{correctness} | {status} |"
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

        save_run(
            source_code=source_code,
            generated_code=generated,
            source_language=source_language,
            target_language=target_language,
            model=model_name,
            test_input=test_input or "",
            benchmark=result["benchmark"],
            verification=result["verification"],
            recommendation=result["recommendation"],
        )

        return (
            generated,
            render_comparison(
                source_language,
                target_language,
                result["benchmark"],
                result["verification"],
                result["recommendation"],
            ),
            render_history(),
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
            render_history(),
            "### 🧠 Algorithm Analysis\n\nUnavailable.",
            "### 🧪 Verification\n\nUnavailable.",
            "### ⚡ Performance\n\nUnavailable.",
            "### 🏆 OptiForge Recommendation\n\n**REJECT** — The operation could not be completed.",
            f"❌ {type(exc).__name__}: {exc}",
        )


with gr.Blocks(title="OptiForge.Ai", css=CSS, theme=gr.themes.Default()) as app:
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
            value=list(MODEL_OPTIONS.keys())[0],
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

    # Full-width result section 1: Language Comparison
    with gr.Column(elem_id="full_width_result"):
        comparison_result = gr.Markdown(
            "Run an optimization to see the measured comparison."
        )

    # Full-width result section 2: Persistent Comparison History
    with gr.Column(elem_id="full_width_result"):
        history_result = gr.Markdown(
            render_history(),
            elem_id="history",
        )

    # Full-width result section 3: Algorithm Analysis
    with gr.Column(elem_id="full_width_result"):
        algorithm_result = gr.Markdown(
            "Algorithm analysis will appear here.",
            elem_id="algorithm_analysis",
        )

    # Three equal-width result grids:
    # Verification | Performance | OptiForge Recommendation
    with gr.Row(equal_height=True, elem_id="result_grid"):
        with gr.Column(scale=1, min_width=0, elem_id="result_card"):
            verification_result = gr.Markdown(
                "Verification results will appear here."
            )

        with gr.Column(scale=1, min_width=0, elem_id="result_card"):
            performance_result = gr.Markdown(
                "Benchmark results will appear here."
            )

        with gr.Column(scale=1, min_width=0, elem_id="result_card"):
            recommendation_result = gr.Markdown(
                "Recommendation will appear here."
            )

    error_result = gr.Markdown(visible=True)

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
            history_result,
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
    