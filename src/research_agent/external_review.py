"""Compatibility alias; implementation lives in experiments.progress."""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .experiments.progress.external_review import *
import sys
from .experiments.progress import external_review as _implementation
sys.modules[__name__] = _implementation
