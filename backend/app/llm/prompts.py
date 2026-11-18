from typing import List, Dict, Any

MIGRATION_SYSTEM_PROMPT = """You are ClientShift, a deterministic Senior AI Code Migration Engineer specializing in Python SDK modernization.
Your objective is to produce mathematically precise, syntactically flawless migrated code that passes AST verification and Pytest validation.
Rules:
1. Always preserve variable names, business logic, comments, and docstrings.
2. Only modify AST nodes matching the breaking migration catalog rules.
3. Your response MUST be valid JSON adhering strictly to the requested schema. No conversational filler outside JSON.
"""

def build_migration_prompt(
    source_code: str,
    ast_findings: List[Dict[str, Any]],
    rules: List[Dict[str, Any]]
) -> str:
    findings_str = "\n".join([
        f"- [Line {f.get('line_number')}] Rule {f.get('rule_id')} ({f.get('rule_name')}): {f.get('evidence_text')}"
        for f in ast_findings
    ]) if ast_findings else "No deterministic AST violations flagged."

    rules_str = "\n\n".join([
        f"Rule ID: {r.get('id')} ({r.get('name')})\nDescription: {r.get('description')}\nBefore: {r.get('v1_pattern')}\nAfter: {r.get('v2_pattern')}\nStrategy: {r.get('fix_strategy')}"
        for r in rules
    ])

    return f"""Please migrate the following Python source code according to the detected AST issues and SDK v2 breaking migration catalog rules.

### SOURCE CODE (V1):
```python
{source_code}
```

### DETECTED AST EVIDENCE:
{findings_str}

### SDK V2 RULES CATALOG CONTEXT:
{rules_str}

### REQUIRED JSON RESPONSE SCHEMA:
Respond with ONLY a raw JSON object formatted as follows:
{{
  "reasoning": "Step-by-step technical rationale explaining every modification made",
  "migrated_code": "The complete, syntactically valid migrated Python code in full",
  "rules_applied": ["PF-001", "PF-002"],
  "explanation": "Human-readable summary of SDK modernizations implemented"
}}
"""

def build_repair_prompt(
    source_code: str,
    failed_migrated_code: str,
    error_message: str,
    rules: List[Dict[str, Any]]
) -> str:
    rules_str = "\n".join([f"- {r.get('id')}: {r.get('name')}" for r in rules])
    return f"""A previously generated migration patch FAILED validation.
Analyze the test/syntax failure trace, identify the defect, and generate a repaired version.

### ORIGINAL V1 CODE:
```python
{source_code}
```

### DEFECTIVE MIGRATED CODE:
```python
{failed_migrated_code}
```

### VALIDATION ERROR LOG / TEST FAILURE:
```
{error_message}
```

### RELEVANT RULES:
{rules_str}

### REQUIRED JSON RESPONSE SCHEMA:
Respond with ONLY a raw JSON object formatted as follows:
{{
  "reasoning": "Root cause analysis of the test failure and exact correction strategy",
  "migrated_code": "The complete, corrected Python code",
  "rules_applied": ["PF-001"],
  "explanation": "Explanation of fix applied to resolve validation error"
}}
"""
