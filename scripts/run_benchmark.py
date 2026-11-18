import sys
import json
import argparse
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Add backend directory to path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.evaluation.benchmark import BenchmarkRunner

def main():
    parser = argparse.ArgumentParser(description="ClientShift-MiniBench Benchmark Harness")
    parser.add_argument("--experiment", choices=["all", "exp_a", "exp_b", "exp_c"], default="all", help="Experiment to run")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of test cases")
    parser.add_argument("--category", type=str, default=None, help="Filter by specific category")
    parser.add_argument("--output", type=str, default=None, help="Path to write JSON results")
    args = parser.parse_args()

    runner = BenchmarkRunner()
    print("=" * 70)
    print("🚀 CLIENTSHIFT-MINIBENCH BENCHMARK SUITE")
    print("Deterministic Evaluation of AI Code Migration Across SDK Breaking Versions")
    print("=" * 70)

    if args.experiment == "all":
        summaries = runner.run_all_experiments(limit=args.limit)
    else:
        summaries = [runner.run_experiment(experiment_id=args.experiment, limit=args.limit, category=args.category)]

    print("\n" + "=" * 70)
    print(f"{'Experiment':<28} | {'Pass %':<8} | {'Syntax %':<8} | {'Recall %':<8} | {'Latency':<9} | {'Repair %'}")
    print("-" * 70)
    for s in summaries:
        print(f"{s.experiment_name:<28} | {s.pass_rate:>6.1f}% | {s.syntax_rate:>6.1f}% | {s.rule_recall:>6.1f}% | {s.avg_latency_ms:>6.1f}ms | {s.repair_success_rate:>6.1f}%")
    print("=" * 70)

    # Category breakdown for Exp C
    exp_c = next((s for s in summaries if s.experiment_id == "exp_c"), None)
    if exp_c and exp_c.category_breakdown:
        print("\n📊 CATEGORY BREAKDOWN (ClientShift Engine - Exp C):")
        print(f"{'Category':<25} | {'Cases':<6} | {'Pass %':<8} | {'Recall %':<8} | {'Avg Latency'}")
        print("-" * 65)
        for cat, metrics in exp_c.category_breakdown.items():
            print(f"{cat:<25} | {int(metrics['total']):<6} | {metrics['pass_rate']:>6.1f}% | {metrics['recall']:>6.1f}% | {metrics['avg_latency_ms']:>6.1f}ms")
        print("-" * 65)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump([s.model_dump() for s in summaries], f, indent=2)
        print(f"\nSaved benchmark results to {out_path}")

if __name__ == "__main__":
    main()
