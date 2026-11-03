"""Compatibility alias for the existing continuous regime."""
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .experiments.regimes.continuous import *
import sys
from .experiments.regimes import continuous as _implementation
sys.modules[__name__] = _implementation
