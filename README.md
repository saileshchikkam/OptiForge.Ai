# OptiForge.Ai — Phase 10

OptiForge accepts Python, C++, or Java source code, asks a selected LLM for a transformed implementation, executes it, verifies output equivalence, benchmarks runtime, and makes a recommendation from measured evidence.

## Architecture

Source Code
→ Phase 3 Analyzer
→ Phase 4 Transformer
→ Phase 5 Execution
→ Phase 6 Verification
→ Phase 7 Benchmark
→ Phase 8 Candidate
→ Phase 9 Recommendation
→ Phase 10 Gradio UI

## Phase 10 UI

- Source code editor
- Generated code editor
- Source language
- Target language
- Model selection
- Deterministic test input
- Language comparison table
- Algorithm analysis
- Verification
- Benchmark
- Speedup
- Improvement %
- Recommendation

## Run

```bash
pip install -r requirements.txt
python app.py
```

For API models, configure the appropriate key in `.env`.

Ollama models require Ollama to be running locally and the selected model to be installed.
