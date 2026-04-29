from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Set
import pandas as pd

@dataclass
class VRPConfig:
    num_east_trucks: int
    num_west_trucks: int
    weather_multiplier: float
    cost_per_km: float
    search_time_limit: int
    service_time: int = 10
    fallback_speed: float = 20.0

@dataclass
class VRPResult:
    total_distance: float
    used_vehicles: int
    routes_text: List[str]
    map_polylines: List[Tuple[List[List[float]], str, bool]]
    visited_nodes: Set[int]
    school_labels: Dict[int, str]
    export_data: List[Dict[str, Any]]
    dropped_schools: Set[int]
    baseline_dist: float
    opt_cost: float
    savings_per_day: float
    savings_per_year: float
