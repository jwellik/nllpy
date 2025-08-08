# =============================================================================
# nllpy/core/commands.py
# =============================================================================
"""
NLLoc command definitions as dataclasses
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class ControlCommand:
    """CONTROL command parameters"""
    message_flag: int = 1
    random_seed: int = 54321

    def __str__(self):
        return f"CONTROL {self.message_flag} {self.random_seed}"


@dataclass
class TransCommand:
    """TRANS command for coordinate transformation"""
    transformation: str = "SIMPLE"
    lat_orig: Optional[float] = None
    lon_orig: Optional[float] = None
    rotation: float = 0.0

    def __str__(self):
        if self.lat_orig is None or self.lon_orig is None:
            raise ValueError("lat_orig and lon_orig must be specified")
        return f"TRANS {self.transformation} {self.lat_orig} {self.lon_orig} {self.rotation}"


@dataclass
class VelGridCommand:
    """VELGRID command parameters"""
    num_grid_x: int = 200
    num_grid_y: int = 200
    num_grid_z: int = 50
    orig_grid_x: Optional[float] = None
    orig_grid_y: Optional[float] = None
    orig_grid_z: float = 0.0
    d_grid_x: float = 1.0
    d_grid_y: float = 1.0
    d_grid_z: float = 1.0
    d_xy: Optional[float] = None  # Convenience parameter for setting both d_grid_x and d_grid_y
    d_xyz: Optional[float] = None  # Convenience parameter for setting all three spacing values
    grid_type: str = "SLOW_LEN"

    def __post_init__(self):
        """Calculate grid origins if not specified and handle convenience spacing parameters"""
        # Handle convenience spacing parameters
        if self.d_xyz is not None:
            self.d_grid_x = self.d_grid_y = self.d_grid_z = self.d_xyz
        elif self.d_xy is not None:
            self.d_grid_x = self.d_grid_y = self.d_xy
        
        # Calculate grid origins if not specified
        if self.orig_grid_x is None:
            self.orig_grid_x = -(self.num_grid_x * self.d_grid_x) / 2.0
        if self.orig_grid_y is None:
            self.orig_grid_y = -(self.num_grid_y * self.d_grid_y) / 2.0

    def __str__(self):
        return (f"VGGRID {self.num_grid_x} {self.num_grid_y} {self.num_grid_z}  "
                f"{self.orig_grid_x} {self.orig_grid_y} {self.orig_grid_z}  "
                f"{self.d_grid_x} {self.d_grid_y} {self.d_grid_z}  "
                f"{self.grid_type}")

@dataclass
class LocGridCommand:
    """LOCGRID command parameters"""
    num_grid_x: int = 100
    num_grid_y: int = 100
    num_grid_z: int = 50
    orig_grid_x: Optional[float] = None
    orig_grid_y: Optional[float] = None
    orig_grid_z: float = 0.0
    d_grid_x: float = 1.0
    d_grid_y: float = 1.0
    d_grid_z: float = 1.0
    d_xy: Optional[float] = None  # Convenience parameter for setting both d_grid_x and d_grid_y
    d_xyz: Optional[float] = None  # Convenience parameter for setting all three spacing values
    grid_type: str = "PROB_DENSITY"
    float_type: str = "SAVE"

    def __post_init__(self):
        """Calculate grid origins if not specified and handle convenience spacing parameters"""
        # Handle convenience spacing parameters
        if self.d_xyz is not None:
            self.d_grid_x = self.d_grid_y = self.d_grid_z = self.d_xyz
        elif self.d_xy is not None:
            self.d_grid_x = self.d_grid_y = self.d_xy
        
        # Calculate grid origins if not specified
        if self.orig_grid_x is None:
            self.orig_grid_x = -(self.num_grid_x * self.d_grid_x) / 2.0
        if self.orig_grid_y is None:
            self.orig_grid_y = -(self.num_grid_y * self.d_grid_y) / 2.0

    def __str__(self):
        return (f"LOCGRID {self.num_grid_x} {self.num_grid_y} {self.num_grid_z}  "
                f"{self.orig_grid_x} {self.orig_grid_y} {self.orig_grid_z}  "
                f"{self.d_grid_x} {self.d_grid_y} {self.d_grid_z}  "
                f"{self.grid_type} {self.float_type}")


@dataclass
class LocSearchCommand:
    """LOCSEARCH command parameters"""

    # # Search parameters for local events
    # config.locsearch.search_type = "OCT"
    # config.locsearch.num_cells_x = 20
    # config.locsearch.num_cells_y = 20
    # config.locsearch.num_cells_z = 11
    # config.locsearch.min_node_size = 0.01
    # config.locsearch.max_num_nodes = 5000
    # config.locsearch.num_scatter = 1

    search_type: str = "OCT"
    num_cells_x: int = 20
    num_cells_y: int = 20
    num_cells_z: int = 11
    min_node_size: float = 0.01
    max_num_nodes: int = 20000
    num_scatter: int = 5000

    def __str__(self):
        if self.search_type == "OCT":
            return (f"LOCSEARCH {self.search_type} {self.num_cells_x} {self.num_cells_y} {self.num_cells_z} "
                    f"{self.min_node_size} {self.max_num_nodes} {self.num_scatter} 0 1")  # STUB
        else:
            return f"LOCSEARCH {self.search_type}"


@dataclass
class LocMethodCommand:
    """LOCMETH command parameters"""
    method: str = "EDT_OT_WT"
    max_dist_sta_grid: float = 9999.0
    min_num_phases: int = 6
    max_num_phases: int = -1
    min_num_s_phases: int = -1
    v_p_vs_ratio: int = -1
    max_num_3d_grid_memory: int = 0
    min_num_loc_grids: int = -1
    duplicate_arrivals_mode: int = 1

    def __str__(self):
        return (f"LOCMETH {self.method} {self.max_dist_sta_grid:.1f} "
                f"{self.min_num_phases} {self.max_num_phases} "
                f"{self.min_num_s_phases} {self.v_p_vs_ratio} "
                f"{self.max_num_3d_grid_memory} {self.min_num_loc_grids} "
                f"{self.duplicate_arrivals_mode}")


@dataclass
class GTSrceCommand:
    """GTSRCE command for station parameters"""
    label: str
    lat_sta: float
    lon_sta: float
    elev: float
    depth_corr: float = 0.0
    sta_fmt: str = "STA"

    def __str__(self):
        # Adjust field width based on station format
        if self.sta_fmt in ["NET.STA", "NET_STA"]:
            field_width = 8
        else:
            field_width = 5
        
        return f"GTSRCE {self.label:<{field_width}s} LATLON {self.lat_sta:.6f} {self.lon_sta:.6f} {self.depth_corr:.1f} {self.elev:.3f} "

@dataclass
class EQSTACommand:
    """Command for station-specific error definitions"""
    label: str
    phase: str = "P"
    error_type: str = "GAU"
    error: float = 0.0
    error_report_type: str = "GAU"
    error_report: float = 0.0
    prob_active: float = 1.0
    sta_fmt: str = "STA"

    def __str__(self) -> str:
        # Adjust field width based on station format
        if self.sta_fmt in ["NET.STA", "NET_STA"]:
            field_width = 8
        else:
            field_width = 5

        return f"EQSTA  {self.label:<{field_width}s}  {self.phase}  {self.error_type}  {self.error}  {self.error_report_type}  {self.error_report}  {self.prob_active}"

@dataclass
class LayerCommand:
    """LAYER layers for velocity model"""
    layers: List[Tuple[float, float, float, float, float, float, float]] = field(default_factory=list)

    def __post_init__(self):
        if not self.layers:
            # Generic stratovolcano model from Pesicek & Rynberg (2024)
            self.layers = [
                (0.00, 4.2669, 0.00, 2.4664, 0.00, 2.7, 0.0),
                (1.00, 4.6400, 0.00, 2.6821, 0.00, 2.7, 0.0),
                (2.00, 4.9574, 0.00, 2.8656, 0.00, 2.7, 0.0),
                (3.00, 5.2000, 0.00, 3.0059, 0.00, 2.7, 0.0),
                (4.00, 5.3846, 0.00, 3.1125, 0.00, 2.7, 0.0),
                (5.00, 5.5344, 0.00, 3.1991, 0.00, 2.7, 0.0),
                (6.00, 5.6382, 0.00, 3.2591, 0.00, 2.7, 0.0),
                (7.00, 5.7612, 0.00, 3.3302, 0.00, 2.7, 0.0),
                (8.00, 5.8638, 0.00, 3.3895, 0.00, 2.7, 0.0),
                (9.00, 5.9561, 0.00, 3.4429, 0.00, 2.7, 0.0),
                (10.00, 6.0681, 0.00, 3.5076, 0.00, 2.7, 0.0),
                (11.00, 6.1625, 0.00, 3.5621, 0.00, 2.7, 0.0),
                (12.00, 6.2579, 0.00, 3.6173, 0.00, 2.7, 0.0),
                (13.00, 6.3340, 0.00, 3.6613, 0.00, 2.7, 0.0),
                (14.00, 6.3930, 0.00, 3.6954, 0.00, 2.7, 0.0),
                (15.00, 6.5047, 0.00, 3.7600, 0.00, 2.7, 0.0),
                (16.00, 6.5277, 0.00, 3.7732, 0.00, 2.7, 0.0),
                (17.00, 6.5967, 0.00, 3.8131, 0.00, 2.7, 0.0),
                (18.00, 6.6520, 0.00, 3.8451, 0.00, 2.7, 0.0),
                (19.00, 6.7230, 0.00, 3.8861, 0.00, 2.7, 0.0),
                (20.00, 6.7715, 0.00, 3.9142, 0.00, 2.7, 0.0),
                (21.00, 6.8049, 0.00, 3.8861, 0.00, 2.7, 0.0),
                (22.00, 6.8533, 0.00, 3.9614, 0.00, 2.7, 0.0),
                (23.00, 6.8985, 0.00, 3.9876, 0.00, 2.7, 0.0),
                (24.00, 6.9619, 0.00, 4.0242, 0.00, 2.7, 0.0),
                (25.00, 6.9889, 0.00, 4.0398, 0.00, 2.7, 0.0),
                (26.00, 7.0233, 0.00, 4.0597, 0.00, 2.7, 0.0),
                (27.00, 7.0807, 0.00, 4.0929, 0.00, 2.7, 0.0),
                (28.00, 7.1085, 0.00, 4.1089, 0.00, 2.7, 0.0),
            ]

    def __str__(self):
        lines = []
        for depth, VpTop, VpGrad, VsTop, VsGrad, rhoTop, rhoGrad in self.layers:
            lines.append(f"LAYER {depth:>5.2f} {VpTop:.2f} {VpGrad:.2f} {VsTop:.2f} {VsGrad:.2f} {rhoTop:.2f} {rhoGrad:.2f}")
        return "\n".join(lines)


@dataclass
class LocPhaseIDCommand:
    """LOCPHASEID command for phase definitions"""
    phase_type: str
    phase_labels: List[str]

    def __str__(self):
        return f"LOCPHASEID {self.phase_type}   {' '.join(self.phase_labels)}"


@dataclass
class LocQual2ErrCommand:
    """LOCQUAL2ERR command for quality to error mapping"""
    error_values: List[float] = field(default_factory=lambda: [0.02, 0.05, 0.1, 0.2, 0.5, 99999.9])

    def __str__(self):
        error_str = ' '.join([f"{err:.3f}" for err in self.error_values])
        return f"LOCQUAL2ERR {error_str}"