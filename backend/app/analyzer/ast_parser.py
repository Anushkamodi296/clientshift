import ast
from typing import List, Dict, Any, Optional

class CallNodeInfo:
    def __init__(
        self,
        full_call_path: str,
        callee_parts: List[str],
        func_name: str,
        kwargs: Dict[str, Any],
        kwarg_names: List[str],
        lineno: int,
        col_offset: int,
        end_lineno: Optional[int],
        end_col_offset: Optional[int],
        node: ast.Call
    ):
        self.full_call_path = full_call_path
        self.callee_parts = callee_parts
        self.func_name = func_name
        self.kwargs = kwargs
        self.kwarg_names = kwarg_names
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno or lineno
        self.end_col_offset = end_col_offset
        self.node = node

class ImportNodeInfo:
    def __init__(self, module: Optional[str], names: List[str], aliases: Dict[str, str], lineno: int):
        self.module = module
        self.names = names
        self.aliases = aliases
        self.lineno = lineno

class ExceptHandlerInfo:
    def __init__(self, exc_name: str, asname: Optional[str], lineno: int, node: ast.ExceptHandler):
        self.exc_name = exc_name
        self.asname = asname
        self.lineno = lineno
        self.node = node

class ParsedSource:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.lines = source_code.splitlines()
        self.tree: Optional[ast.AST] = None
        self.syntax_error: Optional[str] = None
        self.syntax_error_lineno: Optional[int] = None
        self.calls: List[CallNodeInfo] = []
        self.imports: List[ImportNodeInfo] = []
        self.except_handlers: List[ExceptHandlerInfo] = []
        self.parse()

    def parse(self):
        try:
            self.tree = ast.parse(self.source_code)
        except SyntaxError as e:
            self.syntax_error = str(e)
            self.syntax_error_lineno = e.lineno
            return

        visitor = CodeASTVisitor(self)
        visitor.visit(self.tree)

    def get_line_snippet(self, lineno: int, end_lineno: Optional[int] = None) -> str:
        if not self.lines:
            return ""
        start = max(1, lineno) - 1
        end = max(start + 1, end_lineno or lineno)
        return "\n".join(self.lines[start:end])

class CodeASTVisitor(ast.NodeVisitor):
    def __init__(self, parsed_source: ParsedSource):
        self.parsed_source = parsed_source

    def _get_attribute_chain(self, node: ast.AST) -> List[str]:
        parts = []
        curr = node
        while isinstance(curr, ast.Attribute):
            parts.append(curr.attr)
            curr = curr.value
        if isinstance(curr, ast.Name):
            parts.append(curr.id)
        elif isinstance(curr, ast.Call):
            parts.append("call()")
        return list(reversed(parts))

    def visit_Call(self, node: ast.Call):
        callee_parts = self._get_attribute_chain(node.func)
        full_path = ".".join(callee_parts)
        func_name = callee_parts[-1] if callee_parts else ""

        kwarg_names = []
        kwargs = {}
        for kw in node.keywords:
            if kw.arg is not None:
                kwarg_names.append(kw.arg)
                kwargs[kw.arg] = kw.value

        call_info = CallNodeInfo(
            full_call_path=full_path,
            callee_parts=callee_parts,
            func_name=func_name,
            kwargs=kwargs,
            kwarg_names=kwarg_names,
            lineno=node.lineno,
            col_offset=node.col_offset,
            end_lineno=getattr(node, "end_lineno", node.lineno),
            end_col_offset=getattr(node, "end_col_offset", None),
            node=node
        )
        self.parsed_source.calls.append(call_info)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        names = [alias.name for alias in node.names]
        aliases = {alias.name: alias.asname or alias.name for alias in node.names}
        self.parsed_source.imports.append(
            ImportNodeInfo(module=None, names=names, aliases=aliases, lineno=node.lineno)
        )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        names = [alias.name for alias in node.names]
        aliases = {alias.name: alias.asname or alias.name for alias in node.names}
        self.parsed_source.imports.append(
            ImportNodeInfo(module=node.module, names=names, aliases=aliases, lineno=node.lineno)
        )
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        if node.type is not None:
            exc_names = []
            if isinstance(node.type, ast.Name):
                exc_names.append(node.type.id)
            elif isinstance(node.type, ast.Attribute):
                parts = self._get_attribute_chain(node.type)
                exc_names.append(".".join(parts))
            elif isinstance(node.type, ast.Tuple):
                for elt in node.type.elts:
                    if isinstance(elt, ast.Name):
                        exc_names.append(elt.id)
                    elif isinstance(elt, ast.Attribute):
                        exc_names.append(".".join(self._get_attribute_chain(elt)))
            for name in exc_names:
                self.parsed_source.except_handlers.append(
                    ExceptHandlerInfo(
                        exc_name=name,
                        asname=node.name,
                        lineno=node.lineno,
                        node=node
                    )
                )
        self.generic_visit(node)
