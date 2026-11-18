import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class MigrationRule(BaseModel):
    id: str
    name: str
    category: str
    severity: str
    description: str
    v1_pattern: str
    v2_pattern: str
    ast_match_criteria: Dict[str, Any]
    code_example_before: str
    code_example_after: str
    fix_strategy: str

class RuleCatalog:
    def __init__(self, catalog_path: Optional[Path] = None):
        if catalog_path is None:
            # Default to data/migration_rules/payflow_v1_to_v2.json
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            catalog_path = base_dir / "data" / "migration_rules" / "payflow_v1_to_v2.json"
        self.catalog_path = catalog_path
        self._rules: Dict[str, MigrationRule] = {}
        self.load()

    def load(self):
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog file not found at: {self.catalog_path}")
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                rule = MigrationRule(**item)
                self._rules[rule.id] = rule

    def get_rule(self, rule_id: str) -> Optional[MigrationRule]:
        return self._rules.get(rule_id)

    def get_all_rules(self) -> List[MigrationRule]:
        return list(self._rules.values())

    def get_rules_by_category(self, category: str) -> List[MigrationRule]:
        return [r for r in self._rules.values() if r.category == category]
