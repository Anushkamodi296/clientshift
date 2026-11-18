import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from app.db.models import MigrationRunRecord, ExperimentSummary, BenchmarkCaseResult, UserProfile, UserStats

DB_PATH = Path(__file__).resolve().parent.parent.parent / "clientshift.db"

class Repository:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS migration_runs (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    source_code TEXT NOT NULL,
                    migrated_code TEXT NOT NULL,
                    diff TEXT NOT NULL,
                    status TEXT NOT NULL,
                    passed_validation INTEGER NOT NULL,
                    repair_attempts INTEGER NOT NULL,
                    total_latency_ms REAL NOT NULL,
                    ast_findings TEXT NOT NULL,
                    stages TEXT NOT NULL,
                    pytest_result TEXT,
                    rules_applied TEXT NOT NULL,
                    error_message TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_summaries (
                    experiment_id TEXT PRIMARY KEY,
                    experiment_name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    total_cases INTEGER NOT NULL,
                    passed_cases INTEGER NOT NULL,
                    pass_rate REAL NOT NULL,
                    syntax_rate REAL NOT NULL,
                    rule_recall REAL NOT NULL,
                    avg_latency_ms REAL NOT NULL,
                    repair_success_rate REAL NOT NULL,
                    category_breakdown TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_case_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_id TEXT NOT NULL,
                    case_id TEXT NOT NULL,
                    case_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    passed INTEGER NOT NULL,
                    syntax_valid INTEGER NOT NULL,
                    rules_detected TEXT NOT NULL,
                    expected_rules TEXT NOT NULL,
                    recall REAL NOT NULL,
                    latency_ms REAL NOT NULL,
                    repair_needed INTEGER NOT NULL,
                    repair_succeeded INTEGER NOT NULL,
                    diff TEXT NOT NULL,
                    error TEXT,
                    run_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    avatar_url TEXT,
                    password_hash TEXT,
                    provider TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_migration_run(self, record: MigrationRunRecord):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO migration_runs (
                    id, created_at, source_code, migrated_code, diff, status,
                    passed_validation, repair_attempts, total_latency_ms,
                    ast_findings, stages, pytest_result, rules_applied, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.id,
                record.created_at,
                record.source_code,
                record.migrated_code,
                record.diff,
                record.status,
                1 if record.passed_validation else 0,
                record.repair_attempts,
                record.total_latency_ms,
                json.dumps([f.model_dump() for f in record.ast_findings]),
                json.dumps([s.model_dump() for s in record.stages]),
                json.dumps(record.pytest_result.model_dump()) if record.pytest_result else None,
                json.dumps(record.rules_applied),
                record.error_message
            ))
            conn.commit()

    def get_migration_run(self, run_id: str) -> Optional[MigrationRunRecord]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM migration_runs WHERE id = ?", (run_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_record(row)

    def list_migration_runs(self, limit: int = 50) -> List[MigrationRunRecord]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM migration_runs ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [self._row_to_record(row) for row in rows]

    def _row_to_record(self, row: sqlite3.Row) -> MigrationRunRecord:
        pytest_raw = row["pytest_result"]
        pytest_obj = json.loads(pytest_raw) if pytest_raw else None
        return MigrationRunRecord(
            id=row["id"],
            created_at=row["created_at"],
            source_code=row["source_code"],
            migrated_code=row["migrated_code"],
            diff=row["diff"],
            status=row["status"],
            passed_validation=bool(row["passed_validation"]),
            repair_attempts=row["repair_attempts"],
            total_latency_ms=row["total_latency_ms"],
            ast_findings=json.loads(row["ast_findings"]),
            stages=json.loads(row["stages"]),
            pytest_result=pytest_obj,
            rules_applied=json.loads(row["rules_applied"]),
            error_message=row["error_message"]
        )

    def save_experiment_summary(self, summary: ExperimentSummary):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO benchmark_summaries (
                    experiment_id, experiment_name, description, total_cases,
                    passed_cases, pass_rate, syntax_rate, rule_recall,
                    avg_latency_ms, repair_success_rate, category_breakdown, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                summary.experiment_id,
                summary.experiment_name,
                summary.description,
                summary.total_cases,
                summary.passed_cases,
                summary.pass_rate,
                summary.syntax_rate,
                summary.rule_recall,
                summary.avg_latency_ms,
                summary.repair_success_rate,
                json.dumps(summary.category_breakdown),
                summary.timestamp
            ))
            conn.commit()

    def get_all_experiment_summaries(self) -> List[ExperimentSummary]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM benchmark_summaries")
            rows = cursor.fetchall()
            results = []
            for r in rows:
                results.append(ExperimentSummary(
                    experiment_id=r["experiment_id"],
                    experiment_name=r["experiment_name"],
                    description=r["description"],
                    total_cases=r["total_cases"],
                    passed_cases=r["passed_cases"],
                    pass_rate=r["pass_rate"],
                    syntax_rate=r["syntax_rate"],
                    rule_recall=r["rule_recall"],
                    avg_latency_ms=r["avg_latency_ms"],
                    repair_success_rate=r["repair_success_rate"],
                    category_breakdown=json.loads(r["category_breakdown"]),
                    timestamp=r["timestamp"]
                ))
            return results

    def create_user(
        self,
        user_id: str,
        email: str,
        full_name: str,
        password_hash: Optional[str],
        provider: str,
        avatar_url: Optional[str],
        created_at: str
    ) -> UserProfile:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO users (
                    id, email, full_name, avatar_url, password_hash, provider, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, email, full_name, avatar_url, password_hash, provider, created_at))
            conn.commit()
        return UserProfile(
            id=user_id,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
            provider=provider,
            created_at=created_at
        )

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            if not row:
                return None
            return dict(row)

    def get_user_by_id(self, user_id: str) -> Optional[UserProfile]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return UserProfile(
                id=row["id"],
                email=row["email"],
                full_name=row["full_name"],
                avatar_url=row["avatar_url"],
                provider=row["provider"],
                created_at=row["created_at"]
            )

    def get_user_stats(self, user_id: str) -> UserStats:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count, SUM(passed_validation) as passed FROM migration_runs")
            row = cursor.fetchone()
            total_migrations = row["count"] if row and row["count"] else 0
            passed = row["passed"] if row and row["passed"] else 0
            pass_rate = round((passed / total_migrations * 100), 1) if total_migrations > 0 else 100.0

            cursor.execute("SELECT COUNT(*) as count FROM benchmark_summaries")
            b_row = cursor.fetchone()
            benchmarks = b_row["count"] if b_row and b_row["count"] else 3

            return UserStats(
                saved_migrations=total_migrations,
                benchmark_runs=benchmarks,
                success_rate=pass_rate
            )
