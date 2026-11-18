import time
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from app.analyzer.ast_parser import ParsedSource
from app.analyzer.detector import ASTDetector
from app.knowledge.catalog import RuleCatalog
from app.knowledge.retriever import RuleRetriever
from app.llm.planner import MigrationPlanner
from app.migration.patcher import DiffPatcher
from app.validation.syntax import validate_syntax
from app.validation.test_runner import PytestRunner
from app.db.models import (
    MigrationRunRecord,
    MigrationStageLog,
    ASTEvidence,
    RuleMatch,
    PytestOutput
)
from app.db.repository import Repository

class MigrationOrchestrator:
    def __init__(
        self,
        catalog: Optional[RuleCatalog] = None,
        retriever: Optional[RuleRetriever] = None,
        planner: Optional[MigrationPlanner] = None,
        test_runner: Optional[PytestRunner] = None,
        repository: Optional[Repository] = None
    ):
        self.catalog = catalog or RuleCatalog()
        self.retriever = retriever or RuleRetriever(self.catalog)
        self.detector = ASTDetector(self.catalog)
        self.planner = planner or MigrationPlanner()
        self.test_runner = test_runner or PytestRunner()
        self.repository = repository or Repository()

    def run_migration(
        self,
        source_code: str,
        test_code: Optional[str] = None,
        max_repairs: int = 2
    ) -> MigrationRunRecord:
        run_id = f"mig_{uuid.uuid4().hex[:10]}"
        start_time = time.time()
        stages: List[MigrationStageLog] = []

        # =========================================================
        # Stage 1: AST Analysis
        # =========================================================
        s1_start = time.time()
        parsed = ParsedSource(source_code)
        ast_findings: List[ASTEvidence] = self.detector.detect(parsed)
        s1_latency = (time.time() - s1_start) * 1000

        stages.append(
            MigrationStageLog(
                stage_number=1,
                stage_name="AST Analysis",
                status="completed" if not parsed.syntax_error else "failed",
                latency_ms=round(s1_latency, 2),
                details={
                    "findings_count": len(ast_findings),
                    "syntax_error": parsed.syntax_error,
                    "findings": [f.model_dump() for f in ast_findings]
                },
                message=f"Detected {len(ast_findings)} AST violation(s)" if not parsed.syntax_error else f"Source syntax error: {parsed.syntax_error}"
            )
        )

        # =========================================================
        # Stage 2: Rule Retrieval
        # =========================================================
        s2_start = time.time()
        detected_rule_ids = [f.rule_id for f in ast_findings if f.rule_id.startswith("PF-")]
        matched_rules: List[RuleMatch] = self.retriever.retrieve(
            code=source_code,
            ast_detected_rule_ids=detected_rule_ids,
            top_k=6
        )
        s2_latency = (time.time() - s2_start) * 1000

        stages.append(
            MigrationStageLog(
                stage_number=2,
                stage_name="Rule Retrieval",
                status="completed",
                latency_ms=round(s2_latency, 2),
                details={
                    "matched_count": len(matched_rules),
                    "rules": [r.model_dump() for r in matched_rules]
                },
                message=f"Retrieved {len(matched_rules)} relevant catalog rule(s)"
            )
        )

        # =========================================================
        # Stage 3: AI Plan
        # =========================================================
        s3_start = time.time()
        plan = self.planner.plan_migration(
            source_code=source_code,
            ast_findings=ast_findings,
            matched_rules=matched_rules
        )
        s3_latency = (time.time() - s3_start) * 1000
        candidate_code = plan.migrated_code

        stages.append(
            MigrationStageLog(
                stage_number=3,
                stage_name="AI Plan",
                status="completed",
                latency_ms=round(s3_latency, 2),
                details={
                    "rules_applied": plan.rules_applied,
                    "reasoning": plan.reasoning,
                    "explanation": plan.explanation
                },
                message=f"Plan generated applying {len(plan.rules_applied)} rule(s)"
            )
        )

        # =========================================================
        # Stage 4: Diff Patch & Syntax Verification
        # =========================================================
        s4_start = time.time()
        diff = DiffPatcher.generate_unified_diff(source_code, candidate_code)
        syntax_ok, syntax_err, err_line = validate_syntax(candidate_code)
        s4_latency = (time.time() - s4_start) * 1000

        stages.append(
            MigrationStageLog(
                stage_number=4,
                stage_name="Diff Patch",
                status="completed" if syntax_ok else "failed",
                latency_ms=round(s4_latency, 2),
                details={
                    "diff_stats": DiffPatcher.get_diff_stats(diff),
                    "syntax_valid": syntax_ok,
                    "syntax_error": syntax_err
                },
                message="Patch generated and syntax verified" if syntax_ok else f"Syntax check failed: {syntax_err}"
            )
        )

        # =========================================================
        # Stage 5: Sandbox Pytest Validation & Bounded Repair
        # =========================================================
        s5_start = time.time()
        pytest_result: Optional[PytestOutput] = None
        repair_attempts = 0
        current_code = candidate_code

        # Initial validation attempt
        if syntax_ok:
            pytest_result = self.test_runner.run_validation(current_code, test_code)
        else:
            pytest_result = PytestOutput(
                exit_code=1,
                passed=False,
                summary="Aborted sandbox: candidate code contains syntax errors",
                stdout="",
                stderr=syntax_err or "Syntax Error",
                failure_details=syntax_err
            )

        # Bounded repair loop if initial validation failed
        while (not pytest_result or not pytest_result.passed) and (repair_attempts < max_repairs):
            repair_attempts += 1
            error_to_feed = (
                syntax_err
                if not syntax_ok
                else (pytest_result.failure_details or pytest_result.stderr or pytest_result.stdout)
            )

            # Invoke repair planner
            repaired_plan = self.planner.repair_migration(
                source_code=source_code,
                failed_migrated_code=current_code,
                error_message=error_to_feed,
                matched_rules=matched_rules
            )
            current_code = repaired_plan.migrated_code
            plan.rules_applied = list(set(plan.rules_applied + repaired_plan.rules_applied))

            # Re-verify syntax
            syntax_ok, syntax_err, _ = validate_syntax(current_code)
            diff = DiffPatcher.generate_unified_diff(source_code, current_code)

            if syntax_ok:
                pytest_result = self.test_runner.run_validation(current_code, test_code)
            else:
                pytest_result = PytestOutput(
                    exit_code=1,
                    passed=False,
                    summary=f"Repair attempt {repair_attempts} failed syntax",
                    stdout="",
                    stderr=syntax_err or "Syntax error in repair",
                    failure_details=syntax_err
                )

            if pytest_result and pytest_result.passed:
                break

        s5_latency = (time.time() - s5_start) * 1000
        passed = bool(pytest_result and pytest_result.passed)

        stage5_msg = (
            f"Pytest passed with exit code 0"
            if passed and repair_attempts == 0
            else f"Pytest passed after {repair_attempts} repair loop(s)"
            if passed
            else f"Validation failed after {repair_attempts} repair attempt(s)"
        )

        stages.append(
            MigrationStageLog(
                stage_number=5,
                stage_name="Sandbox Pytest",
                status="completed" if passed else "failed",
                latency_ms=round(s5_latency, 2),
                details={
                    "passed": passed,
                    "exit_code": pytest_result.exit_code if pytest_result else -1,
                    "repair_attempts": repair_attempts,
                    "summary": pytest_result.summary if pytest_result else "No result",
                    "failure_details": pytest_result.failure_details if pytest_result else None
                },
                message=stage5_msg
            )
        )

        total_latency = (time.time() - start_time) * 1000

        # Determine overall status
        if passed and repair_attempts == 0:
            status = "success"
        elif passed and repair_attempts > 0:
            status = "repaired"
        elif not syntax_ok:
            status = "syntax_error"
        else:
            status = "failed"

        record = MigrationRunRecord(
            id=run_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            source_code=source_code,
            migrated_code=current_code,
            diff=diff,
            status=status,
            passed_validation=passed,
            repair_attempts=repair_attempts,
            total_latency_ms=round(total_latency, 2),
            ast_findings=ast_findings,
            stages=stages,
            pytest_result=pytest_result,
            rules_applied=plan.rules_applied,
            error_message=pytest_result.failure_details if (pytest_result and not passed) else None
        )

        self.repository.save_migration_run(record)
        return record
