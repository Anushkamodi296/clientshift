from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.knowledge.catalog import RuleCatalog

router = APIRouter()
catalog = RuleCatalog()

class NiloChatRequest(BaseModel):
    message: str = Field(..., description="User prompt or question")
    code_context: Optional[str] = Field(None, description="Active code snippet in editor")
    error_context: Optional[str] = Field(None, description="Active validation error or pytest traceback")
    current_stage: Optional[str] = Field(None, description="Active stage in workspace")

class NiloChatResponse(BaseModel):
    reply: str
    suggested_actions: List[str]
    rule_references: List[str]

NILO_KNOWLEDGE = {
    "why did my patch fail validation?": """### 🔍 Nilo's Diagnostics: Why Validation Patches Fail

In ClientShift, deterministic AST verification and isolated Pytest execution decide whether a patch succeeds—not LLM hallucinations! Common culprits include:

1. **Missing Mandatory `currency="USD"`**:
   In PayFlow v2, `payments.create(...)` strictly rejects calls without an explicit `currency`. In v1, it defaulted silently.
2. **Missing `ClientConfig` Import**:
   `PayFlowClient` in v2 no longer accepts `apiKey="..."` directly. If you modernized to `PayFlowClient(config=ClientConfig(api_key=...))` but forgot `from payflow.config import ClientConfig`, Python throws `NameError`.
3. **Deprecated Exception Trapping**:
   If your code still catches `PayFlowError`, any runtime exception (`PayFlowAPIException`) will bubble uncaught, failing assertion tests.
4. **Subtle Signature Mismatches**:
   Calling `client.refunds.issue(charge_id=...)` will fail because v2 renamed the parameter to `payment_id`.

💡 **Pro-Tip**: Hit **Migrate & Validate** in the workspace with Repair Loop enabled! ClientShift's bounded repair loop automatically passes the traceback into the planner to patch the missing arguments.""",

    "explain payflow v2 breaking changes": """### ⚡ PayFlow SDK v1.0 ➔ v2.0 Architecture Changes

Here is the executive technical brief on the breaking changes:

| Rule ID | Legacy Pattern (v1.0) | Modern Pattern (v2.0) | Critical Severity |
| :--- | :--- | :--- | :--- |
| **PF-001** | `client.charge.create(...)` | `client.payments.create(...)` | 🚨 Breaking Rename |
| **PF-002** | `amount_cents=5000` | `amount=5000, currency="USD"` | 🚨 Mandatory Param |
| **PF-003** | `except PayFlowError:` | `except PayFlowAPIException:` | 🚨 Hierarchy Shift |
| **PF-004** | `PayFlowClient(apiKey="...")` | `PayFlowClient(config=ClientConfig(api_key="..."))` | 🚨 Config Object |
| **PF-005** | `customers.retrieve(id=...)` | `customers.get(customer_id=...)` | ⚠️ Method & Arg |
| **PF-006** | `refund.process(charge_id=...)`| `refunds.issue(payment_id=...)` | ⚠️ Pluralized Service |

Each of these changes is deterministically detected by ClientShift's AST parser before LLM invocation!""",

    "how to run local benchmark": """### 🏎️ Running ClientShift-MiniBench

ClientShift includes a 60-case synthetic benchmark across 6 categories comparing:
- **Exp A**: LLM-only Baseline
- **Exp B**: AST Rules + LLM Grounding
- **Exp C**: Full Engine with Test-Guided Repair Loops

#### Command-Line Execution:
```powershell
python scripts/run_benchmark.py --experiment all
```
Or run a fast evaluation:
```powershell
python scripts/run_benchmark.py --limit 12
```

#### GUI Execution:
Head over to the **Benchmark Explorer** tab in the top navigation bar! You can inspect individual test cases, run live comparative experiments, and view pass-rate deltas.""",

    "teach me ast analysis": """### 🧠 How Deterministic AST Analysis Works

Rather than having an LLM blindly guess which lines have breaking changes, ClientShift uses Python's built-in `ast` module to inspect the Abstract Syntax Tree:

```
Source Code
    │
    ▼  ast.parse()
AST Abstract Syntax Tree
    ├── ast.Import / ast.ImportFrom  ──> Check for 'PayFlowError'
    └── ast.Call                     ──> Check full callee chain
           ├── func: Attribute       ──> 'charge.create' -> PF-001
           └── keywords: keyword     ──> 'amount_cents' -> PF-002
```

#### Why AST First?
1. **Zero Hallucinations**: Exact line numbers, column offsets, and argument dictionaries.
2. **Grounding Context**: We inject only the rules that matched the AST into the model prompt.
3. **Speed**: Parsing takes ~1.2ms versus several seconds of unguided LLM reasoning!"""
}

@router.post("/chat", response_model=NiloChatResponse)
def nilo_chat(req: NiloChatRequest):
    msg_lower = req.message.lower().strip()

    # Check for direct quick action chip match
    for key, canned in NILO_KNOWLEDGE.items():
        if key in msg_lower or msg_lower in key:
            return NiloChatResponse(
                reply=canned,
                suggested_actions=["Inspect Workspace AST", "Run Benchmark", "View Migration Rules"],
                rule_references=["PF-001", "PF-002", "PF-003", "PF-004"]
            )

    # Contextual diagnosis if error trace provided
    if req.error_context and len(req.error_context.strip()) > 5:
        err = req.error_context
        reply = f"""### 🛠️ Nilo Diagnostic on Active Failure

I inspected the validation failure from your workspace:

> `{err.splitlines()[-1] if err.splitlines() else err}`

**Analysis & Root Cause**:
"""
        if "currency" in err.lower():
            reply += "\nYour `payments.create(...)` call lacks the mandatory `currency` parameter. Add `currency=\"USD\"` to satisfy Rule **PF-002**."
        elif "clientconfig" in err.lower() or "not defined" in err.lower():
            reply += "\nYou initialized `ClientConfig` without importing it. Add:\n```python\nfrom payflow.config import ClientConfig\n```"
        elif "payflowerror" in err.lower():
            reply += "\nThe runtime test raised `PayFlowAPIException` but your code caught `PayFlowError`. Modernize the `except` block to **PF-003**."
        else:
            reply += "\nThe test assertion or sandbox execution failed. Ensure your method renames (`charge.create` -> `payments.create`) and keyword arguments match the v2 specifications."

        return NiloChatResponse(
            reply=reply,
            suggested_actions=["Apply Auto-Fix", "View Unified Diff", "Re-run Pytest Sandbox"],
            rule_references=["PF-001", "PF-002", "PF-004"]
        )

    # General technical assistance
    reply = f"""Hey Engineer! Nilo here. 🚀

I'm monitoring your migration workspace. You asked: **"{req.message}"**

ClientShift is ready to help you migrate Python SDK code deterministically. Here's what I can do:
- **AST Static Analysis**: Parse code down to syntax tokens and callee chains.
- **Rule Grounding**: Retrieve exact breaking change specifications (PF-001 to PF-006).
- **Patch Generation**: Generate unified diffs with verified syntax.
- **Sandboxed Pytest**: Run strict 3s test validation with bounded repair loops.

Try selecting one of the workspace presets or click **"Analyze AST"** on your code!"""

    return NiloChatResponse(
        reply=reply,
        suggested_actions=["Why did my patch fail validation?", "Explain PayFlow v2 breaking changes", "How to run local benchmark"],
        rule_references=["PF-001", "PF-002"]
    )
