from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.analyzer.ast_parser import ParsedSource
from app.analyzer.detector import ASTDetector
from app.knowledge.catalog import RuleCatalog
from app.knowledge.retriever import RuleRetriever
from app.migration.orchestrator import MigrationOrchestrator
from app.db.models import MigrationRunRecord, ASTEvidence, RuleMatch
from app.db.repository import Repository

router = APIRouter()

class AnalyzeRequest(BaseModel):
    source_code: str = Field(..., description="Python source code to analyze")

class AnalyzeResponse(BaseModel):
    ast_findings: List[ASTEvidence]
    matched_rules: List[RuleMatch]
    syntax_error: Optional[str] = None

class MigrateRequest(BaseModel):
    source_code: str = Field(..., description="Python source code to migrate")
    test_code: Optional[str] = Field(None, description="Pytest validation test code")
    max_repairs: int = Field(2, description="Maximum test-guided repair iterations")

catalog = RuleCatalog()
retriever = RuleRetriever(catalog)
detector = ASTDetector(catalog)
orchestrator = MigrationOrchestrator(catalog=catalog, retriever=retriever)
repository = Repository()

@router.get("/rules")
def get_rules():
    return [r.model_dump() for r in catalog.get_all_rules()]

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_code(req: AnalyzeRequest):
    parsed = ParsedSource(req.source_code)
    findings = detector.detect(parsed)
    rule_ids = [f.rule_id for f in findings if f.rule_id.startswith("PF-")]
    matched = retriever.retrieve(code=req.source_code, ast_detected_rule_ids=rule_ids, top_k=6)
    return AnalyzeResponse(
        ast_findings=findings,
        matched_rules=matched,
        syntax_error=parsed.syntax_error
    )

@router.post("/migrate", response_model=MigrationRunRecord)
def migrate_code(req: MigrateRequest):
    if not req.source_code.strip():
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")
    record = orchestrator.run_migration(
        source_code=req.source_code,
        test_code=req.test_code,
        max_repairs=req.max_repairs
    )
    return record

@router.get("/migrations", response_model=List[MigrationRunRecord])
def list_migrations(limit: int = 30):
    return repository.list_migration_runs(limit=limit)

@router.get("/migrations/{run_id}", response_model=MigrationRunRecord)
def get_migration(run_id: str):
    record = repository.get_migration_run(run_id)
    if not record:
        raise HTTPException(status_code=404, detail="Migration run not found.")
    return record
