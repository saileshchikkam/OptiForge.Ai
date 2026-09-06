from .analyzer import analyze_code, analyze_algorithm
from .transformer import generate_code
from .verifier import create_test_cases, verify_programs
from .benchmark import benchmark_comparison
from .models import CandidateResult, build_recommendation


def optimize(
    source_code: str,
    source_language: str,
    target_language: str,
    model_display_name: str,
    test_input: str = "",
):
    """Run the complete Phase 3-9 engine for one selected model."""
    profile = analyze_code(source_code, source_language)
    algorithm = analyze_algorithm(source_code, source_language, profile)

    test_inputs = create_test_cases(
        test_input,
        source_uses_input="input" in profile.io_operations,
    )

    generated = generate_code(
        model_display_name=model_display_name,
        source_code=source_code,
        source_language=source_language,
        target_language=target_language,
        profile=profile,
    )

    candidate = CandidateResult(
        candidate_id="C1",
        model=model_display_name,
        source_code=generated,
        language=target_language,
    )

    # Initial compile/execution gate.
    initial = __import__("optiforge.compiler", fromlist=["run_code"]).run_code(
        generated, target_language, test_input
    )
    if not initial.success:
        candidate.status = "compilation_failed"
        return {
            "profile": profile,
            "algorithm": algorithm,
            "candidate": candidate,
            "verification": None,
            "benchmark": None,
            "recommendation": build_recommendation([candidate]),
        }

    candidate.compiled = True

    verification = verify_programs(
        source_code,
        source_language,
        generated,
        target_language,
        test_inputs,
    )
    candidate.verification = verification
    candidate.verified = verification.verified

    if not candidate.verified:
        candidate.status = "verification_failed"
        return {
            "profile": profile,
            "algorithm": algorithm,
            "candidate": candidate,
            "verification": verification,
            "benchmark": None,
            "recommendation": build_recommendation([candidate]),
        }

    benchmark = benchmark_comparison(
        source_code,
        source_language,
        generated,
        target_language,
        test_input,
        runs=5,
    )
    candidate.benchmark = benchmark
    candidate.status = "verified"

    recommendation = build_recommendation([candidate])

    return {
        "profile": profile,
        "algorithm": algorithm,
        "candidate": candidate,
        "verification": verification,
        "benchmark": benchmark,
        "recommendation": recommendation,
    }
