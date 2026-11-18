import json
from pathlib import Path

cases = []

# Category 1: method_renames (10 cases)
method_cases = [
    {
        "name": "Standard Charge Creation",
        "code": "def process_order(client, total, user_id):\n    return client.charge.create(amount=total, currency=\"USD\", customer=user_id)",
        "test": "def test_process_order():\n    from migrated_module import process_order\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    client = PayFlowClient(config=ClientConfig(api_key=\"test\"))\n    res = process_order(client, 100, \"usr_1\")\n    assert res[\"status\"] == \"succeeded\"\n    assert res[\"amount\"] == 100",
        "expected_rules": ["PF-001"],
        "golden": "def process_order(client, total, user_id):\n    return client.payments.create(amount=total, currency=\"USD\", customer=user_id)"
    },
    {
        "name": "Charge Creation with Metadata",
        "code": "def submit_payment(client, meta):\n    return client.charge.create(amount=50, currency=\"USD\", metadata=meta)",
        "test": "def test_submit_payment():\n    from migrated_module import submit_payment\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    client = PayFlowClient(config=ClientConfig(api_key=\"test\"))\n    res = submit_payment(client, {\"order_id\": \"ord_99\"})\n    assert res[\"metadata\"][\"order_id\"] == \"ord_99\"",
        "expected_rules": ["PF-001"],
        "golden": "def submit_payment(client, meta):\n    return client.payments.create(amount=50, currency=\"USD\", metadata=meta)"
    },
    {
        "name": "Charge Create Assigned to Result Variable",
        "code": "def capture_cart(client, cart_id, price):\n    res = client.charge.create(amount=price, currency=\"USD\", cart_ref=cart_id)\n    return res.get(\"id\")",
        "test": "def test_capture_cart():\n    from migrated_module import capture_cart\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    client = PayFlowClient(config=ClientConfig(api_key=\"test\"))\n    tx_id = capture_cart(client, \"cart_555\", 42)\n    assert tx_id is not None and tx_id.startswith(\"pay_\")",
        "expected_rules": ["PF-001"],
        "golden": "def capture_cart(client, cart_id, price):\n    res = client.payments.create(amount=price, currency=\"USD\", cart_ref=cart_id)\n    return res.get(\"id\")"
    },
    {
        "name": "Customer Retrieve By ID",
        "code": "def fetch_user_profile(client, cid):\n    return client.customers.retrieve(id=cid)",
        "test": "def test_fetch_user():\n    from migrated_module import fetch_user_profile\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    client = PayFlowClient(config=ClientConfig(api_key=\"test\"))\n    c = fetch_user_profile(client, \"cus_44\")\n    assert c[\"customer_id\"] == \"cus_44\"",
        "expected_rules": ["PF-005"],
        "golden": "def fetch_user_profile(client, cid):\n    return client.customers.get(customer_id=cid)"
    },
    {
        "name": "Refund Process Transaction",
        "code": "def issue_store_credit(client, ch_id, val):\n    return client.refund.process(charge_id=ch_id, amount=val)",
        "test": "def test_issue_credit():\n    from migrated_module import issue_store_credit\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    client = PayFlowClient(config=ClientConfig(api_key=\"test\"))\n    rf = issue_store_credit(client, \"pay_100\", 50)\n    assert rf[\"status\"] == \"refunded\"",
        "expected_rules": ["PF-006"],
        "golden": "def issue_store_credit(client, ch_id, val):\n    return client.refunds.issue(payment_id=ch_id, amount=val)"
    },
    {
        "name": "Method Call Inside Class Method",
        "code": "class PaymentService:\n    def __init__(self, client):\n        self.client = client\n    def pay(self, cost):\n        return self.client.charge.create(amount=cost, currency=\"USD\")",
        "test": "def test_class_method():\n    from migrated_module import PaymentService\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    svc = PaymentService(PayFlowClient(config=ClientConfig(api_key=\"test\")))\n    r = svc.pay(300)\n    assert r[\"status\"] == \"succeeded\"",
        "expected_rules": ["PF-001"],
        "golden": "class PaymentService:\n    def __init__(self, client):\n        self.client = client\n    def pay(self, cost):\n        return self.client.payments.create(amount=cost, currency=\"USD\")"
    },
    {
        "name": "Multiple Charge Invocations in Loop",
        "code": "def process_batch(client, items):\n    results = []\n    for item in items:\n        res = client.charge.create(amount=item[\"val\"], currency=\"USD\")\n        results.append(res)\n    return results",
        "test": "def test_batch():\n    from migrated_module import process_batch\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    client = PayFlowClient(config=ClientConfig(api_key=\"test\"))\n    res = process_batch(client, [{\"val\": 10}, {\"val\": 20}])\n    assert len(res) == 2 and res[0][\"amount\"] == 10",
        "expected_rules": ["PF-001"],
        "golden": "def process_batch(client, items):\n    results = []\n    for item in items:\n        res = client.payments.create(amount=item[\"val\"], currency=\"USD\")\n        results.append(res)\n    return results"
    },
    {
        "name": "Customer Retrieve with Options",
        "code": "def get_account(client, account_id):\n    data = client.customers.retrieve(id=account_id)\n    return data[\"name\"]",
        "test": "def test_get_account():\n    from migrated_module import get_account\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    client = PayFlowClient(config=ClientConfig(api_key=\"test\"))\n    name = get_account(client, \"cus_vip\")\n    assert name == \"Customer cus_vip\"",
        "expected_rules": ["PF-005"],
        "golden": "def get_account(client, account_id):\n    data = client.customers.get(customer_id=account_id)\n    return data[\"name\"]"
    },
    {
        "name": "Refund with Reason Argument",
        "code": "def cancel_transaction(client, tx_id, why):\n    return client.refund.process(charge_id=tx_id, reason=why)",
        "test": "def test_cancel_tx():\n    from migrated_module import cancel_transaction\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    client = PayFlowClient(config=ClientConfig(api_key=\"test\"))\n    rf = cancel_transaction(client, \"pay_abc\", \"customer_request\")\n    assert rf[\"status\"] == \"refunded\"",
        "expected_rules": ["PF-006"],
        "golden": "def cancel_transaction(client, tx_id, why):\n    return client.refunds.issue(payment_id=tx_id, reason=why)"
    },
    {
        "name": "Charge Create with Description",
        "code": "def bill_invoice(client, inv_id, amt):\n    return client.charge.create(amount=amt, currency=\"USD\", description=f\"Inv {inv_id}\")",
        "test": "def test_bill_invoice():\n    from migrated_module import bill_invoice\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    client = PayFlowClient(config=ClientConfig(api_key=\"test\"))\n    out = bill_invoice(client, \"1001\", 75)\n    assert out[\"description\"] == \"Inv 1001\"",
        "expected_rules": ["PF-001"],
        "golden": "def bill_invoice(client, inv_id, amt):\n    return client.payments.create(amount=amt, currency=\"USD\", description=f\"Inv {inv_id}\")"
    }
]

for idx, item in enumerate(method_cases, 1):
    cases.append({
        "id": f"case-{len(cases)+1:03d}",
        "name": item["name"],
        "category": "method_renames",
        "description": f"Method rename migration scenario #{idx}",
        "source_code_v1": item["code"],
        "test_code": item["test"],
        "expected_rules": item["expected_rules"],
        "golden_v2_code": item["golden"]
    })

# Category 2: auth_init (10 cases)
auth_cases = [
    {
        "name": "Direct Client Init with apiKey camelCase",
        "code": "from payflow.client import PayFlowClient\ndef make_client(token):\n    return PayFlowClient(apiKey=token)",
        "test": "def test_make_client():\n    from migrated_module import make_client\n    c = make_client(\"live_secret_123\")\n    assert c.config.api_key == \"live_secret_123\"",
        "expected_rules": ["PF-004"],
        "golden": "from payflow.client import PayFlowClient\nfrom payflow.config import ClientConfig\ndef make_client(token):\n    return PayFlowClient(config=ClientConfig(api_key=token))"
    },
    {
        "name": "Direct Client Init with api_key snake_case",
        "code": "from payflow.client import PayFlowClient\ndef init_gateway():\n    return PayFlowClient(api_key=\"test_key_888\")",
        "test": "def test_init_gateway():\n    from migrated_module import init_gateway\n    c = init_gateway()\n    assert c.config.api_key == \"test_key_888\"",
        "expected_rules": ["PF-004"],
        "golden": "from payflow.client import PayFlowClient\nfrom payflow.config import ClientConfig\ndef init_gateway():\n    return PayFlowClient(config=ClientConfig(api_key=\"test_key_888\"))"
    },
    {
        "name": "Client Factory Function",
        "code": "import payflow.client as pf\ndef build_service(key):\n    return pf.PayFlowClient(apiKey=key)",
        "test": "def test_build_service():\n    from migrated_module import build_service\n    c = build_service(\"sk_prod\")\n    assert c.config.api_key == \"sk_prod\"",
        "expected_rules": ["PF-004"],
        "golden": "import payflow.client as pf\nfrom payflow.config import ClientConfig\ndef build_service(key):\n    return pf.PayFlowClient(config=ClientConfig(api_key=key))"
    },
    {
        "name": "Env Variable Client Setup",
        "code": "import os\nfrom payflow.client import PayFlowClient\ndef get_default_client():\n    key = os.getenv(\"PAYFLOW_KEY\", \"default_key\")\n    return PayFlowClient(api_key=key)",
        "test": "def test_default_client():\n    from migrated_module import get_default_client\n    c = get_default_client()\n    assert c.config.api_key == \"default_key\"",
        "expected_rules": ["PF-004"],
        "golden": "import os\nfrom payflow.client import PayFlowClient\nfrom payflow.config import ClientConfig\ndef get_default_client():\n    key = os.getenv(\"PAYFLOW_KEY\", \"default_key\")\n    return PayFlowClient(config=ClientConfig(api_key=key))"
    },
    {
        "name": "Class Initializing Client in __init__",
        "code": "from payflow.client import PayFlowClient\nclass BillingManager:\n    def __init__(self, key):\n        self.client = PayFlowClient(apiKey=key)",
        "test": "def test_manager():\n    from migrated_module import BillingManager\n    mgr = BillingManager(\"secret_token\")\n    assert mgr.client.config.api_key == \"secret_token\"",
        "expected_rules": ["PF-004"],
        "golden": "from payflow.client import PayFlowClient\nfrom payflow.config import ClientConfig\nclass BillingManager:\n    def __init__(self, key):\n        self.client = PayFlowClient(config=ClientConfig(api_key=key))"
    },
    {
        "name": "Client with Hardcoded Development Key",
        "code": "from payflow.client import PayFlowClient\ndef dev_client():\n    return PayFlowClient(apiKey=\"dev_12345\")",
        "test": "def test_dev():\n    from migrated_module import dev_client\n    c = dev_client()\n    assert c.config.api_key == \"dev_12345\"",
        "expected_rules": ["PF-004"],
        "golden": "from payflow.client import PayFlowClient\nfrom payflow.config import ClientConfig\ndef dev_client():\n    return PayFlowClient(config=ClientConfig(api_key=\"dev_12345\"))"
    },
    {
        "name": "Client Initialization with Argument Alias",
        "code": "from payflow.client import PayFlowClient\ndef setup(k):\n    c = PayFlowClient(apiKey=k)\n    return c",
        "test": "def test_alias():\n    from migrated_module import setup\n    c = setup(\"key_abc\")\n    assert c.config.api_key == \"key_abc\"",
        "expected_rules": ["PF-004"],
        "golden": "from payflow.client import PayFlowClient\nfrom payflow.config import ClientConfig\ndef setup(k):\n    c = PayFlowClient(config=ClientConfig(api_key=k))\n    return c"
    },
    {
        "name": "Client Init in Singleton Pattern",
        "code": "from payflow.client import PayFlowClient\n_instance = None\ndef get_singleton(secret):\n    global _instance\n    if _instance is None:\n        _instance = PayFlowClient(api_key=secret)\n    return _instance",
        "test": "def test_singleton():\n    from migrated_module import get_singleton\n    c1 = get_singleton(\"single_key\")\n    c2 = get_singleton(\"single_key\")\n    assert c1 is c2 and c1.config.api_key == \"single_key\"",
        "expected_rules": ["PF-004"],
        "golden": "from payflow.client import PayFlowClient\nfrom payflow.config import ClientConfig\n_instance = None\ndef get_singleton(secret):\n    global _instance\n    if _instance is None:\n        _instance = PayFlowClient(config=ClientConfig(api_key=secret))\n    return _instance"
    },
    {
        "name": "Client Init with Keyword Unpacking Guard",
        "code": "from payflow.client import PayFlowClient\ndef configure_client(auth_token):\n    client = PayFlowClient(apiKey=auth_token)\n    return client",
        "test": "def test_configure():\n    from migrated_module import configure_client\n    c = configure_client(\"tok_999\")\n    assert c.config.api_key == \"tok_999\"",
        "expected_rules": ["PF-004"],
        "golden": "from payflow.client import PayFlowClient\nfrom payflow.config import ClientConfig\ndef configure_client(auth_token):\n    client = PayFlowClient(config=ClientConfig(api_key=auth_token))\n    return client"
    },
    {
        "name": "Client Wrapper Function with Docstring",
        "code": "from payflow.client import PayFlowClient\ndef create_authenticated_client(key: str) -> PayFlowClient:\n    \"\"\"Return initialized client.\"\"\"\n    return PayFlowClient(apiKey=key)",
        "test": "def test_docstring():\n    from migrated_module import create_authenticated_client\n    c = create_authenticated_client(\"doc_key\")\n    assert c.config.api_key == \"doc_key\"",
        "expected_rules": ["PF-004"],
        "golden": "from payflow.client import PayFlowClient\nfrom payflow.config import ClientConfig\ndef create_authenticated_client(key: str) -> PayFlowClient:\n    \"\"\"Return initialized client.\"\"\"\n    return PayFlowClient(config=ClientConfig(api_key=key))"
    }
]

for idx, item in enumerate(auth_cases, 1):
    cases.append({
        "id": f"case-{len(cases)+1:03d}",
        "name": item["name"],
        "category": "auth_init",
        "description": f"Client authentication initialization scenario #{idx}",
        "source_code_v1": item["code"],
        "test_code": item["test"],
        "expected_rules": item["expected_rules"],
        "golden_v2_code": item["golden"]
    })

# Category 3: exceptions (10 cases)
exception_cases = [
    {
        "name": "Catch PayFlowError in Try Block",
        "code": "from payflow.exceptions import PayFlowError\ndef safe_execute(action):\n    try:\n        return action()\n    except PayFlowError as err:\n        return {\"error\": str(err)}",
        "test": "def test_safe():\n    from migrated_module import safe_execute\n    from payflow.exceptions import PayFlowAPIException\n    def failing():\n        raise PayFlowAPIException(\"API rate limit\")\n    res = safe_execute(failing)\n    assert \"API rate limit\" in res[\"error\"]",
        "expected_rules": ["PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException\ndef safe_execute(action):\n    try:\n        return action()\n    except PayFlowAPIException as err:\n        return {\"error\": str(err)}"
    },
    {
        "name": "Re-raise PayFlowError",
        "code": "from payflow.exceptions import PayFlowError\ndef guarded_call(fn):\n    try:\n        return fn()\n    except PayFlowError:\n        raise",
        "test": "def test_reraise():\n    import pytest\n    from migrated_module import guarded_call\n    from payflow.exceptions import PayFlowAPIException\n    def fail():\n        raise PayFlowAPIException(\"Network down\")\n    with pytest.raises(PayFlowAPIException):\n        guarded_call(fail)",
        "expected_rules": ["PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException\ndef guarded_call(fn):\n    try:\n        return fn()\n    except PayFlowAPIException:\n        raise"
    },
    {
        "name": "Direct Raise of PayFlowError",
        "code": "from payflow.exceptions import PayFlowError\ndef check_account(val):\n    if val < 0:\n        raise PayFlowError(\"Invalid balance\")\n    return True",
        "test": "def test_direct_raise():\n    import pytest\n    from migrated_module import check_account\n    from payflow.exceptions import PayFlowAPIException\n    with pytest.raises(PayFlowAPIException):\n        check_account(-1)",
        "expected_rules": ["PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException\ndef check_account(val):\n    if val < 0:\n        raise PayFlowAPIException(\"Invalid balance\")\n    return True"
    },
    {
        "name": "Multiple Exception Handlers with PayFlowError",
        "code": "from payflow.exceptions import PayFlowError\ndef handle_payment(task):\n    try:\n        return task()\n    except ValueError as e:\n        return \"value error\"\n    except PayFlowError as e:\n        return \"gateway error\"",
        "test": "def test_mult():\n    from migrated_module import handle_payment\n    from payflow.exceptions import PayFlowAPIException\n    def bomb():\n        raise PayFlowAPIException(\"fail\")\n    assert handle_payment(bomb) == \"gateway error\"",
        "expected_rules": ["PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException\ndef handle_payment(task):\n    try:\n        return task()\n    except ValueError as e:\n        return \"value error\"\n    except PayFlowAPIException as e:\n        return \"gateway error\""
    },
    {
        "name": "PayFlowError Subclass Checking with isinstance",
        "code": "from payflow.exceptions import PayFlowError\ndef is_payflow_problem(exc):\n    return isinstance(exc, PayFlowError)",
        "test": "def test_isinstance():\n    from migrated_module import is_payflow_problem\n    from payflow.exceptions import PayFlowAPIException\n    assert is_payflow_problem(PayFlowAPIException(\"err\")) is True",
        "expected_rules": ["PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException\ndef is_payflow_problem(exc):\n    return isinstance(exc, PayFlowAPIException)"
    },
    {
        "name": "Exception Log and Return Status",
        "code": "from payflow.exceptions import PayFlowError\ndef attempt_transaction(op):\n    try:\n        op()\n        return True\n    except PayFlowError:\n        return False",
        "test": "def test_attempt():\n    from migrated_module import attempt_transaction\n    from payflow.exceptions import PayFlowAPIException\n    def boom():\n        raise PayFlowAPIException(\"Card declined\")\n    assert attempt_transaction(boom) is False",
        "expected_rules": ["PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException\ndef attempt_transaction(op):\n    try:\n        op()\n        return True\n    except PayFlowAPIException:\n        return False"
    },
    {
        "name": "PayFlowError Custom Wrapper",
        "code": "from payflow.exceptions import PayFlowError\nclass CustomGatewayException(Exception):\n    pass\ndef wrap_error(fn):\n    try:\n        return fn()\n    except PayFlowError as orig:\n        raise CustomGatewayException(str(orig))",
        "test": "def test_custom_wrap():\n    import pytest\n    from migrated_module import wrap_error, CustomGatewayException\n    from payflow.exceptions import PayFlowAPIException\n    def boom():\n        raise PayFlowAPIException(\"bad auth\")\n    with pytest.raises(CustomGatewayException):\n        wrap_error(boom)",
        "expected_rules": ["PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException\nclass CustomGatewayException(Exception):\n    pass\ndef wrap_error(fn):\n    try:\n        return fn()\n    except PayFlowAPIException as orig:\n        raise CustomGatewayException(str(orig))"
    },
    {
        "name": "Catch Tuple with PayFlowError",
        "code": "from payflow.exceptions import PayFlowError\ndef multi_catch(func):\n    try:\n        return func()\n    except (IOError, PayFlowError):\n        return \"handled\"",
        "test": "def test_tuple_catch():\n    from migrated_module import multi_catch\n    from payflow.exceptions import PayFlowAPIException\n    def boom():\n        raise PayFlowAPIException(\"timeout\")\n    assert multi_catch(boom) == \"handled\"",
        "expected_rules": ["PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException\ndef multi_catch(func):\n    try:\n        return func()\n    except (IOError, PayFlowAPIException):\n        return \"handled\""
    },
    {
        "name": "Module Level Import of Exceptions",
        "code": "import payflow.exceptions as pfe\ndef verify_handler(fn):\n    try:\n        return fn()\n    except pfe.PayFlowError as e:\n        return str(e)",
        "test": "def test_module_import():\n    from migrated_module import verify_handler\n    from payflow.exceptions import PayFlowAPIException\n    def fail():\n        raise PayFlowAPIException(\"invalid signature\")\n    assert verify_handler(fail) == \"invalid signature\"",
        "expected_rules": ["PF-003"],
        "golden": "import payflow.exceptions as pfe\ndef verify_handler(fn):\n    try:\n        return fn()\n    except pfe.PayFlowAPIException as e:\n        return str(e)"
    },
    {
        "name": "PayFlowError in Exception Context Chain",
        "code": "from payflow.exceptions import PayFlowError\ndef raise_chained():\n    try:\n        raise ValueError(\"underlying fault\")\n    except ValueError as v:\n        raise PayFlowError(\"wrapped\") from v",
        "test": "def test_chain():\n    import pytest\n    from migrated_module import raise_chained\n    from payflow.exceptions import PayFlowAPIException\n    with pytest.raises(PayFlowAPIException) as excinfo:\n        raise_chained()\n    assert excinfo.value.__cause__ is not None",
        "expected_rules": ["PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException\ndef raise_chained():\n    try:\n        raise ValueError(\"underlying fault\")\n    except ValueError as v:\n        raise PayFlowAPIException(\"wrapped\") from v"
    }
]

for idx, item in enumerate(exception_cases, 1):
    cases.append({
        "id": f"case-{len(cases)+1:03d}",
        "name": item["name"],
        "category": "exceptions",
        "description": f"Exception handling migration scenario #{idx}",
        "source_code_v1": item["code"],
        "test_code": item["test"],
        "expected_rules": item["expected_rules"],
        "golden_v2_code": item["golden"]
    })

# Category 4: args_and_schemas (10 cases)
args_cases = [
    {
        "name": "Simple amount_cents Rename",
        "code": "def send_payment(client, cents):\n    return client.payments.create(amount_cents=cents, currency=\"USD\")",
        "test": "def test_send_payment():\n    from migrated_module import send_payment\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = send_payment(c, 2500)\n    assert res[\"amount\"] == 2500 and res[\"currency\"] == \"USD\"",
        "expected_rules": ["PF-002"],
        "golden": "def send_payment(client, cents):\n    return client.payments.create(amount=cents, currency=\"USD\")"
    },
    {
        "name": "Missing Currency Parameter Injection",
        "code": "def process_default_charge(client, amt):\n    return client.payments.create(amount=amt)",
        "test": "def test_default_charge():\n    from migrated_module import process_default_charge\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = process_default_charge(c, 3000)\n    assert res[\"currency\"] == \"USD\"",
        "expected_rules": ["PF-002"],
        "golden": "def process_default_charge(client, amt):\n    return client.payments.create(amount=amt, currency=\"USD\")"
    },
    {
        "name": "amount_cents and Missing Currency",
        "code": "def process_raw(client, total_cents):\n    return client.payments.create(amount_cents=total_cents)",
        "test": "def test_raw():\n    from migrated_module import process_raw\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = process_raw(c, 1500)\n    assert res[\"amount\"] == 1500 and res[\"currency\"] == \"USD\"",
        "expected_rules": ["PF-002"],
        "golden": "def process_raw(client, total_cents):\n    return client.payments.create(amount=total_cents, currency=\"USD\")"
    },
    {
        "name": "amount_cents with Explicit Customer",
        "code": "def bill_customer(client, cust_id, cents):\n    return client.payments.create(amount_cents=cents, currency=\"USD\", customer=cust_id)",
        "test": "def test_bill():\n    from migrated_module import bill_customer\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = bill_customer(c, \"c_1\", 4500)\n    assert res[\"amount\"] == 4500 and res[\"customer\"] == \"c_1\"",
        "expected_rules": ["PF-002"],
        "golden": "def bill_customer(client, cust_id, cents):\n    return client.payments.create(amount=cents, currency=\"USD\", customer=cust_id)"
    },
    {
        "name": "Variable Amount Cents Expression",
        "code": "def calc_and_pay(client, base, fee):\n    return client.payments.create(amount_cents=base + fee, currency=\"USD\")",
        "test": "def test_calc():\n    from migrated_module import calc_and_pay\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = calc_and_pay(c, 100, 25)\n    assert res[\"amount\"] == 125",
        "expected_rules": ["PF-002"],
        "golden": "def calc_and_pay(client, base, fee):\n    return client.payments.create(amount=base + fee, currency=\"USD\")"
    },
    {
        "name": "Keyword Argument amount_cents with Non-USD Currency",
        "code": "def pay_eur(client, cents):\n    return client.payments.create(amount_cents=cents, currency=\"EUR\")",
        "test": "def test_eur():\n    from migrated_module import pay_eur\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = pay_eur(c, 900)\n    assert res[\"amount\"] == 900 and res[\"currency\"] == \"EUR\"",
        "expected_rules": ["PF-002"],
        "golden": "def pay_eur(client, cents):\n    return client.payments.create(amount=cents, currency=\"EUR\")"
    },
    {
        "name": "amount_cents in Dictionary Kwargs Builder",
        "code": "def pay_with_idempotency(client, cents, key):\n    return client.payments.create(amount_cents=cents, currency=\"USD\", idempotency_key=key)",
        "test": "def test_idempotency():\n    from migrated_module import pay_with_idempotency\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = pay_with_idempotency(c, 600, \"idemp_01\")\n    assert res[\"amount\"] == 600 and res[\"idempotency_key\"] == \"idemp_01\"",
        "expected_rules": ["PF-002"],
        "golden": "def pay_with_idempotency(client, cents, key):\n    return client.payments.create(amount=cents, currency=\"USD\", idempotency_key=key)"
    },
    {
        "name": "Refund Argument charge_id to payment_id",
        "code": "def cancel_charge(client, charge_id):\n    return client.refunds.issue(charge_id=charge_id)",
        "test": "def test_cancel_charge():\n    from migrated_module import cancel_charge\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = cancel_charge(c, \"pay_999\")\n    assert res[\"payment_id\"] == \"pay_999\"",
        "expected_rules": ["PF-006"],
        "golden": "def cancel_charge(client, charge_id):\n    return client.refunds.issue(payment_id=charge_id)"
    },
    {
        "name": "Customer Retrieve id to customer_id",
        "code": "def query_customer(client, target_id):\n    return client.customers.get(id=target_id)",
        "test": "def test_query():\n    from migrated_module import query_customer\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = query_customer(c, \"cus_55\")\n    assert res[\"customer_id\"] == \"cus_55\"",
        "expected_rules": ["PF-005"],
        "golden": "def query_customer(client, target_id):\n    return client.customers.get(customer_id=target_id)"
    },
    {
        "name": "amount_cents and Multiple Options",
        "code": "def charge_vip(client, c_id, val):\n    return client.payments.create(amount_cents=val, customer=c_id)",
        "test": "def test_vip():\n    from migrated_module import charge_vip\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = charge_vip(c, \"cust_vip\", 7700)\n    assert res[\"amount\"] == 7700 and res[\"currency\"] == \"USD\"",
        "expected_rules": ["PF-002"],
        "golden": "def charge_vip(client, c_id, val):\n    return client.payments.create(amount=val, currency=\"USD\", customer=c_id)"
    }
]

for idx, item in enumerate(args_cases, 1):
    cases.append({
        "id": f"case-{len(cases)+1:03d}",
        "name": item["name"],
        "category": "args_and_schemas",
        "description": f"Argument and schema modernization scenario #{idx}",
        "source_code_v1": item["code"],
        "test_code": item["test"],
        "expected_rules": item["expected_rules"],
        "golden_v2_code": item["golden"]
    })

# Category 5: multi_change (10 cases combining multiple breaking changes)
multi_cases = [
    {
        "name": "Client Init + Method Rename + Args Change",
        "code": "from payflow.client import PayFlowClient\ndef checkout(key, total):\n    client = PayFlowClient(apiKey=key)\n    return client.charge.create(amount_cents=total)",
        "test": "def test_checkout():\n    from migrated_module import checkout\n    res = checkout(\"key_123\", 5000)\n    assert res[\"amount\"] == 5000 and res[\"currency\"] == \"USD\"",
        "expected_rules": ["PF-004", "PF-001", "PF-002"],
        "golden": "from payflow.client import PayFlowClient\nfrom payflow.config import ClientConfig\ndef checkout(key, total):\n    client = PayFlowClient(config=ClientConfig(api_key=key))\n    return client.payments.create(amount=total, currency=\"USD\")"
    },
    {
        "name": "Method Rename + Exception Handling",
        "code": "from payflow.exceptions import PayFlowError\ndef guarded_pay(client, cost):\n    try:\n        return client.charge.create(amount=cost, currency=\"USD\")\n    except PayFlowError:\n        return None",
        "test": "def test_guarded():\n    from migrated_module import guarded_pay\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"key\"))\n    res = guarded_pay(c, 200)\n    assert res[\"status\"] == \"succeeded\"",
        "expected_rules": ["PF-001", "PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException\ndef guarded_pay(client, cost):\n    try:\n        return client.payments.create(amount=cost, currency=\"USD\")\n    except PayFlowAPIException:\n        return None"
    },
    {
        "name": "Full Billing Flow (Init, Charge, Refund, Exception)",
        "code": "from payflow.client import PayFlowClient\nfrom payflow.exceptions import PayFlowError\ndef run_order_cycle(secret, amt):\n    try:\n        client = PayFlowClient(apiKey=secret)\n        charge = client.charge.create(amount_cents=amt)\n        refund = client.refund.process(charge_id=charge[\"id\"])\n        return {\"charge\": charge, \"refund\": refund}\n    except PayFlowError as e:\n        return {\"error\": str(e)}",
        "test": "def test_order_cycle():\n    from migrated_module import run_order_cycle\n    res = run_order_cycle(\"sec_test\", 1000)\n    assert \"charge\" in res and \"refund\" in res\n    assert res[\"charge\"][\"amount\"] == 1000",
        "expected_rules": ["PF-004", "PF-001", "PF-002", "PF-006", "PF-003"],
        "golden": "from payflow.client import PayFlowClient\nfrom payflow.config import ClientConfig\nfrom payflow.exceptions import PayFlowAPIException\ndef run_order_cycle(secret, amt):\n    try:\n        client = PayFlowClient(config=ClientConfig(api_key=secret))\n        charge = client.payments.create(amount=amt, currency=\"USD\")\n        refund = client.refunds.issue(payment_id=charge[\"id\"])\n        return {\"charge\": charge, \"refund\": refund}\n    except PayFlowAPIException as e:\n        return {\"error\": str(e)}"
    },
    {
        "name": "Customer Retrieval and Payment Creation",
        "code": "def charge_member(client, user_id, cents):\n    user = client.customers.retrieve(id=user_id)\n    return client.charge.create(amount_cents=cents, customer=user[\"customer_id\"])",
        "test": "def test_charge_member():\n    from migrated_module import charge_member\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"key\"))\n    res = charge_member(c, \"cus_99\", 8800)\n    assert res[\"amount\"] == 8800 and res[\"currency\"] == \"USD\"",
        "expected_rules": ["PF-005", "PF-001", "PF-002"],
        "golden": "def charge_member(client, user_id, cents):\n    user = client.customers.get(customer_id=user_id)\n    return client.payments.create(amount=cents, currency=\"USD\", customer=user[\"customer_id\"])"
    },
    {
        "name": "Client Initialization + Customer Lookup",
        "code": "from payflow.client import PayFlowClient\ndef find_client_user(token, cid):\n    client = PayFlowClient(apiKey=token)\n    return client.customers.retrieve(id=cid)",
        "test": "def test_find_user():\n    from migrated_module import find_client_user\n    res = find_client_user(\"tok_1\", \"cus_vip\")\n    assert res[\"customer_id\"] == \"cus_vip\"",
        "expected_rules": ["PF-004", "PF-005"],
        "golden": "from payflow.client import PayFlowClient\nfrom payflow.config import ClientConfig\ndef find_client_user(token, cid):\n    client = PayFlowClient(config=ClientConfig(api_key=token))\n    return client.customers.get(customer_id=cid)"
    },
    {
        "name": "Multi-Step Refund and Catch Error",
        "code": "from payflow.exceptions import PayFlowError\ndef refund_safely(client, ch_id):\n    try:\n        return client.refund.process(charge_id=ch_id)\n    except PayFlowError:\n        return {\"status\": \"failed\"}",
        "test": "def test_refund_safely():\n    from migrated_module import refund_safely\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = refund_safely(c, \"pay_10\")\n    assert res[\"status\"] == \"refunded\"",
        "expected_rules": ["PF-006", "PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException\ndef refund_safely(client, ch_id):\n    try:\n        return client.refunds.issue(payment_id=ch_id)\n    except PayFlowAPIException:\n        return {\"status\": \"failed\"}"
    },
    {
        "name": "Payment Gateway Adapter Class",
        "code": "from payflow.client import PayFlowClient\nfrom payflow.exceptions import PayFlowError\nclass GatewayAdapter:\n    def __init__(self, key):\n        self.client = PayFlowClient(apiKey=key)\n    def charge(self, val):\n        try:\n            return self.client.charge.create(amount_cents=val)\n        except PayFlowError as e:\n            return None",
        "test": "def test_adapter():\n    from migrated_module import GatewayAdapter\n    gw = GatewayAdapter(\"key_gw\")\n    res = gw.charge(300)\n    assert res[\"amount\"] == 300 and res[\"currency\"] == \"USD\"",
        "expected_rules": ["PF-004", "PF-001", "PF-002", "PF-003"],
        "golden": "from payflow.client import PayFlowClient\nfrom payflow.config import ClientConfig\nfrom payflow.exceptions import PayFlowAPIException\nclass GatewayAdapter:\n    def __init__(self, key):\n        self.client = PayFlowClient(config=ClientConfig(api_key=key))\n    def charge(self, val):\n        try:\n            return self.client.payments.create(amount=val, currency=\"USD\")\n        except PayFlowAPIException as e:\n            return None"
    },
    {
        "name": "Batch Invoicing with Customer Resolution",
        "code": "def process_accounts(client, accounts):\n    receipts = []\n    for acc in accounts:\n        cust = client.customers.retrieve(id=acc[\"cid\"])\n        tx = client.charge.create(amount_cents=acc[\"cents\"], customer=cust[\"customer_id\"])\n        receipts.append(tx[\"id\"])\n    return receipts",
        "test": "def test_accounts():\n    from migrated_module import process_accounts\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"key\"))\n    r = process_accounts(c, [{\"cid\": \"c1\", \"cents\": 100}, {\"cid\": \"c2\", \"cents\": 200}])\n    assert len(r) == 2",
        "expected_rules": ["PF-005", "PF-001", "PF-002"],
        "golden": "def process_accounts(client, accounts):\n    receipts = []\n    for acc in accounts:\n        cust = client.customers.get(customer_id=acc[\"cid\"])\n        tx = client.payments.create(amount=acc[\"cents\"], currency=\"USD\", customer=cust[\"customer_id\"])\n        receipts.append(tx[\"id\"])\n    return receipts"
    },
    {
        "name": "Complete Subscription Renewal Method",
        "code": "from payflow.exceptions import PayFlowError\ndef renew_sub(client, cid, cents):\n    try:\n        return client.charge.create(amount_cents=cents, customer=cid, currency=\"USD\")\n    except PayFlowError as err:\n        return {\"failed\": True, \"msg\": str(err)}",
        "test": "def test_renew():\n    from migrated_module import renew_sub\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"key\"))\n    res = renew_sub(c, \"cus_sub\", 999)\n    assert res[\"amount\"] == 999 and res[\"currency\"] == \"USD\"",
        "expected_rules": ["PF-001", "PF-002", "PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException\ndef renew_sub(client, cid, cents):\n    try:\n        return client.payments.create(amount=cents, customer=cid, currency=\"USD\")\n    except PayFlowAPIException as err:\n        return {\"failed\": True, \"msg\": str(err)}"
    },
    {
        "name": "Refund with Fallback Re-charge",
        "code": "from payflow.exceptions import PayFlowError\ndef exchange_item(client, orig_id, diff_cents):\n    try:\n        client.refund.process(charge_id=orig_id)\n        return client.charge.create(amount_cents=diff_cents)\n    except PayFlowError:\n        return None",
        "test": "def test_exchange():\n    from migrated_module import exchange_item\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"key\"))\n    res = exchange_item(c, \"pay_11\", 450)\n    assert res[\"amount\"] == 450 and res[\"currency\"] == \"USD\"",
        "expected_rules": ["PF-006", "PF-001", "PF-002", "PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException\ndef exchange_item(client, orig_id, diff_cents):\n    try:\n        client.refunds.issue(payment_id=orig_id)\n        return client.payments.create(amount=diff_cents, currency=\"USD\")\n    except PayFlowAPIException:\n        return None"
    }
]

for idx, item in enumerate(multi_cases, 1):
    cases.append({
        "id": f"case-{len(cases)+1:03d}",
        "name": item["name"],
        "category": "multi_change",
        "description": f"Multi-breaking-change migration scenario #{idx}",
        "source_code_v1": item["code"],
        "test_code": item["test"],
        "expected_rules": item["expected_rules"],
        "golden_v2_code": item["golden"]
    })

# Category 6: ambiguous_edge_cases (10 cases)
edge_cases = [
    {
        "name": "Dynamic Kwargs in Charge Call",
        "code": "def process_dynamic(client, **opts):\n    # Needs amount and currency in opts or direct\n    return client.charge.create(**opts)",
        "test": "def test_dyn():\n    from migrated_module import process_dynamic\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    r = process_dynamic(c, amount=100, currency=\"USD\")\n    assert r[\"status\"] == \"succeeded\"",
        "expected_rules": ["PF-001"],
        "golden": "def process_dynamic(client, **opts):\n    # Needs amount and currency in opts or direct\n    return client.payments.create(**opts)"
    },
    {
        "name": "Nested Client in Attribute Path",
        "code": "def nested_exec(ctx):\n    return ctx.services.payment_client.charge.create(amount=500, currency=\"USD\")",
        "test": "def test_nested():\n    from migrated_module import nested_exec\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    class Context:\n        class Services:\n            pass\n    ctx = Context()\n    ctx.services = Context.Services()\n    ctx.services.payment_client = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = nested_exec(ctx)\n    assert res[\"amount\"] == 500",
        "expected_rules": ["PF-001"],
        "golden": "def nested_exec(ctx):\n    return ctx.services.payment_client.payments.create(amount=500, currency=\"USD\")"
    },
    {
        "name": "Aliased Import of PayFlowClient",
        "code": "from payflow.client import PayFlowClient as Gateway\ndef build_custom():\n    return Gateway(apiKey=\"alias_key\")",
        "test": "def test_alias_init():\n    from migrated_module import build_custom\n    c = build_custom()\n    assert c.config.api_key == \"alias_key\"",
        "expected_rules": ["PF-004"],
        "golden": "from payflow.client import PayFlowClient as Gateway\nfrom payflow.config import ClientConfig\ndef build_custom():\n    return Gateway(config=ClientConfig(api_key=\"alias_key\"))"
    },
    {
        "name": "Charge Call with Conditional Currency Argument",
        "code": "def pay_cond(client, val, is_foreign):\n    cur = \"EUR\" if is_foreign else \"USD\"\n    return client.charge.create(amount=val, currency=cur)",
        "test": "def test_cond():\n    from migrated_module import pay_cond\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = pay_cond(c, 250, True)\n    assert res[\"currency\"] == \"EUR\"",
        "expected_rules": ["PF-001"],
        "golden": "def pay_cond(client, val, is_foreign):\n    cur = \"EUR\" if is_foreign else \"USD\"\n    return client.payments.create(amount=val, currency=cur)"
    },
    {
        "name": "Ambiguous Exception Aliased in as clause",
        "code": "from payflow.exceptions import PayFlowError as PaymentFailure\ndef do_action(action):\n    try:\n        return action()\n    except PaymentFailure as pf_err:\n        return str(pf_err)",
        "test": "def test_alias_exc():\n    from migrated_module import do_action\n    from payflow.exceptions import PayFlowAPIException\n    def fail():\n        raise PayFlowAPIException(\"failure\")\n    assert do_action(fail) == \"failure\"",
        "expected_rules": ["PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException as PaymentFailure\ndef do_action(action):\n    try:\n        return action()\n    except PaymentFailure as pf_err:\n        return str(pf_err)"
    },
    {
        "name": "Charge Create with Variable Dict Unpacking",
        "code": "def invoke_charge_params(client, cents):\n    data = {\"amount_cents\": cents, \"currency\": \"USD\"}\n    return client.charge.create(amount_cents=cents, currency=\"USD\")",
        "test": "def test_unpack():\n    from migrated_module import invoke_charge_params\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = invoke_charge_params(c, 400)\n    assert res[\"amount\"] == 400",
        "expected_rules": ["PF-001", "PF-002"],
        "golden": "def invoke_charge_params(client, cents):\n    data = {\"amount\": cents, \"currency\": \"USD\"}\n    return client.payments.create(amount=cents, currency=\"USD\")"
    },
    {
        "name": "Multiple Client Initializations in One Function",
        "code": "from payflow.client import PayFlowClient\ndef make_pair(k1, k2):\n    c1 = PayFlowClient(apiKey=k1)\n    c2 = PayFlowClient(api_key=k2)\n    return c1, c2",
        "test": "def test_pair():\n    from migrated_module import make_pair\n    c1, c2 = make_pair(\"one\", \"two\")\n    assert c1.config.api_key == \"one\" and c2.config.api_key == \"two\"",
        "expected_rules": ["PF-004"],
        "golden": "from payflow.client import PayFlowClient\nfrom payflow.config import ClientConfig\ndef make_pair(k1, k2):\n    c1 = PayFlowClient(config=ClientConfig(api_key=k1))\n    c2 = PayFlowClient(config=ClientConfig(api_key=k2))\n    return c1, c2"
    },
    {
        "name": "Async Charge Handler with Method Rename",
        "code": "async def async_pay(client, cents):\n    # Simulate async adapter wrapping sync call\n    return client.charge.create(amount_cents=cents, currency=\"USD\")",
        "test": "import asyncio\ndef test_async_pay():\n    from migrated_module import async_pay\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = asyncio.run(async_pay(c, 700))\n    assert res[\"amount\"] == 700",
        "expected_rules": ["PF-001", "PF-002"],
        "golden": "async def async_pay(client, cents):\n    # Simulate async adapter wrapping sync call\n    return client.payments.create(amount=cents, currency=\"USD\")"
    },
    {
        "name": "Decorated Function Calling charge.create",
        "code": "def audit_log(f):\n    def wrapper(*args, **kwargs):\n        return f(*args, **kwargs)\n    return wrapper\n\n@audit_log\ndef perform_transaction(client, amt):\n    return client.charge.create(amount=amt, currency=\"USD\")",
        "test": "def test_decorated():\n    from migrated_module import perform_transaction\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = perform_transaction(c, 850)\n    assert res[\"amount\"] == 850",
        "expected_rules": ["PF-001"],
        "golden": "def audit_log(f):\n    def wrapper(*args, **kwargs):\n        return f(*args, **kwargs)\n    return wrapper\n\n@audit_log\ndef perform_transaction(client, amt):\n    return client.payments.create(amount=amt, currency=\"USD\")"
    },
    {
        "name": "Complex Chained Customer and Refund Operation",
        "code": "from payflow.exceptions import PayFlowError\ndef refund_customer_balance(client, cid, charge_ref):\n    try:\n        user = client.customers.retrieve(id=cid)\n        return client.refund.process(charge_id=charge_ref)\n    except PayFlowError:\n        return False",
        "test": "def test_chained_edge():\n    from migrated_module import refund_customer_balance\n    from payflow.client import PayFlowClient\n    from payflow.config import ClientConfig\n    c = PayFlowClient(config=ClientConfig(api_key=\"k\"))\n    res = refund_customer_balance(c, \"cus_123\", \"ch_xyz\")\n    assert res[\"status\"] == \"refunded\"",
        "expected_rules": ["PF-005", "PF-006", "PF-003"],
        "golden": "from payflow.exceptions import PayFlowAPIException\ndef refund_customer_balance(client, cid, charge_ref):\n    try:\n        user = client.customers.get(customer_id=cid)\n        return client.refunds.issue(payment_id=charge_ref)\n    except PayFlowAPIException:\n        return False"
    }
]

for idx, item in enumerate(edge_cases, 1):
    cases.append({
        "id": f"case-{len(cases)+1:03d}",
        "name": item["name"],
        "category": "ambiguous_edge_cases",
        "description": f"Ambiguous edge case migration scenario #{idx}",
        "source_code_v1": item["code"],
        "test_code": item["test"],
        "expected_rules": item["expected_rules"],
        "golden_v2_code": item["golden"]
    })

print(f"Total benchmark cases prepared: {len(cases)}")
out_path = Path("clientshift/data/benchmark/cases.jsonl")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    for c in cases:
        f.write(json.dumps(c) + "\n")
print(f"Successfully wrote {len(cases)} cases to {out_path}")
