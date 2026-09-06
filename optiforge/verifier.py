from dataclasses import dataclass, field
from .compiler import run_code


@dataclass
class TestCaseResult:
    test_number: int
    passed: bool
    expected_output: str
    actual_output: str
    original_runtime: float
    generated_runtime: float
    error: str = ""


@dataclass
class VerificationResult:
    verified: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    test_results: list = field(default_factory=list)
    reason: str = ""


def normalize_output(output: str) -> str:
    return output.strip()


def compare_outputs(expected: str, actual: str) -> bool:
    return normalize_output(expected) == normalize_output(actual)


def create_test_cases(test_input: str, source_uses_input: bool) -> list[str]:
    if source_uses_input:
        if not test_input.strip():
            raise ValueError(
                "This program reads standard input. Enter test input before optimizing."
            )
        return [test_input]
    return [test_input or ""]


def verify_programs(
    original_code: str,
    original_language: str,
    generated_code: str,
    generated_language: str,
    test_inputs: list[str],
) -> VerificationResult:
    results = []

    for number, input_data in enumerate(test_inputs, 1):
        original = run_code(original_code, original_language, input_data)

        if not original.success:
            results.append(
                TestCaseResult(
                    number, False, "", "", original.runtime, 0.0,
                    f"Original program failed during {original.phase}: {original.stderr.strip()}",
                )
            )
            continue

        generated = run_code(generated_code, generated_language, input_data)

        if not generated.success:
            results.append(
                TestCaseResult(
                    number, False, original.stdout, generated.stdout,
                    original.runtime, generated.runtime,
                    f"Generated program failed during {generated.phase}: {generated.stderr.strip()}",
                )
            )
            continue

        passed = compare_outputs(original.stdout, generated.stdout)
        results.append(
            TestCaseResult(
                number,
                passed,
                original.stdout,
                generated.stdout,
                original.runtime,
                generated.runtime,
                "" if passed else "Output mismatch.",
            )
        )

    passed = sum(x.passed for x in results)
    failed = len(results) - passed
    verified = bool(results) and failed == 0

    return VerificationResult(
        verified,
        len(results),
        passed,
        failed,
        results,
        "All test cases passed." if verified else f"{failed} test case(s) failed.",
    )
