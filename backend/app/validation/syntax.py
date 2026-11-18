import ast
from typing import Tuple, Optional

def validate_syntax(code: str) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Validates Python syntax.
    Returns: (is_valid, error_message, line_number)
    """
    try:
        ast.parse(code)
        return True, None, None
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} at line {e.lineno}, col {e.offset}", e.lineno
    except Exception as e:
        return False, f"ParseError: {str(e)}", None
