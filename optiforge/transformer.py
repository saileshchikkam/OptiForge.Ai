import os
from openai import OpenAI

from .analyzer import CodeProfile


MODEL_OPTIONS = {
    "GPT-OSS 120B (Groq)": (
        "openai/gpt-oss-120b",
        "groq",
    ),

    "Qwen3.8 27B (Groq)": (
        "qwen/qwen3.8-27b",
        "groq",
    ),

    "Qwen3 Coder 480B (OpenRouter)": (
        "qwen/qwen3-coder-480b-a35b-instruct",
        "openrouter",
    ),

    "Qwen3 Coder Next (OpenRouter)": (
        "qwen/qwen3-coder-next",
        "openrouter",
    ),

    "Qwen3.6 27B (OpenRouter)": (
        "qwen/qwen3.6-27b",
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


def _client(provider):

    if provider == "groq":
        return OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY") or "",
        )

    if provider == "openrouter":
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY") or "",
        )

    raise ValueError(f"Unsupported provider: {provider}")


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
    client = _client(provider)

    if not client.api_key:
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
