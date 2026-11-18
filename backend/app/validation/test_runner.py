import sys
import time
import subprocess
from pathlib import Path
from typing import Optional
from app.validation.sandbox import SandboxContext
from app.db.models import PytestOutput

class PytestRunner:
    def __init__(self, timeout_seconds: float = 3.0):
        self.timeout_seconds = timeout_seconds

    def run_validation(self, migrated_code: str, test_code: Optional[str] = None) -> PytestOutput:
        start_time = time.time()
        with SandboxContext(migrated_code=migrated_code, test_code=test_code) as sandbox:
            cwd = sandbox.temp_dir
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "test_migrated.py",
                "-v",
                "--tb=short"
            ]

            env = {
                **{k: v for k, v in subprocess.os.environ.items() if not k.startswith("PYTHON")},
                "PYTHONPATH": str(cwd),
                "PYTHONDONTWRITEBYTECODE": "1"
            }

            try:
                proc = subprocess.run(
                    cmd,
                    cwd=str(cwd),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout_seconds
                )
                duration = round(time.time() - start_time, 3)
                passed = (proc.returncode == 0)
                stdout = proc.stdout
                stderr = proc.stderr

                # Extract failure details if any
                failure_details = None
                if not passed:
                    failure_details = self._extract_failure_reason(stdout, stderr)

                summary = "All tests passed successfully" if passed else "Tests failed in sandbox"
                return PytestOutput(
                    exit_code=proc.returncode,
                    passed=passed,
                    summary=summary,
                    stdout=stdout,
                    stderr=stderr,
                    tests_run=1,
                    duration_s=duration,
                    failure_details=failure_details
                )
            except subprocess.TimeoutExpired as e:
                duration = round(time.time() - start_time, 3)
                return PytestOutput(
                    exit_code=-1,
                    passed=False,
                    summary=f"Pytest execution timed out after {self.timeout_seconds}s limit",
                    stdout=e.stdout or "",
                    stderr=e.stderr or "Execution exceeded safety timeout cap.",
                    tests_run=1,
                    duration_s=duration,
                    failure_details="TimeoutExpired: Sandboxed test exceeded strict 3s threshold."
                )
            except Exception as e:
                duration = round(time.time() - start_time, 3)
                return PytestOutput(
                    exit_code=1,
                    passed=False,
                    summary=f"Execution error: {str(e)}",
                    stdout="",
                    stderr=str(e),
                    tests_run=0,
                    duration_s=duration,
                    failure_details=str(e)
                )

    def _extract_failure_reason(self, stdout: str, stderr: str) -> str:
        lines = stdout.splitlines() + stderr.splitlines()
        extracted = []
        for line in lines:
            if "FAILED" in line or "ERROR" in line or "AssertionError" in line or "AttributeError" in line or "TypeError" in line or "ValueError" in line:
                extracted.append(line.strip())
        return "\n".join(extracted[:8]) if extracted else "Test assertion failed or raised unexpected exception."
