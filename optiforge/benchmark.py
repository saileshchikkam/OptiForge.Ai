from dataclasses import dataclass, field
from statistics import median
from .compiler import run_code


@dataclass
class BenchmarkResult:
    original_runs: list = field(default_factory=list)
    generated_runs: list = field(default_factory=list)
    original_average: float = 0.0
    generated_average: float = 0.0
    original_median: float = 0.0
    generated_median: float = 0.0
    original_best: float = 0.0
    generated_best: float = 0.0
    original_worst: float = 0.0
    generated_worst: float = 0.0
    speedup: float = 0.0
    improvement_percent: float = 0.0
    faster: bool = False


def _run_times(code: str, language: str, input_data: str, runs: int):
    times = []
    for _ in range(runs):
        result = run_code(code, language, input_data)
        if not result.success:
            return None, result
        times.append(result.runtime)
    return times, None


def benchmark_comparison(
    original_code: str,
    original_language: str,
    generated_code: str,
    generated_language: str,
    input_data: str = "",
    runs: int = 5,
) -> BenchmarkResult:
    if runs < 1:
        raise ValueError("Benchmark runs must be at least 1.")

    original_runs, original_error = _run_times(
        original_code, original_language, input_data, runs
    )
    if original_error:
        raise RuntimeError(
            f"Original benchmark failed during {original_error.phase}: {original_error.stderr.strip()}"
        )

    generated_runs, generated_error = _run_times(
        generated_code, generated_language, input_data, runs
    )
    if generated_error:
        raise RuntimeError(
            f"Generated benchmark failed during {generated_error.phase}: {generated_error.stderr.strip()}"
        )

    oa = sum(original_runs) / len(original_runs)
    ga = sum(generated_runs) / len(generated_runs)

    speedup = oa / ga if ga > 0 else 0.0
    improvement = ((oa - ga) / oa * 100.0) if oa > 0 else 0.0

    return BenchmarkResult(
        original_runs=original_runs,
        generated_runs=generated_runs,
        original_average=oa,
        generated_average=ga,
        original_median=median(original_runs),
        generated_median=median(generated_runs),
        original_best=min(original_runs),
        generated_best=min(generated_runs),
        original_worst=max(original_runs),
        generated_worst=max(generated_runs),
        speedup=speedup,
        improvement_percent=improvement,
        faster=ga < oa,
    )
