"""Exact, synthetic examples for complete-kb-selection-method.md.

Run with Python 3; standard library only. This checks mathematical examples,
not catalog capabilities, a production recommender, or decision quality.
"""

from fractions import Fraction as F
from itertools import combinations, product
import json
from pathlib import Path


def dot(values, weights):
    assert len(values) == len(weights)
    assert sum(weights) == 1 and all(w >= 0 for w in weights)
    return sum((F(v) * w for v, w in zip(values, weights)), F(0))


def subsets(items):
    return (
        frozenset(group)
        for size in range(len(items) + 1)
        for group in combinations(items, size)
    )


def feasible_profiles(profiles, requirements):
    return [p for p in profiles if requirements <= p]


def weight_vertices(bounds):
    """Vertices of a box intersected with sum(w)=1, using exact rationals.

    At a vertex all but at most one coordinate lie at box bounds.
    This is not a general LP solver or a sampler.
    """
    vertices = set()
    for free in range(len(bounds)):
        fixed = [i for i in range(len(bounds)) if i != free]
        for values in product(*(bounds[i] for i in fixed)):
            point = [F(0)] * len(bounds)
            for index, value in zip(fixed, values):
                point[index] = value
            point[free] = 1 - sum(values)
            if all(low <= value <= high for value, (low, high) in zip(point, bounds)):
                vertices.add(tuple(point))
    assert vertices, "Empty weight region"
    return sorted(vertices)


def margin_range(a, b, bounds):
    vertices = weight_vertices(bounds)
    margins = [dot(a, w) - dot(b, w) for w in vertices]
    return min(margins), max(margins)


def relative_scores(options, weights):
    lows = [min(row[j] for row in options.values()) for j in range(len(weights))]
    highs = [max(row[j] for row in options.values()) for j in range(len(weights))]
    assert all(high > low for low, high in zip(lows, highs))
    return {
        name: dot(tuple(F(v - low, high - low) for v, low, high in zip(row, lows, highs)), weights)
        for name, row in options.items()
    }


def run_examples():
    results = {}

    # E01: Each requirement has a witness, but there is no common witness.
    required = frozenset({"spark_write", "trino_read"})
    incompatible_profiles = [frozenset({"spark_write"}), frozenset({"trino_read"})]
    assert all(any(r in p for p in incompatible_profiles) for r in required)
    assert not feasible_profiles(incompatible_profiles, required)
    results["E01_joint_compatibility"] = {"separate_checks_pass": True, "joint_check_passes": False}

    # E02: Resolving one conflict need not resolve every conflict.
    requirements = frozenset({"H1", "H2", "H3"})
    profiles = [frozenset({h}) for h in sorted(requirements)]
    conflicts = [s for s in subsets(sorted(requirements)) if not feasible_profiles(profiles, s)]
    minimal_conflicts = [s for s in conflicts if all(feasible_profiles(profiles, s - {h}) for h in s)]
    repairs = [removed for removed in subsets(sorted(requirements)) if feasible_profiles(profiles, requirements - removed)]
    minimal_repairs = [s for s in repairs if not any(other < s for other in repairs)]
    assert {tuple(sorted(s)) for s in minimal_conflicts} == {("H1", "H2"), ("H1", "H3"), ("H2", "H3")}
    assert all(len(s) == 2 for s in minimal_repairs)
    assert not feasible_profiles(profiles, requirements - {"H1"})
    results["E02_conflicts_and_repairs"] = {
        "minimal_conflicts": sorted(sorted(s) for s in minimal_conflicts),
        "minimal_repairs": sorted(sorted(s) for s in minimal_repairs),
        "removing_H1_alone_restores_feasibility": False,
    }

    # E03: Reproduce the pasted scores and their exact switching boundary.
    a, b = (5, 5, 3), (3, 5, 5)
    weights = (F("0.4"), F("0.35"), F("0.25"))
    av, bv = tuple(F(v - 1, 4) for v in a), tuple(F(v - 1, 4) for v in b)
    assert (dot(a, weights), dot(b, weights)) == (F("4.5"), F("4.2"))
    assert (dot(av, weights), dot(bv, weights)) == (F("0.875"), F("0.8"))
    boundary = (F("0.325"), F("0.35"), F("0.325"))
    assert dot(a, boundary) == dot(b, boundary)
    results["E03_weighted_example"] = {
        "raw_scores": [dot(a, weights), dot(b, weights)],
        "value_scores": [dot(av, weights), dot(bv, weights)],
        "tie_weights_with_integration_fixed": boundary,
        "security_weight_transfer_to_tie": weights[0] - boundary[0],
    }

    # E04: An ordinal order does not fix the spacing of value levels.
    ordinal_a, ordinal_b = (5, 1), (3, 4)
    equal_weights = (F("0.5"), F("0.5"))
    recode = {1: F(0), 2: F("0.1"), 3: F("0.2"), 4: F("0.3"), 5: F(1)}
    raw = (dot(ordinal_a, equal_weights), dot(ordinal_b, equal_weights))
    recoded = (dot(tuple(recode[v] for v in ordinal_a), equal_weights), dot(tuple(recode[v] for v in ordinal_b), equal_weights))
    assert raw[0] < raw[1] and recoded[0] > recoded[1]
    results["E04_ordinal_spacing"] = {"raw_scores": raw, "recoded_scores": recoded, "winner_changes": True}

    # E05: Recomputing min/max from candidates can reverse A vs B.
    options = {"A": (8, 2), "B": (6, 6)}
    two_weights = (F("0.6"), F("0.4"))
    before = relative_scores(options, two_weights)
    after = relative_scores({**options, "C": (0, 5)}, two_weights)
    assert all(x >= y for x, y in zip(options["B"], (0, 5)))
    assert before["A"] > before["B"] and after["A"] < after["B"]
    fixed = {name: dot((F(row[0], 8), F(row[1] - 2, 4)), two_weights) for name, row in options.items()}
    assert fixed["A"] < fixed["B"]
    results["E05_candidate_normalization"] = {"before": before, "after_adding_dominated_C": after, "fixed_anchor_scores": fixed}

    # E06: Joint weight changes obey both bounds and the sum constraint.
    narrow = ((F("0.36"), F("0.44")), (F("0.31"), F("0.39")), (F("0.21"), F("0.29")))
    wide = ((F("0.25"), F("0.45")), (F("0.30"), F("0.40")), (F("0.20"), F("0.40")))
    narrow_range, wide_range = margin_range(av, bv, narrow), margin_range(av, bv, wide)
    assert narrow_range == (F("0.035"), F("0.115"))
    assert wide_range == (F("-0.075"), F("0.125"))
    results["E06_exact_weight_regions"] = {
        "narrow_margin_range_A_minus_B": narrow_range,
        "wide_margin_range_A_minus_B": wide_range,
        "narrow_A_is_strict_winner_everywhere": True,
        "wide_winner_changes": True,
    }

    # E07: Dominance may yield a score tie if improvements have zero weight.
    dominant, dominated = (1, 1), (1, 0)
    assert dot(dominant, (F(1), F(0))) == dot(dominated, (F(1), F(0)))
    results["E07_dominance_zero_weight"] = {"strict_raw_dominance": True, "weighted_scores_tie": True}

    # E08: A large soft score cannot compensate for a hard failure.
    candidates = {"A": {"passes": False, "score": F("0.95")}, "B": {"passes": True, "score": F("0.6")}}
    feasible = {name: info for name, info in candidates.items() if info["passes"]}
    chosen = max(feasible, key=lambda name: feasible[name]["score"])
    assert chosen == "B"
    results["E08_hard_gate"] = {"winner_after_gate": chosen, "infeasible_A_has_higher_soft_score": True}
    return results


def serialize(value):
    if isinstance(value, F):
        return {"exact": str(value), "decimal": float(value)}
    raise TypeError(f"Unsupported value: {type(value)}")


if __name__ == "__main__":
    examples = run_examples()
    report = {
        "status": "passed",
        "example_count": len(examples),
        "scope": "Synthetic exact-arithmetic examples only; no catalog validation or user study.",
        "examples": examples,
    }
    output = Path(__file__).with_name("complete-kb-check-results.json")
    output.write_text(json.dumps(report, default=serialize, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Passed {len(examples)} synthetic examples; results: {output.name}")
