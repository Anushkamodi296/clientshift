import json
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.llm.provider import LLMProvider, get_llm_provider
from app.llm.prompts import (
    MIGRATION_SYSTEM_PROMPT,
    build_migration_prompt,
    build_repair_prompt
)
from app.db.models import ASTEvidence, RuleMatch

class MigrationPlanSchema(BaseModel):
    reasoning: str = Field(description="Step-by-step technical explanation")
    migrated_code: str = Field(description="The complete migrated source code")
    rules_applied: List[str] = Field(default_factory=list, description="IDs of rules applied, e.g. PF-001")
    explanation: str = Field(default="", description="Summary explanation for user")

class MigrationPlanner:
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or get_llm_provider()

    def plan_migration(
        self,
        source_code: str,
        ast_findings: List[ASTEvidence],
        matched_rules: List[RuleMatch]
    ) -> MigrationPlanSchema:
        findings_payload = [f.model_dump() for f in ast_findings]
        rules_payload = [r.model_dump() for r in matched_rules]

        prompt = build_migration_prompt(
            source_code=source_code,
            ast_findings=findings_payload,
            rules=rules_payload
        )

        raw_resp = self.provider.generate(prompt=prompt, system=MIGRATION_SYSTEM_PROMPT)
        return self._parse_and_validate(raw_resp, fallback_code=source_code)

    def repair_migration(
        self,
        source_code: str,
        failed_migrated_code: str,
        error_message: str,
        matched_rules: List[RuleMatch]
    ) -> MigrationPlanSchema:
        rules_payload = [r.model_dump() for r in matched_rules]
        prompt = build_repair_prompt(
            source_code=source_code,
            failed_migrated_code=failed_migrated_code,
            error_message=error_message,
            rules=rules_payload
        )
        raw_resp = self.provider.generate(prompt=prompt, system=MIGRATION_SYSTEM_PROMPT)
        return self._parse_and_validate(raw_resp, fallback_code=failed_migrated_code)

    def _parse_and_validate(self, raw_resp: str, fallback_code: str) -> MigrationPlanSchema:
        clean = raw_resp.strip()

        # Extract JSON if enclosed in markdown blocks
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean, re.DOTALL)
        if json_match:
            clean = json_match.group(1).strip()
        elif "{" in clean and "}" in clean:
            start = clean.find("{")
            end = clean.rfind("}") + 1
            clean = clean[start:end]

        try:
            data = json.loads(clean)
            return MigrationPlanSchema(**data)
        except Exception:
            # Fallback if raw response could not be parsed as JSON
            return MigrationPlanSchema(
                reasoning="Failed to parse structured JSON from model; fallback returned.",
                migrated_code=fallback_code,
                rules_applied=[],
                explanation="Model response was not valid JSON."
            )
