# 🚀 ClientShift — AI-Assisted Code Migration Engine & Benchmark Platform

> **Deterministic AI code-migration engine with AST static analysis, ground-truth catalog retrieval, minimal unified diffs, sandboxed Pytest verification, and bounded self-healing repair loops.**

---

## 🌟 Executive Overview

Migrating breaking SDK upgrades (e.g. **PayFlow SDK v1.0 ➔ v2.0**) often causes silent runtime outages when developers rely solely on ungrounded LLMs. LLMs hallucinate parameter names, miss subtle import removals, and cannot verify whether generated code actually executes.

**ClientShift changes the paradigm**:
- **Deterministic AST Verification & Pytest Exit Codes decide ground truth.** The LLM only proposes edits.
- **AST Static Analysis First**: Traverses the Python Abstract Syntax Tree before model prompting, extracting exact callee paths, keyword arguments, and line numbers.
- **Hybrid TF-IDF Rule Retrieval**: Injects only verified breaking migration specifications into the prompt context.
- **Sandboxed Test Isolation**: Executes generated code against contract tests with a strict 3-second timeout cap.
- **Bounded Repair Loop**: If Pytest fails (exit code ≠ 0), sanitized traceback logs feed back into the planner for up to 2 self-healing cycles.
- **Zero API Cost Runtime**: Local inference via Ollama (`qwen2.5-coder:7b`) with an instant deterministic mock model adapter fallback.

---

## 🏗️ System Architecture

```
                                  [Source Code V1]
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
         [Stage 1: AST Analysis]                        [Knowledge Catalog]
       • Extracts Call Nodes & Kwargs                     • PayFlow v1➔v2 Rules
       • Locates Deprecated Exceptions                            │
                  │                                               │
                  └───────────────────────┬───────────────────────┘
                                          ▼
                              [Stage 2: Rule Retrieval]
                            • Hybrid TF-IDF / AST Matching
                            • Ranked Rule Citations (PF-001..PF-006)
                                          │
                                          ▼
                                [Stage 3: AI Planner]
                             • Ollama (Qwen2.5-Coder 7B)
                             • Zero-Cost Mock Adapter Fallback
                             • Pydantic MigrationPlanSchema
                                          │
                                          ▼
                              [Stage 4: Unified Diff]
                            • Minimal .patch generation
                            • ast.parse() Syntax Check
                                          │
                                          ▼
                             [Stage 5: Sandbox Pytest]
                         • Isolated Temporary Environment
                         • Mock PayFlow v2 SDK Package
                         • 3s Execution Timeout Cap
                                          │
                             ┌────────────┴────────────┐
                             │                         │
                       [Pass: Exit 0]            [Fail: Exit ≠ 0]
                             │                         │
                             ▼                         ▼
                      [Final Patch]          [Bounded Repair Loop]
                                            (Max 2 Self-Healing Cycles)
```

---

## 📋 PayFlow SDK v1.0 ➔ v2.0 Breaking Changes

| Rule ID | Legacy Pattern (v1.0) | Target Pattern (v2.0) | Severity | Description |
| :--- | :--- | :--- | :--- | :--- |
| **PF-001** | `client.charge.create(...)` | `client.payments.create(...)` | 🚨 Breaking | Unified payment service method rename |
| **PF-002** | `amount_cents=5000` | `amount=5000, currency="USD"` | 🚨 Breaking | Parameter rename and mandatory currency field |
| **PF-003** | `except PayFlowError:` | `except PayFlowAPIException:` | 🚨 Breaking | Base exception modernized in exception hierarchy |
| **PF-004** | `PayFlowClient(apiKey="...")` | `PayFlowClient(config=ClientConfig(api_key="..."))` | 🚨 Breaking | Dedicated `ClientConfig` configuration object overhaul |
| **PF-005** | `customers.retrieve(id=...)` | `customers.get(customer_id=...)` | ⚠️ Method/Arg | Customer lookup standardization |
| **PF-006** | `refund.process(charge_id=...)`| `refunds.issue(payment_id=...)` | ⚠️ Pluralized | Refund method pluralization and parameter rename |

---

## 🎨 Tri-Mode Theme & Design System

The workbench interface implements a smooth, persistent theme system (`ThemeContext`) supporting 3 distinct modes with 300ms transitions:

1. **Dark Mode (`dark`) — Deep Midnight Obsidian**:
   - Background Base: `#0B0C10`
   - Card Surfaces & Panels: `#121218` with glassmorphic borders (`border-white/10`)
   - Accent 1 (Electric Cyan): `#00F2FE`
   - Accent 2 (Muted Champagne Gold): `#D4AF37`
   - Accent 3 (Soft Violet): `#8A2BE2`
2. **Light Mode (`light`) — Cream Vanilla & Electric Indigo**:
   - Background Base: `#FBF9F5`
   - Card Surfaces & Panels: `#FFFFFF`
   - Primary Accent (Royal Indigo): `#4F46E5`
   - Secondary Accent (Sunset Amber): `#F59E0B`
   - Highlight Accent (Ice Cyan): `#0891B2`
3. **Auto-Sync (`system_auto`) — Dynamic Day/Night Sync**:
   - Automatically synchronizes with local system time:
     - **06:00 to 18:59**: Warm Light Mode
     - **19:00 to 05:59**: Deep Midnight Obsidian

### Time-Aware Header Greeting & Real-Time Clock
- `05:00 - 11:59`: "Good morning, Engineer ☀️"
- `12:00 - 16:59`: "Good afternoon, Engineer ⚡"
- `17:00 - 21:59`: "Good evening, Architect 🌙"
- `22:00 - 04:59`: "Burning the midnight oil, Visionary 🚀"
- Real-time ticking Local & UTC clock widget.

---

## 🤖 Nilo AI Assistant (`NiloChatbot.tsx`)

- **Trigger**: Persistent floating action button (bottom-right) with pulsing cyan/violet glow aura + global keyboard shortcut `Cmd+K` / `Ctrl+K`.
- **Persona**: Warm, articulate, witty, deeply technical AI DevOps & Migration Specialist.
- **Capabilities**:
  1. Explains code migration errors, AST parsing issues, and Pytest tracebacks in plain English.
  2. Context-aware failure diagnosis on active workspace test errors.
  3. Interactive quick-action chips for breaking changes, benchmarks, and AST concepts.

---

## 📊 ClientShift-MiniBench Benchmark Harness

Includes **60 synthetic test cases** across 6 failure categories:
- `method_renames` (10 cases)
- `auth_init` (10 cases)
- `exceptions` (10 cases)
- `args_and_schemas` (10 cases)
- `multi_change` (10 cases)
- `ambiguous_edge_cases` (10 cases)

### Experimental Comparison:
- **Exp A (Baseline LLM)**: Ungrounded one-shot LLM migration.
- **Exp B (Rules + LLM)**: AST static detection + TF-IDF rule grounding.
- **Exp C (Full ClientShift)**: AST Grounding + Rule Retrieval + Pytest Sandbox + Bounded Repair Loop.

### Running the Benchmark CLI:
```powershell
python scripts/run_benchmark.py --experiment all
```

---

## ⚡ Quickstart & Local Execution

### 1. Start the Backend API (FastAPI)
```powershell
cd clientshift/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
FastAPI Swagger docs available at: `http://localhost:8000/docs`

### 2. Start the Frontend Workbench (Vite + React)
```powershell
cd clientshift/frontend
npm run dev
```
Workbench UI available at: `http://localhost:5173`

### 3. Run Backend Test Suite
```powershell
python -m pytest clientshift/backend/tests/test_backend.py -v
```

### 4. Run via Docker Compose
```powershell
docker-compose up --build
```
