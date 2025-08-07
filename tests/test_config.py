# =============================================================================
# tests/test_config.py
# =============================================================================
"""
Tests for main configuration class
"""

import pytest
import tempfile
from pathlib import Path
from nllpy.core.config import NLLocConfig


def test_basic_config():
    config = NLLocConfig()
    assert config.control.message_flag == 1
    assert config.locsig == "PyNLLoc - Python NLLoc Control Generator"


def test_add_station():
    config = NLLocConfig()
    config.add_station("VT01", 46.51, 8.47, 1500.0)

    assert len(config.gtsrce_stations) == 1
    station = config.gtsrce_stations[0]
    assert station.label == "VT01"
    assert station.lat_sta == 46.51
    assert station.lon_sta == 8.47
    assert station.elev == 1500.0


def test_gtsrce_section():
    config = NLLocConfig()
    config.add_station("VT01", 46.51, 8.47, 1500.0)
    config.add_station("VT02", 46.52, 8.48, 1200.0)

    section = config.get_gtsrce_section()
    lines = section.split('\n')
    assert len(lines) == 3  # Header + 2 stations
    assert "VT01" in lines[1]
    assert "VT02" in lines[2]


def test_write_control_file():
    config = NLLocConfig()
    config.trans.lat_orig = 46.51
    config.trans.lon_orig = 8.47
    config.add_station("VT01", 46.51, 8.47, 1500.0)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.in', delete=False) as f:
        temp_path = f.name

    try:
        config.write_complete_control_file(temp_path)

        # Verify file was created and has content
        content = Path(temp_path).read_text()
        assert "CONTROL" in content
        assert "TRANS" in content
        assert "LOCGRID" in content
        assert "GTSRCE VT01" in content

    finally:
        Path(temp_path).unlink()


def test_eqsta_inclusion_with_inventory():
    """Test that EQSTA commands are automatically added when inventory is provided"""
    config = NLLocConfig()
    
    # Add some test stations first
    config.add_station("VT01", 46.51, 8.47, 1500.0)
    config.add_station("VT02", 46.52, 8.48, 1200.0)
    
    # Initially no EQSTA commands
    assert len(config.eqsta_commands) == 0
    
    # Call modify_from_args with inventory (simulating control command)
    config.modify_from_args(
        inventory="test_inventory.txt",  # This will be ignored since it's not a real file
        p_error=0.15,
        s_error=0.25,
        phases="PS",
        error_type="GAU",
        prob_active=1.0
    )
    
    # Should now have EQSTA commands for both stations, both P and S phases
    assert len(config.eqsta_commands) == 4  # 2 stations × 2 phases
    
    # Check that EQSTA section contains the commands
    eqsta_section = config.get_eqsta_section()
    assert "VT01" in eqsta_section
    assert "VT02" in eqsta_section
    assert "P" in eqsta_section
    assert "S" in eqsta_section
    assert "0.15" in eqsta_section  # P error
    assert "0.25" in eqsta_section  # S error


def test_eqsta_phases_selection():
    """Test that only specified phases are included in EQSTA commands"""
    config = NLLocConfig()
    config.add_station("VT01", 46.51, 8.47, 1500.0)
    
    # Test P phase only
    config.modify_from_args(
        inventory="test_inventory.txt",
        p_error=0.1,
        s_error=0.2,
        phases="P",
        error_type="GAU"
    )
    
    assert len(config.eqsta_commands) == 1  # Only P phase
    assert config.eqsta_commands[0].phase == "P"
    
    # Test S phase only
    config.eqsta_commands.clear()
    config.modify_from_args(
        inventory="test_inventory.txt",
        p_error=0.1,
        s_error=0.2,
        phases="S",
        error_type="GAU"
    )
    
    assert len(config.eqsta_commands) == 1  # Only S phase
    assert config.eqsta_commands[0].phase == "S"
