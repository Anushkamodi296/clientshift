from typing import List, Optional
from app.analyzer.ast_parser import ParsedSource
from app.db.models import ASTEvidence
from app.knowledge.catalog import RuleCatalog

class ASTDetector:
    def __init__(self, catalog: Optional[RuleCatalog] = None):
        self.catalog = catalog or RuleCatalog()

    def detect(self, parsed: ParsedSource) -> List[ASTEvidence]:
        if parsed.syntax_error:
            return [
                ASTEvidence(
                    rule_id="SYNTAX-001",
                    rule_name="Python Syntax Error",
                    line_number=parsed.syntax_error_lineno or 1,
                    col_offset=0,
                    end_line_number=parsed.syntax_error_lineno or 1,
                    node_type="SyntaxError",
                    snippet=parsed.get_line_snippet(parsed.syntax_error_lineno or 1),
                    evidence_text=f"Source code has syntax error: {parsed.syntax_error}",
                    risk_level="HIGH",
                    recommended_fix="Fix syntax error before AST migration."
                )
            ]

        findings: List[ASTEvidence] = []

        # 1. Inspect Imports
        for imp in parsed.imports:
            # Check PF-003: PayFlowError import
            if "PayFlowError" in imp.names:
                snippet = parsed.get_line_snippet(imp.lineno)
                findings.append(
                    ASTEvidence(
                        rule_id="PF-003",
                        rule_name="Exception Hierarchy Modernization",
                        line_number=imp.lineno,
                        col_offset=0,
                        end_line_number=imp.lineno,
                        node_type="ImportFrom" if imp.module else "Import",
                        snippet=snippet,
                        evidence_text=f"Deprecated import 'PayFlowError' found from '{imp.module}'",
                        risk_level="HIGH",
                        recommended_fix="Replace 'PayFlowError' import with 'PayFlowAPIException'."
                    )
                )

        # 2. Inspect Exception Handlers
        for h in parsed.except_handlers:
            if "PayFlowError" in h.exc_name:
                snippet = parsed.get_line_snippet(h.lineno)
                findings.append(
                    ASTEvidence(
                        rule_id="PF-003",
                        rule_name="Exception Hierarchy Modernization",
                        line_number=h.lineno,
                        col_offset=0,
                        end_line_number=h.lineno,
                        node_type="ExceptHandler",
                        snippet=snippet,
                        evidence_text=f"except clause catches deprecated exception '{h.exc_name}'",
                        risk_level="HIGH",
                        recommended_fix="Catch 'PayFlowAPIException' instead of 'PayFlowError'."
                    )
                )

        # 3. Inspect Function Calls
        for call in parsed.calls:
            snippet = parsed.get_line_snippet(call.lineno, call.end_lineno)
            call_path = call.full_call_path

            # PF-004: PayFlowClient initialization
            if call_path.endswith("PayFlowClient") or call.func_name == "PayFlowClient" or "PayFlowClient" in call.callee_parts:
                has_api_key = "apiKey" in call.kwarg_names or "api_key" in call.kwarg_names
                has_config = "config" in call.kwarg_names
                if has_api_key or not has_config:
                    findings.append(
                        ASTEvidence(
                            rule_id="PF-004",
                            rule_name="Client Initialization Config Object Overhaul",
                            line_number=call.lineno,
                            col_offset=call.col_offset,
                            end_line_number=call.end_lineno,
                            node_type="Call",
                            snippet=snippet,
                            evidence_text=f"Direct PayFlowClient instantiation with kwargs {call.kwarg_names}. v2 requires config=ClientConfig(api_key=...)",
                            risk_level="HIGH",
                            recommended_fix="Wrap credentials in ClientConfig and pass config=ClientConfig(api_key=...)."
                        )
                    )

            # PF-001: Method rename: charge.create -> payments.create
            if "charge.create" in call_path or (
                len(call.callee_parts) >= 2 and call.callee_parts[-2] == "charge" and call.callee_parts[-1] == "create"
            ):
                findings.append(
                    ASTEvidence(
                        rule_id="PF-001",
                        rule_name="Payment Method Invocation Migration",
                        line_number=call.lineno,
                        col_offset=call.col_offset,
                        end_line_number=call.end_lineno,
                        node_type="Call",
                        snippet=snippet,
                        evidence_text=f"Call to deprecated 'charge.create' (full path: '{call_path}').",
                        risk_level="HIGH",
                        recommended_fix="Rename method invocation to 'payments.create'."
                    )
                )

            # PF-002: Argument rename: amount_cents -> amount, missing currency
            is_payment_call = (
                "charge.create" in call_path or
                "payments.create" in call_path or
                call.func_name == "create" and any("payment" in p or "charge" in p for p in call.callee_parts)
            )
            has_amount_cents = "amount_cents" in call.kwarg_names
            missing_currency = is_payment_call and ("currency" not in call.kwarg_names)

            if has_amount_cents or (is_payment_call and missing_currency):
                issues = []
                if has_amount_cents:
                    issues.append("uses deprecated 'amount_cents'")
                if missing_currency:
                    issues.append("missing mandatory 'currency' argument")
                
                findings.append(
                    ASTEvidence(
                        rule_id="PF-002",
                        rule_name="Payment Argument Rename & Currency Enforcement",
                        line_number=call.lineno,
                        col_offset=call.col_offset,
                        end_line_number=call.end_lineno,
                        node_type="Call",
                        snippet=snippet,
                        evidence_text=f"Call parameters issue: {', '.join(issues)} in kwargs: {call.kwarg_names}",
                        risk_level="MEDIUM" if not has_amount_cents else "HIGH",
                        recommended_fix="Rename 'amount_cents' to 'amount' and ensure currency='USD' is passed."
                    )
                )

            # PF-005: Customer retrieval: customers.retrieve -> customers.get
            if "customers.retrieve" in call_path or (
                len(call.callee_parts) >= 2 and call.callee_parts[-2] == "customers" and call.callee_parts[-1] == "retrieve"
            ):
                findings.append(
                    ASTEvidence(
                        rule_id="PF-005",
                        rule_name="Customer Retrieval Method & Parameter Standardization",
                        line_number=call.lineno,
                        col_offset=call.col_offset,
                        end_line_number=call.end_lineno,
                        node_type="Call",
                        snippet=snippet,
                        evidence_text=f"Deprecated 'customers.retrieve' called with kwargs {call.kwarg_names}",
                        risk_level="HIGH",
                        recommended_fix="Change to 'customers.get' and rename parameter 'id' to 'customer_id'."
                    )
                )
            elif "customers.get" in call_path and "id" in call.kwarg_names:
                findings.append(
                    ASTEvidence(
                        rule_id="PF-005",
                        rule_name="Customer Retrieval Method & Parameter Standardization",
                        line_number=call.lineno,
                        col_offset=call.col_offset,
                        end_line_number=call.end_lineno,
                        node_type="Call",
                        snippet=snippet,
                        evidence_text="Param 'id' used on customers.get. v2 requires 'customer_id'.",
                        risk_level="MEDIUM",
                        recommended_fix="Rename 'id' parameter to 'customer_id'."
                    )
                )

            # PF-006: Refund process: refund.process -> refunds.issue
            if "refund.process" in call_path or (
                len(call.callee_parts) >= 2 and call.callee_parts[-2] == "refund" and call.callee_parts[-1] == "process"
            ):
                findings.append(
                    ASTEvidence(
                        rule_id="PF-006",
                        rule_name="Refund Method Deprecation",
                        line_number=call.lineno,
                        col_offset=call.col_offset,
                        end_line_number=call.end_lineno,
                        node_type="Call",
                        snippet=snippet,
                        evidence_text=f"Deprecated 'refund.process' invoked with kwargs {call.kwarg_names}",
                        risk_level="HIGH",
                        recommended_fix="Change to 'refunds.issue' and rename 'charge_id' to 'payment_id'."
                    )
                )
            elif "refunds.issue" in call_path and "charge_id" in call.kwarg_names:
                findings.append(
                    ASTEvidence(
                        rule_id="PF-006",
                        rule_name="Refund Method Deprecation",
                        line_number=call.lineno,
                        col_offset=call.col_offset,
                        end_line_number=call.end_lineno,
                        node_type="Call",
                        snippet=snippet,
                        evidence_text="Param 'charge_id' used on refunds.issue. v2 requires 'payment_id'.",
                        risk_level="MEDIUM",
                        recommended_fix="Rename 'charge_id' to 'payment_id'."
                    )
                )

        return findings
