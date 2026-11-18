import pytest
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.analyzer.ast_parser import ParsedSource
from app.analyzer.detector import ASTDetector
from app.knowledge.catalog import RuleCatalog
from app.knowledge.retriever import RuleRetriever
from app.llm.provider import MockProvider
from app.validation.syntax import validate_syntax
from app.validation.test_runner import PytestRunner
from app.migration.orchestrator import MigrationOrchestrator
from app.migration.patcher import DiffPatcher

def test_ast_parser_and_detector():
    code = """
from payflow.client import PayFlowClient
from payflow.exceptions import PayFlowError

def charge_user(key, val):
    try:
        client = PayFlowClient(apiKey=key)
        return client.charge.create(amount_cents=val)
    except PayFlowError as e:
        return None
"""
    parsed = ParsedSource(code)
    assert parsed.syntax_error is None
    assert len(parsed.calls) >= 2
    assert len(parsed.imports) >= 2
    assert len(parsed.except_handlers) >= 1

    detector = ASTDetector()
    findings = detector.detect(parsed)
    rule_ids = [f.rule_id for f in findings]

    assert "PF-001" in rule_ids  # charge.create
    assert "PF-002" in rule_ids  # amount_cents and missing currency
    assert "PF-003" in rule_ids  # PayFlowError import and except
    assert "PF-004" in rule_ids  # PayFlowClient(apiKey=...)

def test_catalog_and_retriever():
    catalog = RuleCatalog()
    rules = catalog.get_all_rules()
    assert len(rules) >= 4
    assert catalog.get_rule("PF-001") is not None

    retriever = RuleRetriever(catalog)
    matches = retriever.retrieve("client.charge.create(amount_cents=100)")
    assert len(matches) > 0
    top_ids = [m.rule_id for m in matches]
    assert "PF-001" in top_ids or "PF-002" in top_ids

def test_syntax_validation():
    valid_code = "def foo():\n    return 42"
    invalid_code = "def foo(\n    return 42"
    assert validate_syntax(valid_code)[0] is True
    assert validate_syntax(invalid_code)[0] is False

def test_diff_patcher():
    orig = "def foo():\n    return 1"
    mig = "def foo():\n    return 2"
    diff = DiffPatcher.generate_unified_diff(orig, mig)
    assert "-    return 1" in diff
    assert "+    return 2" in diff
    stats = DiffPatcher.get_diff_stats(diff)
    assert stats["additions"] == 1
    assert stats["deletions"] == 1

def test_sandboxed_pytest_runner():
    migrated_code = """
from payflow.client import PayFlowClient
from payflow.config import ClientConfig

def process(key, val):
    c = PayFlowClient(config=ClientConfig(api_key=key))
    return c.payments.create(amount=val, currency="USD")
"""
    test_code = """
def test_process():
    from migrated_module import process
    res = process("key_test", 100)
    assert res["status"] == "succeeded"
    assert res["amount"] == 100
"""
    runner = PytestRunner(timeout_seconds=3.0)
    result = runner.run_validation(migrated_code, test_code)
    assert result.passed is True
    assert result.exit_code == 0

def test_orchestrator_end_to_end():
    source_code = """
from payflow.client import PayFlowClient

def bill(token, cost):
    c = PayFlowClient(apiKey=token)
    return c.charge.create(amount_cents=cost)
"""
    test_code = """
def test_bill():
    from migrated_module import bill
    res = bill("secret", 500)
    assert res["status"] == "succeeded"
    assert res["amount"] == 500
"""
    orchestrator = MigrationOrchestrator()
    record = orchestrator.run_migration(source_code=source_code, test_code=test_code)

    assert record.passed_validation is True
    assert record.status in ["success", "repaired"]
    assert len(record.stages) == 5
    assert "payments.create" in record.migrated_code
    assert "ClientConfig" in record.migrated_code
