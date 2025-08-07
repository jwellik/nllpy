# =============================================================================
# tests/test_commands.py
# =============================================================================
"""
Tests for command classes
"""

import pytest
from nllpy.core.commands import (
    ControlCommand, TransCommand, LocGridCommand,
    GTSrceCommand
)


def test_control_command():
    cmd = ControlCommand()
    assert str(cmd) == "CONTROL 1 54321"

    cmd = ControlCommand(message_flag=-1, random_seed=12345)
    assert str(cmd) == "CONTROL -1 12345"


def test_trans_command():
    cmd = TransCommand(transformation="SDC", lat_orig=46.51, lon_orig=8.48)
    expected = "TRANS SDC 46.51000000 8.48000000 0.00"
    assert str(cmd) == expected


def test_locgrid_command():
    cmd = LocGridCommand()
    expected = ("LOCGRID 101 101 51 0.000 0.000 0.000 "
                "1.000 1.000 1.000 PROB_DENSITY SAVE")
    assert str(cmd) == expected


def test_gtsrce_command():
    cmd = GTSrceCommand("VT01", 46.5103, 8.4758, -1.5)
    expected = "GTSRCE VT01 LATLON 46.510300 8.475800 -1.500 0.000"
    assert str(cmd) == expected
