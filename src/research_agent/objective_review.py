"""Compatibility alias; implementation lives in experiments.progress."""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .experiments.progress.objective_review import *
import sys
from .experiments.progress import objective_review as _implementation
sys.modules[__name__] = _implementation
