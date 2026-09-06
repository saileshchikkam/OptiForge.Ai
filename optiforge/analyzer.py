from dataclasses import dataclass, field
import ast
import re


SUPPORTED_LANGUAGES = {
    "python": {"name": "Python", "extensions": [".py"]},
    "java": {"name": "Java", "extensions": [".java"]},
    "cpp": {"name": "C++", "extensions": [".cpp", ".cc", ".cxx"]},
}


@dataclass
class CodeProfile:
    language: str
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    functions: list = field(default_factory=list)
    loops: int = 0
    imports: list = field(default_factory=list)
    io_operations: list = field(default_factory=list)
    complexity_hints: list = field(default_factory=list)
    performance_patterns: list = field(default_factory=list)


@dataclass
class AlgorithmAnalysis:
    algorithm: str = "General-purpose program"
    approach: str = "Direct program execution"
    time_complexity: str = "Not determined"
    space_complexity: str = "Not determined"
    optimization_opportunity: str = "No specific optimization inferred"


def validate_language(language: str) -> None:
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported language: {language}")


def count_lines(code: str, language: str) -> dict:
    lines = code.splitlines()
    total = len(lines)
    blank = comments = code_lines = 0
    block = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank += 1
            continue

        if block:
            comments += 1
            if "*/" in stripped:
                block = False
            continue

        if language == "python" and stripped.startswith("#"):
            comments += 1
            continue

        if language in {"java", "cpp"}:
            if stripped.startswith("//"):
                comments += 1
                continue
            if stripped.startswith("/*"):
                comments += 1
                if "*/" not in stripped:
                    block = True
                continue

        code_lines += 1

    return {"total": total, "code": code_lines, "comments": comments, "blank": blank}


def detect_functions(code: str, language: str) -> list:
    if language == "python":
        try:
            tree = ast.parse(code)
            return [
                node.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
        except SyntaxError:
            return re.findall(r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)\s*\(", code, re.M)

    if language == "java":
        pattern = r"(?:public|private|protected|static|final|native|synchronized|\s)+[\w<>\[\]]+\s+([A-Za-z_]\w*)\s*\("
    elif language == "cpp":
        pattern = r"^\s*(?:[\w:<>,*&~]+\s+)+([A-Za-z_]\w*)\s*\([^;]*\)\s*(?:const\s*)?\{"
    else:
        return []

    return list(dict.fromkeys(re.findall(pattern, code, re.M)))


def count_loops(code: str, language: str) -> int:
    if language == "python":
        return len(re.findall(r"\b(?:for|while)\b", code))
    return len(re.findall(r"\b(?:for|while)\s*\(", code))


def detect_imports(code: str, language: str) -> list:
    if language == "python":
        return [x.strip() for x in re.findall(r"^\s*(?:import\s+.+|from\s+.+\s+import\s+.+)$", code, re.M)]
    if language == "java":
        return [x.strip() for x in re.findall(r"^\s*import\s+.+?;", code, re.M)]
    if language == "cpp":
        return [x.strip() for x in re.findall(r'^\s*#include\s*[<"][^>"]+[>"]', code, re.M)]
    return []


def detect_io(code: str, language: str) -> list:
    patterns = {
        "python": {"input": r"\binput\s*\(", "output": r"\bprint\s*\("},
        "java": {"input": r"\bScanner\b|\.next\w*\s*\(", "output": r"\bSystem\.out\."},
        "cpp": {"input": r"\bcin\s*>>", "output": r"\bcout\s*<<"},
    }
    found = []
    for name, pattern in patterns.get(language, {}).items():
        if re.search(pattern, code):
            found.append(name)
    return found


def complexity_hints(code: str, language: str) -> list:
    hints = []
    loops = count_loops(code, language)

    if loops == 1:
        hints.append("Possible linear iteration: O(n)")
    elif loops >= 2:
        hints.append("Multiple loops detected; inspect for possible O(n²) or higher complexity")

    if re.search(r"\b(?:sort|sorted)\s*\(", code):
        hints.append("Sorting operation detected: commonly O(n log n)")

    if re.search(r"\b(?:set|dict|map|unordered_map|HashMap|HashSet)\b", code):
        hints.append("Hash/map data structure detected")

    return hints


def detect_performance_patterns(code: str, language: str) -> list:
    patterns = []
    loops = count_loops(code, language)

    if loops >= 2:
        patterns.append("Multiple loops detected")
    if re.search(r"\b(?:sort|sorted)\s*\(", code):
        patterns.append("Sorting operation")
    if language == "python" and re.search(r"\w+\s*\+=\s*[\"']", code):
        patterns.append("Repeated string concatenation may be expensive")
    if language in {"java", "cpp"} and re.search(r"\.append\s*\(", code):
        patterns.append("Repeated append operation")

    return patterns


def analyze_code(code: str, language: str) -> CodeProfile:
    if not isinstance(code, str) or not code.strip():
        raise ValueError("Source code cannot be empty.")
    validate_language(language)

    lines = count_lines(code, language)
    return CodeProfile(
        language=language,
        total_lines=lines["total"],
        code_lines=lines["code"],
        comment_lines=lines["comments"],
        blank_lines=lines["blank"],
        functions=detect_functions(code, language),
        loops=count_loops(code, language),
        imports=detect_imports(code, language),
        io_operations=detect_io(code, language),
        complexity_hints=complexity_hints(code, language),
        performance_patterns=detect_performance_patterns(code, language),
    )


def analyze_algorithm(code: str, language: str, profile: CodeProfile | None = None) -> AlgorithmAnalysis:
    profile = profile or analyze_code(code, language)

    if language == "python":
        try:
            tree = ast.parse(code)
            if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in {"sort", "sorted"} for n in ast.walk(tree)):
                return AlgorithmAnalysis(
                    algorithm="Sorting",
                    approach="Ordering a collection using a sorting operation",
                    time_complexity="Typically O(n log n)",
                    space_complexity="Implementation dependent",
                    optimization_opportunity="Avoid unnecessary sorting or sort only the required portion",
                )
        except SyntaxError:
            pass

    if profile.loops >= 2:
        return AlgorithmAnalysis(
            algorithm="Nested/multiple-loop computation",
            approach="Iterative traversal with multiple loop levels",
            time_complexity="Potentially O(n²) or higher",
            space_complexity="O(1) auxiliary space unless collections are created",
            optimization_opportunity="Inspect loop nesting and look for hashing, indexing, or one-pass alternatives",
        )

    if profile.loops == 1:
        return AlgorithmAnalysis(
            algorithm="Linear iteration",
            approach="Single-pass iterative processing",
            time_complexity="O(n)",
            space_complexity="O(1) auxiliary space unless additional storage is used",
            optimization_opportunity="Look for vectorization, built-ins, closed-form formulas, or unnecessary work inside the loop",
        )

    return AlgorithmAnalysis(
        algorithm="Direct computation",
        approach="No dominant loop-based algorithm detected",
        time_complexity="Not determined",
        space_complexity="Not determined",
        optimization_opportunity="Inspect expensive operations and I/O before changing the implementation",
    )
