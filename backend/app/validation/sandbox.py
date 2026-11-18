import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

PAYFLOW_V2_CONFIG_CODE = """
class ClientConfig:
    def __init__(self, api_key: str):
        self.api_key = api_key
"""

PAYFLOW_V2_EXCEPTIONS_CODE = """
class PayFlowAPIException(Exception):
    pass

class PayFlowError(Exception):
    pass
"""

PAYFLOW_V2_CLIENT_CODE = """
from payflow.config import ClientConfig
from payflow.exceptions import PayFlowAPIException

class PaymentsService:
    def create(self, **kwargs):
        if "amount" not in kwargs:
            raise ValueError("amount is required in PayFlow v2")
        if "currency" not in kwargs:
            raise ValueError("currency is required in PayFlow v2")
        return {
            "id": "pay_987654321",
            "status": "succeeded",
            "amount": kwargs.get("amount"),
            "currency": kwargs.get("currency"),
            "customer": kwargs.get("customer"),
            "metadata": kwargs.get("metadata", {}),
            "description": kwargs.get("description"),
            "idempotency_key": kwargs.get("idempotency_key")
        }

class CustomersService:
    def get(self, customer_id: str):
        return {
            "customer_id": customer_id,
            "name": f"Customer {customer_id}",
            "email": f"{customer_id}@example.com"
        }
    def retrieve(self, *args, **kwargs):
        raise AttributeError("PayFlow v2 deprecated 'customers.retrieve'. Use 'customers.get(customer_id=...)'")

class RefundsService:
    def issue(self, payment_id: str, **kwargs):
        return {
            "id": "ref_112233",
            "status": "refunded",
            "payment_id": payment_id,
            "amount": kwargs.get("amount"),
            "reason": kwargs.get("reason")
        }
    def process(self, *args, **kwargs):
        raise AttributeError("PayFlow v2 deprecated 'refund.process'. Use 'refunds.issue(payment_id=...)'")

class DeprecatedChargeService:
    def create(self, *args, **kwargs):
        raise AttributeError("PayFlow v2 removed 'client.charge.create'. Use 'client.payments.create(...)'.")

class PayFlowClient:
    def __init__(self, config=None, **kwargs):
        if "apiKey" in kwargs or "api_key" in kwargs:
            raise TypeError("PayFlowClient direct apiKey/api_key initialization is deprecated in v2. Use config=ClientConfig(api_key=...).")
        if config is None or not isinstance(config, ClientConfig):
            raise ValueError("PayFlowClient requires a valid ClientConfig instance passed to config.")
        self.config = config
        self.payments = PaymentsService()
        self.charge = DeprecatedChargeService()
        self.customers = CustomersService()
        self.refunds = RefundsService()
        self.refund = self.refunds
"""

class SandboxContext:
    def __init__(self, migrated_code: str, test_code: Optional[str] = None):
        self.migrated_code = migrated_code
        self.test_code = test_code
        self.temp_dir: Optional[Path] = None

    def __enter__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="clientshift_sandbox_"))
        self._setup_environment()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            except Exception:
                pass

    def _setup_environment(self):
        # Create payflow package directory
        pkg_dir = self.temp_dir / "payflow"
        pkg_dir.mkdir(parents=True, exist_ok=True)
        (pkg_dir / "__init__.py").write_text("# PayFlow v2 Mock Package\n", encoding="utf-8")
        (pkg_dir / "config.py").write_text(PAYFLOW_V2_CONFIG_CODE.strip() + "\n", encoding="utf-8")
        (pkg_dir / "exceptions.py").write_text(PAYFLOW_V2_EXCEPTIONS_CODE.strip() + "\n", encoding="utf-8")
        (pkg_dir / "client.py").write_text(PAYFLOW_V2_CLIENT_CODE.strip() + "\n", encoding="utf-8")

        # Write migrated module
        (self.temp_dir / "migrated_module.py").write_text(self.migrated_code, encoding="utf-8")

        # Write test code
        test_content = self.test_code or "def test_syntax():\n    import migrated_module\n    assert True\n"
        (self.temp_dir / "test_migrated.py").write_text(test_content, encoding="utf-8")
