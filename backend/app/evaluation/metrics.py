from typing import List, Dict, Any
from app.db.models import BenchmarkCaseResult, ExperimentSummary

def compute_experiment_summary(
    experiment_id: str,
    experiment_name: str,
    description: str,
    results: List[BenchmarkCaseResult],
    timestamp: str
) -> ExperimentSummary:
    total = len(results)
    if total == 0:
        return ExperimentSummary(
            experiment_id=experiment_id,
            experiment_name=experiment_name,
            description=description,
            total_cases=0,
            passed_cases=0,
            pass_rate=0.0,
            syntax_rate=0.0,
            rule_recall=0.0,
            avg_latency_ms=0.0,
            repair_success_rate=0.0,
            category_breakdown={},
            timestamp=timestamp
        )

    passed = sum(1 for r in results if r.passed)
    syntax_ok = sum(1 for r in results if r.syntax_valid)
    total_recall = sum(r.recall for r in results)
    total_latency = sum(r.latency_ms for r in results)

    # Repair success rate
    repair_needed_count = sum(1 for r in results if r.repair_needed)
    repair_success_count = sum(1 for r in results if r.repair_succeeded)
    repair_rate = (repair_success_count / repair_needed_count * 100) if repair_needed_count > 0 else 100.0

    # Category breakdown
    categories: Dict[str, List[BenchmarkCaseResult]] = {}
    for r in results:
        categories.setdefault(r.category, []).append(r)

    category_breakdown: Dict[str, Dict[str, float]] = {}
    for cat, cat_results in categories.items():
        c_tot = len(cat_results)
        c_pass = sum(1 for cr in cat_results if cr.passed)
        c_syn = sum(1 for cr in cat_results if cr.syntax_valid)
        c_rec = sum(cr.recall for cr in cat_results) / c_tot if c_tot > 0 else 0.0
        c_lat = sum(cr.latency_ms for cr in cat_results) / c_tot if c_tot > 0 else 0.0
        category_breakdown[cat] = {
            "total": float(c_tot),
            "passed": float(c_pass),
            "pass_rate": round(c_pass / c_tot * 100, 1) if c_tot > 0 else 0.0,
            "syntax_rate": round(c_syn / c_tot * 100, 1) if c_tot > 0 else 0.0,
            "recall": round(c_rec * 100, 1),
            "avg_latency_ms": round(c_lat, 1)
        }

    return ExperimentSummary(
        experiment_id=experiment_id,
        experiment_name=experiment_name,
        description=description,
        total_cases=total,
        passed_cases=passed,
        pass_rate=round(passed / total * 100, 1),
        syntax_rate=round(syntax_ok / total * 100, 1),
        rule_recall=round(total_recall / total * 100, 1),
        avg_latency_ms=round(total_latency / total, 1),
        repair_success_rate=round(repair_rate, 1),
        category_breakdown=category_breakdown,
        timestamp=timestamp
    )
