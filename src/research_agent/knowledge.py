"""Compatibility alias; implementation lives in experiments.multiagent."""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .experiments.multiagent.knowledge import *
import sys
from .experiments.multiagent import knowledge as _implementation
sys.modules[__name__] = _implementation
