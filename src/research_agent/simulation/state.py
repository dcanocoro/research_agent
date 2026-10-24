"""Small local simulator. Mutations are synchronous and atomically persisted."""
from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation, localcontext
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Callable
from functools import wraps

from ..workspace import Workspace


def save(path: Path, value: Any) -> None:
    Workspace._check_links(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8"))
        stream.flush()
        os.fsync(stream.fileno())
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def read(path: Path) -> Any:
    Workspace._check_links(path)
    return json.loads(path.read_text(encoding="utf-8"))


def positive(value: Any) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("Expected a positive finite decimal.") from None
    if not result.is_finite() or result <= 0:
        raise ValueError("Expected a positive finite decimal.")
    return result


def decimal_context(function: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        with localcontext() as context:
            context.prec = 34
            return function(*args, **kwargs)
    return wrapped


class Simulator:
    def __init__(self, root: Path) -> None:
        self.root = root.absolute()
        self.config = read(self.root / "config.json")
        self.data = read(self.root / "data.json")
        self.state = read(self.root / "state.json")
        self.universe = {item["symbol"]: item for item in self.config["universe"]}
        self.prices: dict[str, list[dict[str, Any]]] = {}
        for row in self.data["prices"]:
            self.prices.setdefault(row["symbol"], []).append(row)
        for rows in self.prices.values():
            rows.sort(key=lambda row: row["date"])

    @classmethod
    def create(cls, root: Path, config: dict[str, Any], data: dict[str, Any]) -> Simulator:
        root.mkdir(parents=True, exist_ok=False)
        save(root / "config.json", config)
        save(root / "data.json", data)
        save(root / "state.json", {"date": config["start"], "cash": config["initial_cash"],
                                  "positions": {}, "orders": [], "notifications": []})
        return cls(root)

    @property
    def today(self) -> date:
        return date.fromisoformat(self.state["date"])

    def persist(self) -> None:
        save(self.root / "state.json", self.state)

    def symbol(self, value: str) -> str:
        value = value.strip().upper()
        if value not in self.universe:
            raise ValueError("Symbol is outside the frozen scenario universe.")
        return value

    def last_price(self, symbol: str) -> dict[str, Any] | None:
        rows = [r for r in self.prices.get(symbol, []) if r["date"] <= self.state["date"]]
        return rows[-1] if rows else None

    def pending(self) -> list[dict[str, Any]]:
        return [order for order in self.state["orders"] if order["status"] == "pending"]

    @decimal_context
    def get(self) -> dict[str, Any]:
        reserved = sum((Decimal(o["amount"]) for o in self.pending() if o["side"] == "buy"), Decimal(0))
        positions = []
        equity = Decimal(self.state["cash"])
        for symbol, quantity in sorted(self.state["positions"].items()):
            price = self.last_price(symbol)
            value = Decimal(quantity) * positive(price["close"]) if price else None
            if value is not None:
                equity += value
            positions.append({"symbol": symbol, "quantity": quantity,
                              "price": price, "value": str(value) if value is not None else None})
        return {"as_of": self.state["date"], "currency": "USD", "cash": self.state["cash"],
                "available_cash": str(Decimal(self.state["cash"]) - reserved),
                "positions": positions, "pending_orders": self.pending(),
                "equity": str(equity) if all(p["value"] is not None for p in positions) else None,
                "max_positions": self.config["max_positions"]}

    @decimal_context
    def order(self, symbol: str, side: str, value: Any) -> dict[str, Any]:
        symbol = self.symbol(symbol)
        if self.state.get("finished"):
            raise ValueError("Scenario is finished.")
        size = positive(value)
        if side == "buy":
            occupied = set(self.state["positions"]) | {o["symbol"] for o in self.pending() if o["side"] == "buy"}
            if symbol not in occupied and len(occupied) >= self.config["max_positions"]:
                raise ValueError("Maximum number of positions, including pending openings, reached.")
            if size > Decimal(self.get()["available_cash"]):
                raise ValueError("Insufficient available cash.")
        elif side == "sell":
            reserved = sum((Decimal(o["quantity"]) for o in self.pending()
                            if o["side"] == "sell" and o["symbol"] == symbol), Decimal(0))
            if size > Decimal(self.state["positions"].get(symbol, "0")) - reserved:
                raise ValueError("Insufficient available shares.")
        else:
            raise ValueError("Unknown side.")
        order = {"id": f"order-{len(self.state['orders']) + 1:06d}", "symbol": symbol,
                 "side": side, "submitted_on": self.state["date"], "status": "pending",
                 "amount" if side == "buy" else "quantity": str(size)}
        self.state["orders"].append(order)
        self.persist()
        # No future execution date or price is disclosed at submission.
        return dict(order)

    def buy(self, symbol: str, amount: str) -> dict[str, Any]:
        return self.order(symbol, "buy", amount)

    def sell(self, symbol: str, quantity: str) -> dict[str, Any]:
        return self.order(symbol, "sell", quantity)

    @decimal_context
    def close(self, symbol: str) -> dict[str, Any]:
        symbol = self.symbol(symbol)
        reserved = sum((Decimal(o["quantity"]) for o in self.pending()
                        if o["side"] == "sell" and o["symbol"] == symbol), Decimal(0))
        return self.order(symbol, "sell", Decimal(self.state["positions"].get(symbol, "0")) - reserved)

    def advance(self, target: date, *, finish: bool = False) -> None:
        if target < self.today or target > date.fromisoformat(self.config["end"]):
            raise ValueError("Clock must advance within the scenario.")
        executions = []
        for sequence, order in enumerate(self.pending()):
            price = next((p for p in self.prices.get(order["symbol"], [])
                          if order["submitted_on"] < p["date"] <= target.isoformat()), None)
            if price:
                executions.append((price["date"], sequence, order, price))
        for _, _, order, price in sorted(executions, key=lambda e: (e[0], e[1])):
            with localcontext() as context:
                context.prec = 34
                close = positive(price["close"])
                quantity = Decimal(order["amount"]) / close if order["side"] == "buy" else Decimal(order["quantity"])
                amount = Decimal(order["amount"]) if order["side"] == "buy" else quantity * close
                sign = 1 if order["side"] == "buy" else -1
                symbol = order["symbol"]
                held = Decimal(self.state["positions"].get(symbol, "0")) + sign * quantity
                cash = Decimal(self.state["cash"]) - sign * amount
                if held < 0 or cash < 0:
                    raise ValueError("Simulator accounting invariant violated.")
                if held:
                    self.state["positions"][symbol] = str(held)
                else:
                    self.state["positions"].pop(symbol, None)
                self.state["cash"] = str(cash)
                order.update(status="executed", executed_on=price["date"], price=str(close),
                             filled_quantity=str(quantity), filled_amount=str(amount), price_source=price)
        self.state["date"] = target.isoformat()
        if finish:
            for order in self.pending():
                order.update(status="cancelled", reason="scenario_ended")
            self.state["finished"] = True
        self.persist()

    def history(self) -> dict[str, Any]:
        return {"as_of": self.state["date"], "orders": self.state["orders"]}

    def notify(self, message: str) -> dict[str, Any]:
        notification = {"date": self.state["date"], "message": message}
        self.state["notifications"].append(notification)
        self.persist()
        return {"recorded": True, "external_delivery": False, **notification}
