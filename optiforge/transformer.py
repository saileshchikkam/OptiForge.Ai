import os
from openai import OpenAI

from .analyzer import CodeProfile


MODEL_OPTIONS = {
    "Qwen3.5 2B (Ollama)": ("qwen3.5:2b", "ollama"),
    "GPT-OSS 120B (Groq)": ("openai/gpt-oss-120b", "groq"),
    "Gemini 2.5 Pro": ("gemini-2.5-pro", "gemini"),
    "Llama 3.2 (Ollama)": ("llama3.2:latest", "ollama"),
    "Qwen3 Coder 30B (OpenRouter)": (
        "qwen/qwen3-coder-30b-a3b-instruct",
        "openrouter",
    ),
}


SYSTEM_PROMPT = """You are OptiForge AI, a software transformation and optimization engine.

Transform the supplied source program into the requested target language while preserving
observable behavior.

Rules:
1. Preserve input/output behavior.
2. Preserve edge cases and integer behavior.
3. Produce complete executable source code.
4. Improve performance when a real optimization is possible.
5. Prefer standard libraries and simple implementations.
6. Do not invent external dependencies.
7. For Java, the entry class MUST be named Main.
8. Return ONLY source code. No Markdown fences. No explanations.
9. Never claim the generated code is correct or faster; OptiForge will verify and benchmark it.
"""


def _clients():
    return {
        "ollama": OpenAI(base_url="http://localhost:11434/v1", api_key="ollama"),
        "groq": OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY") or "",
        ),
        "gemini": OpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "",
        ),
        "openrouter": OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY") or "",
        ),
    }


def build_transformation_prompt(
    source_code: str,
    source_language: str,
    target_language: str,
    profile: CodeProfile,
) -> str:
    mode = "optimization" if source_language == target_language else "translation + optimization"
    return f"""Transformation mode: {mode}
Source language: {source_language}
Target language: {target_language}

Source profile:
- Lines: {profile.total_lines}
- Functions: {profile.functions}
- Loops: {profile.loops}
- Imports: {profile.imports}
- I/O: {profile.io_operations}
- Complexity hints: {profile.complexity_hints}
- Performance patterns: {profile.performance_patterns}

SOURCE CODE
-----------
{source_code}
-----------

Return the complete {target_language} program only."""


def clean_generated_code(code: str | None) -> str:
    if not code:
        raise ValueError("The selected model returned no source code.")

    code = code.strip()

    if code.startswith("```"):
        lines = code.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        code = "\n".join(lines).strip()

    return code


def generate_code(
    model_display_name: str,
    source_code: str,
    source_language: str,
    target_language: str,
    profile: CodeProfile,
) -> str:
    if model_display_name not in MODEL_OPTIONS:
        raise ValueError(f"Unknown model selection: {model_display_name}")

    model, provider = MODEL_OPTIONS[model_display_name]
    client = _clients()[provider]

    if provider != "ollama" and not client.api_key:
        raise ValueError(
            f"{model_display_name} requires its API key in the environment."
        )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_transformation_prompt(
                    source_code, source_language, target_language, profile
                ),
            },
        ],
        temperature=0,
    )

    content = response.choices[0].message.content
    return clean_generated_code(content)
