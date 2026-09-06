from dataclasses import dataclass, field


@dataclass
class CandidateResult:
    candidate_id: str
    model: str
    source_code: str
    language: str
    compiled: bool = False
    verified: bool = False
    verification: object = None
    benchmark: object = None
    score: float = 0.0
    status: str = "generated"


@dataclass
class RecommendationResult:
    decision: str
    recommended_candidate: CandidateResult | None = None
    recommended_language: str = ""
    reason: str = ""
    strengths: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


def is_candidate_eligible(candidate: CandidateResult) -> bool:
    return (
        candidate.compiled
        and candidate.verified
        and candidate.benchmark is not None
    )


def build_recommendation(candidates: list[CandidateResult]) -> RecommendationResult:
    eligible = [c for c in candidates if is_candidate_eligible(c)]

    if not eligible:
        return RecommendationResult(
            decision="REJECT",
            reason="No candidate passed compilation, verification, and benchmarking.",
        )

    best = min(eligible, key=lambda c: c.benchmark.generated_average)
    b = best.benchmark

    strengths = [
        f"Measured {b.speedup:.2f}x speedup" if b.faster else "Candidate did not improve measured runtime",
        f"{b.improvement_percent:.2f}% runtime improvement",
    ]
    warnings = []

    if not b.faster:
        warnings.append("The generated implementation is slower than the original.")
    elif b.improvement_percent < 5:
        warnings.append("Performance improvement is relatively small.")

    return RecommendationResult(
        decision="ACCEPT" if b.faster and b.improvement_percent >= 5 else "KEEP ORIGINAL",
        recommended_candidate=best,
        recommended_language=best.language,
        reason=(
            "The candidate passed verification and achieved the best measured runtime."
            if b.faster
            else "The candidate passed verification but did not achieve a meaningful runtime improvement."
        ),
        strengths=strengths,
        warnings=warnings,
    )
