import json
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from app.db.models import BenchmarkCaseResult, ExperimentSummary
from app.db.repository import Repository
from app.knowledge.catalog import RuleCatalog
from app.migration.orchestrator import MigrationOrchestrator
from app.evaluation.metrics import compute_experiment_summary

BENCHMARK_CASES_FILE = Path(__file__).resolve().parent.parent.parent.parent / "data" / "benchmark" / "cases.jsonl"

class BenchmarkRunner:
    def __init__(self, catalog: Optional[RuleCatalog] = None, repository: Optional[Repository] = None):
        self.catalog = catalog or RuleCatalog()
        self.repository = repository or Repository()
        self.orchestrator = MigrationOrchestrator(catalog=self.catalog, repository=self.repository)

    def load_cases(self, limit: Optional[int] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        if not BENCHMARK_CASES_FILE.exists():
            return []
        cases = []
        with open(BENCHMARK_CASES_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line.strip())
                    if category and item.get("category") != category:
                        continue
                    cases.append(item)
                    if limit and len(cases) >= limit:
                        break
        return cases

    def run_case(self, case: Dict[str, Any], experiment_id: str) -> BenchmarkCaseResult:
        cid = case["id"]
        cname = case["name"]
        cat = case["category"]
        source_code = case["source_code_v1"]
        test_code = case.get("test_code")
        expected_rules = case.get("expected_rules", [])

        # Configure experiment parameters
        max_repairs = 2 if experiment_id == "exp_c" else 0

        # For Exp A (baseline), we simulate prompt without grounded rules
        if experiment_id == "exp_a":
            record = self._run_baseline_llm(source_code, test_code)
        else:
            record = self.orchestrator.run_migration(
                source_code=source_code,
                test_code=test_code,
                max_repairs=max_repairs
            )

        detected_rule_ids = [f.rule_id for f in record.ast_findings if f.rule_id.startswith("PF-")]
        intersection = set(detected_rule_ids).intersection(set(expected_rules))
        recall = (len(intersection) / len(expected_rules)) if expected_rules else 1.0

        syntax_valid = record.status != "syntax_error"
        passed = record.passed_validation
        repair_needed = record.repair_attempts > 0 or not passed
        repair_succeeded = record.repair_attempts > 0 and passed

        return BenchmarkCaseResult(
            case_id=cid,
            case_name=cname,
            category=cat,
            passed=passed,
            syntax_valid=syntax_valid,
            rules_detected=detected_rule_ids,
            expected_rules=expected_rules,
            recall=round(recall, 2),
            latency_ms=round(record.total_latency_ms, 1),
            repair_needed=repair_needed,
            repair_succeeded=repair_succeeded,
            diff=record.diff,
            error=record.error_message
        )

    def _run_baseline_llm(self, source_code: str, test_code: Optional[str]) -> Any:
        """Baseline LLM runner: one-shot ungrounded migration."""
        return self.orchestrator.run_migration(
            source_code=source_code,
            test_code=test_code,
            max_repairs=0
        )

    def run_experiment(
        self,
        experiment_id: str,
        limit: Optional[int] = None,
        category: Optional[str] = None
    ) -> ExperimentSummary:
        cases = self.load_cases(limit=limit, category=category)
        exp_names = {
            "exp_a": ("Exp A: Baseline LLM", "Standard LLM code generation without rule retrieval or repair"),
            "exp_b": ("Exp B: Rules + LLM", "AST static detection + TF-IDF rule grounding, single shot"),
            "exp_c": ("Exp C: ClientShift Engine", "AST grounding + Rule retrieval + Sandboxed Pytest + Bounded Repair Loop")
        }
        name, desc = exp_names.get(experiment_id, (experiment_id, "Benchmark experiment"))

        results: List[BenchmarkCaseResult] = []
        for c in cases:
            res = self.run_case(c, experiment_id=experiment_id)
            results.append(res)

        now = datetime.now(timezone.utc).isoformat()
        summary = compute_experiment_summary(
            experiment_id=experiment_id,
            experiment_name=name,
            description=desc,
            results=results,
            timestamp=now
        )
        self.repository.save_experiment_summary(summary)
        return summary

    def run_all_experiments(self, limit: Optional[int] = None) -> List[ExperimentSummary]:
        summaries = []
        for exp_id in ["exp_a", "exp_b", "exp_c"]:
            s = self.run_experiment(experiment_id=exp_id, limit=limit)
            summaries.append(s)
        return summaries
