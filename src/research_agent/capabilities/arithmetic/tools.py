from typing import Any

def calculate(operation: str, left: float, right: float, source_refs: list[str]) -> dict[str, object]:
    import math
    import operator
    functions = {"add": operator.add, "subtract": operator.sub, "multiply": operator.mul, "divide": operator.truediv}
    if not math.isfinite(left) or not math.isfinite(right) or operation not in functions:
        raise ValueError("Calculation requires finite numbers and a supported operation.")
    if operation == "divide" and right == 0:
        raise ValueError("Division requires a nonzero denominator.")
    result = functions[operation](left, right)
    if not math.isfinite(result):
        raise ValueError("Calculation produced a non-finite value.")
    return {"formula_version": "arithmetic-v1", "operation": operation, "left": left, "right": right,
            "result": result, "source_refs": source_refs}
