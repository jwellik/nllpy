# =============================================================================
# nllpy/__init__.py
# =============================================================================
"""
NLLPy: Python wrapper for NonLinLoc earthquake location software

This package provides a Python interface for generating NonLinLoc control files,
with special focus on volcano seismology applications.
"""

__version__ = "0.1.0"
__author__ = "Jay Wellik"
__email__ = "jwellik@usgs.gov"

# Import main classes for easy access
from .core.config import NLLocConfig
from .core.commands import (
    ControlCommand,
    TransCommand,
    LocGridCommand,
    LocSearchCommand,
    LocMethodCommand,
    GTSrceCommand,
    LayerCommand,
)

# Import template functions
from .templates.volcano import create_volcano_config
from .templates.regional import create_regional_config

__all__ = [
    "NLLocConfig",
    "ControlCommand",
    "TransCommand",
    "LocGridCommand",
    "LocSearchCommand",
    "LocMethodCommand",
    "GTSrceCommand",
    "LayerCommand",
    "create_volcano_config",
    "create_regional_config",
]
