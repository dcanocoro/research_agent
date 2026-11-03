"""Compatibility alias; implementation lives in experiments.regimes."""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .experiments.regimes.runtime_control import *
import sys
from .experiments.regimes import runtime_control as _implementation
sys.modules[__name__] = _implementation
