# ⚡ OptiForge.Ai

> **AI proposes. The compiler executes. The verifier checks. The benchmark measures. OptiForge decides.**

OptiForge.Ai is an AI-powered code transformation and optimization platform for Python, C++, and Java. It transforms source code into a selected target language, compiles and executes the generated implementation, verifies its behavior against the original program, benchmarks runtime, and produces an evidence-based recommendation.

---

## 🚀 What is OptiForge.Ai?

AI code generation alone cannot reliably answer:

- Does the generated program compile?
- Does it run?
- Does it preserve behavior?
- Is it actually faster?
- How much faster is it?
- Should the generated implementation replace the original?

OptiForge is built around these questions.

### Core philosophy

```text
AI proposes.
The compiler executes.
The verifier checks.
The benchmark measures.
OptiForge decides.
```

The system treats AI output as a **candidate**, not as a trusted answer.

---

# 🎯 Project Goal

OptiForge connects:

```text
Generative AI
      +
Static Analysis
      +
Compilers
      +
Program Execution
      +
Behavioral Verification
      +
Performance Benchmarking
      +
Evidence-Based Decision Making
```

The objective is to turn AI-assisted optimization from a generation task into a measurable engineering workflow.

---

# ✨ Key Features

## Multi-language support

Currently supported:

```text
Python
C++
Java
```

## Multi-language transformation

Supported transformations include:

```text
Python → Python
Python → C++
Python → Java

C++ → C++
C++ → Python
C++ → Java

Java → Java
Java → Python
Java → C++
```

Same-language transformations are treated primarily as optimization/refactoring.

Cross-language transformations are treated as:

```text
Translation + Optimization
```

## Algorithm analysis

OptiForge analyzes:

- Language
- Lines of code
- Functions
- Loops
- Imports
- Input/output
- Complexity hints
- Performance patterns
- Algorithm
- Approach
- Time complexity
- Space complexity
- Optimization opportunities

Example:

```text
Algorithm:
Summation of consecutive integers

Approach:
Iterative accumulation

Time Complexity:
O(n)

Space Complexity:
O(1)

Optimization Opportunity:
Use a mathematical formula instead of iteration
```

The analyzer provides engineering signals and heuristics rather than claiming formal proof.

---

# 🤖 AI Transformation

The transformation layer uses the selected model to generate a complete target-language implementation.

The model receives relevant information such as:

- Source code
- Source language
- Target language
- Code analysis
- Transformation mode
- Optimization requirements

The generation layer is instructed to preserve program I/O and produce executable source code.

The LLM proposes the implementation.

It does **not** decide whether the implementation is correct or faster.

---

# 🧩 Supported AI Models

| Model | Provider | Execution |
|---|---|---|
| Qwen3.5 2B | Ollama | Local |
| Llama 3.2 | Ollama | Local |
| GPT-OSS 120B | Groq | API |
| Gemini 2.5 Pro | Google | API |
| Qwen3 Coder 30B | OpenRouter | API |

The model can be selected from the UI.

---

# 🔬 Verification

Generated code is executed using deterministic test input when the program requires stdin.

Conceptually:

```text
Original Program
      ↓
   Execute
      ↓
Original Output
      │
      │ compare
      ↓
Generated Program
      ↓
   Execute
      ↓
Generated Output
```

Outputs are normalized and compared.

```text
✅ VERIFIED
```

means the generated implementation matched the original for the available test case(s).

```text
❌ NOT VERIFIED
```

means behavioral verification failed.

Passing a limited test suite is not the same as formal proof of program equivalence.

---

# ⏱️ Benchmarking

After successful verification, OptiForge benchmarks the implementations.

Measured values include:

- Average runtime
- Median runtime
- Best runtime
- Worst runtime
- Speedup
- Improvement percentage
- Whether the generated implementation is faster

Example:

```text
Original Runtime:
0.176672 s

Generated Runtime:
0.139757 s

Speedup:
1.26×

Improvement:
20.89%
```

### Speedup

```text
Speedup = Original Runtime / Generated Runtime
```

### Improvement

```text
Improvement =
((Original Runtime - Generated Runtime)
 / Original Runtime) × 100
```

Benchmark results are workload-dependent.

---

# 🏆 Recommendation Engine

OptiForge does not automatically trust or replace the original program.

The decision process is:

```text
Generated Candidate
       │
       ▼
   Compiles?
    /     \
  NO       YES
  │          │
  ▼          ▼
REJECT    Verified?
           /    \
         NO      YES
         │         │
         ▼         ▼
      REJECT    Benchmark
                   │
                   ▼
              Faster enough?
                /       \
              NO         YES
              │            │
              ▼            ▼
       KEEP ORIGINAL     ACCEPT
```

The core idea is:

```text
AI-generated
```

is different from:

```text
AI-generated
+
compiled
+
verified
+
benchmarked
```

Only evidence-backed candidates can earn acceptance.

---

# 🌍 Comparison History

OptiForge retains comparison results during the current application session.

Results are grouped by source language and target language.

Example:

```text
Source: Java

Language          Runtime    Speedup    Improvement    Correctness    Status
----------------------------------------------------------------------------
JAVA (Baseline)   0.180s     1.00×      0.00%          PASS            Baseline
JAVA              0.150s     1.20×     16.67%          PASS            Optimized
CPP               0.090s     2.00×     50.00%          PASS            Faster
PYTHON            0.160s     1.12×     11.11%          PASS            Faster
```

Testing another target updates that target's result without removing other target-language comparisons.

---

# 🖥️ User Interface

OptiForge uses a minimal Gradio interface.

```text
                         OptiForge.Ai

┌────────────────────────────┐  ┌────────────────────────────┐
│                            │  │                            │
│       SOURCE CODE          │  │      GENERATED CODE         │
│                            │  │                            │
└────────────────────────────┘  └────────────────────────────┘

 Source Language    Target Language       Model

                         Test Input

                    [ Optimize Code ]

                         RESULTS

 Language Comparison
 Algorithm Analysis
 Verification
 Performance
 Recommendation

                    Built with Gradio
```

The UI intentionally avoids unnecessary features and keeps the optimization workflow focused.

---

# 🏗️ Architecture

```text
OptiForge.Ai/
│
├── optiforge/
│   ├── analyzer.py
│   ├── transformer.py
│   ├── compiler.py
│   ├── verifier.py
│   ├── benchmark.py
│   ├── models.py
│   └── pipeline.py
│
├── app.py
├── requirements.txt
├── README.md
└── .env.example
```

---

# 📦 Module Responsibilities

### `app.py`

Gradio application layer.

Responsible for:

- UI
- Source editor
- Generated-code editor
- Language selection
- Model selection
- Test input
- Result rendering
- Comparison history

### `optiforge/analyzer.py`

Static analysis layer.

Responsible for:

- Language validation
- Code profiling
- Function detection
- Loop detection
- Import detection
- I/O detection
- Complexity hints
- Performance patterns
- Algorithm analysis

### `optiforge/transformer.py`

AI transformation layer.

Responsible for:

- Model configuration
- Provider configuration
- Transformation prompts
- LLM invocation
- Generated-code cleanup

### `optiforge/compiler.py`

Execution layer.

Responsible for:

- Python execution
- C++ compilation/execution
- Java compilation/execution
- Temporary build directories
- Timeouts
- Runtime capture
- Return codes
- stdout/stderr

### `optiforge/verifier.py`

Correctness layer.

Responsible for:

- Test-case creation
- Output normalization
- Output comparison
- Behavioral verification

### `optiforge/benchmark.py`

Performance layer.

Responsible for:

- Multiple benchmark runs
- Average runtime
- Median runtime
- Best/worst runtime
- Speedup
- Improvement percentage

### `optiforge/models.py`

Decision/data layer.

Responsible for:

- Candidate representation
- Candidate eligibility
- Recommendation representation
- Acceptance logic

### `optiforge/pipeline.py`

Orchestration layer.

Connects:

```text
Analyzer
   ↓
Algorithm Analysis
   ↓
Test Case Creation
   ↓
LLM Transformation
   ↓
Compilation
   ↓
Execution
   ↓
Verification
   ↓
Benchmark
   ↓
Recommendation
```

---

# 🔧 Prerequisites

## 1. Python

Recommended:

```text
Python 3.12.x
```

Verify:

```bash
python --version
```

or:

```bash
py -3.12 --version
```

## 2. C++ Compiler

OptiForge uses `g++`.

On Windows, MSYS2 UCRT64 is recommended.

Install MSYS2:

```text
https://www.msys2.org/
```

Install the compiler:

```bash
pacman -S --needed mingw-w64-ucrt-x86_64-gcc
```

Verify:

```bash
g++ --version
```

and:

```bash
where g++
```

C++ is compiled with:

```text
g++ -std=c++17 -O2
```

## 3. Java

Recommended:

```text
Java 21+
```

Verify:

```bash
java --version
javac --version
```

## 4. Git

Verify:

```bash
git --version
```

## 5. Ollama

Required only for local models.

Install:

```text
https://ollama.com/
```

Verify:

```bash
ollama --version
```

Example:

```bash
ollama pull qwen3.5:2b
ollama pull llama3.2
```

---

# 🐍 Python Requirements

The main Python dependencies are:

```text
gradio
openai
python-dotenv
```

Install:

```bash
pip install -r requirements.txt
```

---

# 🔑 API Configuration

API-based models require provider API keys.

Create:

```text
.env
```

from:

```text
.env.example
```

Example:

```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

Never commit `.env`.

Commit only:

```text
.env.example
```

with placeholder values.

---

# 🧪 Complete Installation

Clone the repository:

```bash
git clone https://github.com/saileshchikkam/OptiForge.Ai.git
```

Enter the project:

```bash
cd OptiForge.Ai
```

Create a virtual environment:

```bash
py -3.12 -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scriptsctivate
```

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Verify:

```bash
python --version
```

Check core imports:

```bash
python -c "import gradio, openai, dotenv; print('Dependencies OK')"
```

---

# ⚙️ Configure Environment

Copy:

```text
.env.example
```

to:

```text
.env
```

Add the required provider keys:

```env
GROQ_API_KEY=
GOOGLE_API_KEY=
OPENROUTER_API_KEY=
```

Use only the keys required by the selected model.

---

# ▶️ Run OptiForge

Start the application:

```bash
python app.py
```

Open the local Gradio address shown in the terminal.

Typical address:

```text
http://127.0.0.1:7860
```

The exact port can vary.

---

# 🧑‍💻 Basic Usage

### Step 1 — Enter source code

Paste code into:

```text
SOURCE CODE
```

### Step 2 — Select source language

Choose:

```text
Python
C++
Java
```

### Step 3 — Select target language

Example:

```text
Source: Python
Target: C++
```

### Step 4 — Select model

Choose an available AI model.

### Step 5 — Provide deterministic test input

For programs using stdin:

```text
1000000
```

### Step 6 — Run

Click:

```text
Optimize Code
```

OptiForge executes the complete pipeline.

---

# 📊 Example

Source:

```python
n = int(input())

total = 0

for i in range(1, n + 1):
    total += i

print(total)
```

Target:

```text
C++
```

The pipeline performs:

```text
1. Analyze source
2. Analyze algorithm
3. Build transformation prompt
4. Ask selected LLM for target code
5. Clean generated code
6. Compile generated code
7. Execute original program
8. Execute generated program
9. Compare outputs
10. Benchmark both implementations
11. Calculate speedup
12. Calculate improvement
13. Produce recommendation
```

---

# 🛡️ Safety and Reliability Philosophy

OptiForge follows:

> **Generated code is a candidate, not a trusted result.**

The architecture separates:

```text
Generation
    ↓
Validation
    ↓
Measurement
    ↓
Decision
```

This prevents:

```text
"LLM says it is optimized"
```

from being interpreted as:

```text
"Program is actually optimized"
```

---

# ⚠️ Current Limitations

## Deterministic programs

Verification works best with deterministic stdin/stdout programs.

Programs heavily dependent on:

- Randomness
- Current time
- Network requests
- External services
- External files
- Interactive behavior
- OS side effects

are not reliably verifiable by the current MVP.

## Test coverage

The current UI provides deterministic test input.

Passing the supplied test case does not mathematically prove complete program equivalence.

## Benchmark workload

Performance results depend on the tested input.

A program faster on one workload may not be faster on another.

## AI reliability

LLMs can generate:

- Incorrect syntax
- Incorrect logic
- Incomplete code
- Poor optimizations
- Semantically different behavior

Compilation and verification therefore remain mandatory.

## Hardware

Local model performance depends on:

- CPU
- RAM
- GPU
- VRAM
- Model size
- Context length

---

# 🔐 Security Considerations

OptiForge executes generated code.

Therefore, the current MVP should primarily be used for:

```text
Local development
Controlled experimentation
Trusted source code
```

It should not be considered a secure multi-user sandbox.

A production deployment should introduce:

- Container isolation
- CPU limits
- Memory limits
- Process limits
- Execution time limits
- Filesystem isolation
- Network isolation
- Restricted system calls
- Resource quotas
- Per-user execution environments

before allowing arbitrary untrusted code.

---

# 🧪 Development Philosophy

OptiForge is developed incrementally:

```text
Build
 ↓
Test
 ↓
Measure
 ↓
Validate
 ↓
Integrate
```

The engineering progression is:

```text
Environment
    ↓
Language Support
    ↓
Code Analysis
    ↓
Transformation
    ↓
Compilation
    ↓
Verification
    ↓
Benchmarking
    ↓
Candidate Evaluation
    ↓
Recommendation
    ↓
UI Integration
```

---

# 🧱 Design Principles

## 1. AI is a proposer

The LLM generates candidates.

It does not make the final decision.

## 2. Compilation matters

If generated C++ or Java does not compile, it is rejected.

## 3. Behavior matters

A fast program that produces the wrong result is not an optimization.

## 4. Measurement matters

Performance claims must come from benchmark measurements.

## 5. Preserve the original when necessary

If the candidate does not provide sufficient verified benefit:

```text
KEEP ORIGINAL
```

is the correct decision.

---

# 🔭 Future Vision

OptiForge can evolve into a broader evidence-driven program optimization engine.

Future architecture:

```text
                       SOURCE PROGRAM
                             │
                             ▼
                         ANALYZER
                             │
                             ▼
                    OPTIMIZATION PLANNER
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
          MODEL 1         MODEL 2         MODEL 3
             │               │               │
             ▼               ▼               ▼
          CANDIDATE        CANDIDATE        CANDIDATE
             │               │               │
             ▼               ▼               ▼
          COMPILE          COMPILE          COMPILE
             │               │               │
             ▼               ▼               ▼
          VERIFY           VERIFY           VERIFY
             │               │               │
             ▼               ▼               ▼
        BENCHMARK         BENCHMARK        BENCHMARK
             │               │               │
             └───────────────┼───────────────┘
                             ▼
                           RANKING
                             │
                             ▼
                    EVIDENCE-BASED DECISION
```

Potential future capabilities:

- Multi-candidate generation
- Multi-model competition
- Automatic test generation
- Property-based verification
- Regression testing
- Advanced static analysis
- More programming languages
- Hardware-aware optimization
- Benchmark reproducibility
- Secure execution sandboxes
- Persistent benchmark history
- Project/workspace-level optimization
- Compiler-aware transformations
- Optimization reports
- CI/CD integration
- Developer tooling integration

These are future directions, not current MVP requirements.

---

# 🗺️ Current MVP Scope

## Included

```text
✅ Python
✅ C++
✅ Java

✅ Same-language optimization
✅ Cross-language transformation
✅ Algorithm analysis
✅ AI-based code generation
✅ Compilation
✅ Execution
✅ Behavioral verification
✅ Runtime benchmarking
✅ Speedup measurement
✅ Improvement measurement
✅ Recommendation engine
✅ Model selection
✅ Comparison history
✅ Gradio UI
```

## Not currently included

```text
❌ Arbitrary untrusted-code sandboxing
❌ Formal program equivalence
❌ Guaranteed semantic equivalence
❌ Distributed benchmarking
❌ Persistent benchmark database
❌ Full project-wide optimization
❌ Automatic multi-model competition
❌ CI/CD deployment system
```

---

# 📁 Project Structure

```text
OptiForge.Ai/
│
├── optiforge/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── transformer.py
│   ├── compiler.py
│   ├── verifier.py
│   ├── benchmark.py
│   ├── models.py
│   └── pipeline.py
│
├── app.py
├── requirements.txt
├── README.md
└── .env.example
```

---

# 🔄 Complete End-to-End Pipeline

```text
SOURCE CODE
    │
    ▼
LANGUAGE SELECTION
    │
    ▼
STATIC ANALYSIS
    │
    ├── Code Profile
    ├── Algorithm
    ├── Complexity
    ├── Functions
    ├── Loops
    ├── I/O
    └── Performance Patterns
    │
    ▼
TRANSFORMATION PLANNING
    │
    ▼
SELECTED LLM
    │
    ▼
GENERATED CANDIDATE
    │
    ▼
OUTPUT CLEANING
    │
    ▼
COMPILATION / EXECUTION
    │
    ├── FAIL ──────────────► REJECT
    │
    ▼
BEHAVIORAL VERIFICATION
    │
    ├── FAIL ──────────────► REJECT
    │
    ▼
BENCHMARK
    │
    ├── Runtime
    ├── Median
    ├── Best
    ├── Worst
    ├── Speedup
    └── Improvement
    │
    ▼
RECOMMENDATION ENGINE
    │
    ├── ACCEPT
    │
    └── KEEP ORIGINAL
```

---

# 🛠️ Development Commands

Create environment:

```bash
py -3.12 -m venv .venv
```

Activate:

```bash
.venv\Scriptsctivate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run application:

```bash
python app.py
```

Check Python:

```bash
python --version
```

Check C++:

```bash
g++ --version
```

Check Java:

```bash
java --version
javac --version
```

Check Git:

```bash
git --version
```

---

# 🧹 Recommended `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo

# Virtual environments
.venv/
venv/
env/

# Environment variables
.env

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Build artifacts
*.exe
*.class
*.o
*.obj

# Temporary files
*.tmp
*.temp
```

---

# 📜 License

Add the project's chosen license before public distribution.

Example:

```text
MIT License
```

Do not assume a license until one has been formally selected.

---

# 👨‍💻 Project Status

**Status: Active MVP Development**

The current implementation demonstrates the complete core loop:

```text
Analyze
   ↓
Generate
   ↓
Compile
   ↓
Verify
   ↓
Benchmark
   ↓
Decide
```

The current focus is to make this loop:

```text
Reliable
Measurable
Explainable
Extensible
```

before expanding the feature surface.

---

# ⭐ Why OptiForge.Ai?

Most AI coding tools focus on:

```text
"Generate code."
```

OptiForge focuses on:

```text
"Generate a candidate.
Prove that it works.
Measure whether it is better.
Then decide."
```

That distinction is the foundation of OptiForge.Ai.

---

## ⚡ OptiForge.Ai

> **From AI-generated code to evidence-backed optimization.**

```text
AI proposes.
Compiler executes.
Verifier checks.
Benchmark measures.
OptiForge decides.
```
