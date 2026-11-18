import difflib
from typing import Tuple, Dict, Any

class DiffPatcher:
    @staticmethod
    def generate_unified_diff(
        original_code: str,
        migrated_code: str,
        filename: str = "source_module.py"
    ) -> str:
        orig_lines = original_code.splitlines(keepends=True)
        mig_lines = migrated_code.splitlines(keepends=True)

        diff = difflib.unified_diff(
            orig_lines,
            mig_lines,
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
            lineterm=""
        )
        return "\n".join(diff)

    @staticmethod
    def get_diff_stats(diff_text: str) -> Dict[str, Any]:
        lines = diff_text.splitlines()
        added = 0
        removed = 0
        for l in lines:
            if l.startswith("+") and not l.startswith("+++"):
                added += 1
            elif l.startswith("-") and not l.startswith("---"):
                removed += 1
        return {
            "additions": added,
            "deletions": removed,
            "total_changes": added + removed
        }
