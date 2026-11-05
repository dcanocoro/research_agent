"""Standalone local POC worker. Preventive filters, NOT a security sandbox."""
from __future__ import annotations

import ast
import builtins
import json
import sys
import traceback
from typing import Any

MODULES = frozenset({"math", "statistics", "numpy", "pandas", "scipy", "numpy_financial"})
FORBIDDEN = frozenset({
    "open", "exec", "eval", "compile", "input", "print", "breakpoint", "help",
    "getattr", "setattr", "delattr", "vars", "dir", "globals", "locals", "type",
    "object", "super", "memoryview", "exit", "quit", "classmethod", "staticmethod",
    "property", "load", "loads", "save", "savez", "savez_compressed", "fromfile",
    "tofile", "memmap", "frombuffer", "ctypes", "ctypeslib", "f2py", "test",
    "show_config", "show_versions", "query", "get_handle", "read", "write",
    "read_pickle", "to_pickle", "ExcelFile", "ExcelWriter", "HDFStore", "DataSource",
    "urlopen", "system", "popen", "spawn", "connect", "load_library",
    "os", "sys", "subprocess", "builtins", "io", "pathlib", "socket", "requests",
    "importlib", "loadtxt", "genfromtxt", "savetxt", "fromregex", "dump", "dumps",
})
SAFE_BUILTINS = (
    "abs", "all", "any", "bool", "dict", "enumerate", "filter", "float", "int",
    "isinstance", "issubclass", "len", "list", "map", "max", "min", "next",
    "pow", "range", "reversed", "round", "set", "slice", "sorted", "str", "sum",
    "tuple", "zip", "Exception", "ValueError", "TypeError", "ZeroDivisionError",
    "ArithmeticError", "RuntimeError", "KeyError", "IndexError",
)


def validate_code(code: str) -> None:
    try:
        tree = ast.parse(code, filename="<operator>")
    except SyntaxError as exc:
        raise ValueError(f"syntax: line {exc.lineno}: {exc.msg}") from None
    for statement in tree.body:
        if not isinstance(statement, (ast.Import, ast.ImportFrom, ast.FunctionDef)):
            raise ValueError(f"contract: line {statement.lineno}: only imports and function definitions at module level")
    entry = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run"]
    if len(entry) != 1:
        raise ValueError("contract: define exactly one run(inputs, parameters)")
    args = entry[0].args
    if ([a.arg for a in args.args] != ["inputs", "parameters"] or args.posonlyargs
            or args.kwonlyargs or args.vararg or args.kwarg or args.defaults):
        raise ValueError("contract: required signature is run(inputs, parameters)")
    for node in ast.walk(tree):
        name = node.id if isinstance(node, ast.Name) else node.attr if isinstance(node, ast.Attribute) else ""
        if name and (name.startswith("_") or name in FORBIDDEN
                     or name.startswith(("read_", "to_")) and name not in {"to_dict", "to_list", "to_numpy", "to_records", "to_datetime", "to_numeric", "to_timedelta", "to_period", "to_timestamp"}):
            raise ValueError(f"restricted: line {getattr(node, 'lineno', '?')}: {name} is unavailable")
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            if (isinstance(node, ast.ImportFrom) and node.level) or any(m.split(".")[0] not in MODULES for m in modules):
                raise ValueError(f"restricted: line {node.lineno}: import outside allowed libraries")
            if any(a.name == "*" or any(p.startswith("_") or p in FORBIDDEN for p in a.name.split("."))
                   or (a.asname or "").startswith("_") for a in node.names):
                raise ValueError(f"restricted: line {node.lineno}: invalid import")
        if isinstance(node, (ast.ClassDef, ast.AsyncFunctionDef, ast.Global, ast.Nonlocal)):
            raise ValueError(f"restricted: line {node.lineno}: unsupported statement")
        if isinstance(node, ast.FunctionDef) and node.decorator_list:
            raise ValueError(f"restricted: line {node.lineno}: decorators are unavailable")


def reject_constant(value: str) -> None:
    raise ValueError(f"serialization: non-finite JSON constant {value}")


def main() -> None:
    try:
        # Paths come from the trusted parent, not the generated request. Do not
        # execute sitecustomize, .pth files, or any Research Agent initialization.
        sys.path.extend(json.loads(sys.argv[1]))
        request = json.loads(sys.stdin.buffer.read(), parse_constant=reject_constant)
        validate_code(request["code"])
        # Load scientific dependencies before restricting imports of generated code.
        import importlib
        libraries = {name: importlib.import_module(name) for name in MODULES}

        def allowed_import(name: str, globals: Any = None, locals: Any = None,
                           fromlist: Any = (), level: int = 0) -> Any:
            if level or name.split(".")[0] not in MODULES:
                raise ValueError("restricted: import outside allowed libraries")
            return builtins.__import__(name, globals, locals, fromlist, level)

        safe = {name: getattr(builtins, name) for name in SAFE_BUILTINS}
        safe["__import__"] = allowed_import
        scope: dict[str, Any] = {"__builtins__": safe, **libraries}
        exec(compile(request["code"], "<operator>", "exec"), scope)
        result = scope["run"](request["inputs"], request["parameters"])
        if not isinstance(result, dict):
            raise ValueError("serialization: run must return a JSON object")
        output = json.dumps({"ok": True, "result": result}, ensure_ascii=False, allow_nan=False).encode("utf-8")
        if len(output) > request["max_output_bytes"]:
            raise ValueError("limit: result exceeds output byte limit")
    except Exception as exc:
        frames = traceback.extract_tb(exc.__traceback__)
        line = next((f.lineno for f in reversed(frames) if f.filename == "<operator>"), None)
        message = f"{type(exc).__name__}" + (f" at line {line}" if line else "") + f": {exc}"
        output = json.dumps({"ok": False, "message": message[:400]}, ensure_ascii=False).encode("utf-8")
    sys.stdout.buffer.write(output)
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
