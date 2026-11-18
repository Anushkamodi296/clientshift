from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class RuleMatch(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    severity: str
    score: float
    description: str

class ASTEvidence(BaseModel):
    rule_id: str
    rule_name: str
    line_number: int
    col_offset: int
    end_line_number: Optional[int] = None
    node_type: str
    snippet: str
    evidence_text: str
    risk_level: str  # "HIGH", "MEDIUM", "LOW"
    recommended_fix: str

class MigrationStageLog(BaseModel):
    stage_number: int
    stage_name: str
    status: str  # "completed", "failed", "skipped"
    latency_ms: float
    details: Dict[str, Any] = Field(default_factory=dict)
    message: str

class PytestOutput(BaseModel):
    exit_code: int
    passed: bool
    summary: str
    stdout: str
    stderr: str
    tests_run: int = 1
    duration_s: float = 0.0
    failure_details: Optional[str] = None

class MigrationRunRecord(BaseModel):
    id: str
    created_at: str
    source_code: str
    migrated_code: str
    diff: str
    status: str  # "success", "repaired", "failed", "syntax_error"
    passed_validation: bool
    repair_attempts: int
    total_latency_ms: float
    ast_findings: List[ASTEvidence] = Field(default_factory=list)
    stages: List[MigrationStageLog] = Field(default_factory=list)
    pytest_result: Optional[PytestOutput] = None
    rules_applied: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None

class BenchmarkCaseResult(BaseModel):
    case_id: str
    case_name: str
    category: str
    passed: bool
    syntax_valid: bool
    rules_detected: List[str]
    expected_rules: List[str]
    recall: float
    latency_ms: float
    repair_needed: bool
    repair_succeeded: bool
    diff: str
    error: Optional[str] = None

class ExperimentSummary(BaseModel):
    experiment_id: str  # "exp_a", "exp_b", "exp_c"
    experiment_name: str
    description: str
    total_cases: int
    passed_cases: int
    pass_rate: float
    syntax_rate: float
    rule_recall: float
    avg_latency_ms: float
    repair_success_rate: float
    category_breakdown: Dict[str, Dict[str, float]]
    timestamp: str

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    provider: str = "local"
    created_at: str

class UserStats(BaseModel):
    saved_migrations: int = 0
    benchmark_runs: int = 0
    success_rate: float = 100.0

class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile
    stats: UserStats

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: str

class GoogleAuthRequest(BaseModel):
    credential: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
