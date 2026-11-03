"""Compatibility alias; implementation lives in experiments.progress."""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .experiments.progress.objectives import *
import sys
from .experiments.progress import objectives as _implementation
sys.modules[__name__] = _implementation
