import numpy as np
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from models import VRPConfig, VRPResult
from data import get_coordinates_only
from osrm import get_osrm_route_geometry
import streamlit as st
from i18n import get_translator

def solve_vrp(config: VRPConfig, locations: list, location_names: list, location_addresses: list, dist_matrix: np.ndarray, base_duration_matrix: np.ndarray, lang: str) -> VRPResult:
    _t = get_translator(lang)
    num_locations = len(locations)
    
    # Numpyによる時間計算の圧縮
    time_matrix = (base_duration_matrix * config.weather_multiplier).astype(int)
    for i in range(2, num_locations):
        time_matrix[i, :] += config.service_time

    num_vehicles = config.num_east_trucks + config.num_west_trucks
    starts = [0] * config.num_east_trucks + [1] * config.num_west_trucks
    ends = [0] * config.num_east_trucks + [1] * config.num_west_trucks

    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, starts, ends)
    routing = pywrapcp.RoutingModel(manager)

    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(time_matrix[from_node][to_node])

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    demands = [0, 0] + [1] * 28
    def demand_callback(from_index):
        return demands[manager.IndexToNode(from_index)]
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index, 0, [2] * num_vehicles, True, 'Capacity'
    )

    routing.AddDimension(
        transit_callback_index, 30, 180, False, 'Time'
    )
    time_dimension = routing.GetDimensionOrDie('Time')

    for node in range(num_locations):
        index = manager.NodeToIndex(node)
        if node == 0 or node == 1:
            time_dimension.CumulVar(index).SetRange(0, 120)
        else:
            time_dimension.CumulVar(index).SetRange(30, 60)
            routing.AddDisjunction([index], 10000000)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_parameters.time_limit.seconds = config.search_time_limit

    solution = routing.SolveWithParameters(search_parameters)
    
    if not solution:
        return None

    # 結果抽出ロジック
    total_dist_optimized = 0.0
    used_vehicles = 0
    routes_text = []
    map_polylines = []
    visited_nodes = set()
    school_labels = {}
    export_data = []

    if "route_geometry_cache" not in st.session_state:
        st.session_state.route_geometry_cache = {}

    all_locs_tuple = get_coordinates_only()

    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route_dist = 0.0
        route_nodes = []
        
        if routing.IsEnd(solution.Value(routing.NextVar(index))):
            continue
            
        used_vehicles += 1
        is_east = (vehicle_id < config.num_east_trucks)
        color = "red" if is_east else "blue"
        depot_name = _t("depot_east") if is_east else _t("depot_west")
        
        route_log = _t("log_truck", depot_name=depot_name, v_id=vehicle_id + 1)
        
        order = 1
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route_nodes.append(node)
            if node >= 2:
                visited_nodes.add(node)
                school_labels[node] = f"{vehicle_id+1}-{order}"
                order += 1
            
            time_var = time_dimension.CumulVar(index)
            arr_min = solution.Min(time_var)
            total_minutes = 10 * 60 + 30 + arr_min
            arr_hour = total_minutes // 60
            arr_minute = total_minutes % 60
            time_str = f"{arr_hour:02d}:{arr_minute:02d}"
            
            route_log += f"{location_names[node]}({time_str}) ➡️ "
            
            export_data.append({
                "Truck_ID": f"{depot_name}-{vehicle_id + 1}",
                "Stop_Order": order - 1 if node >= 2 else 0,
                "Location_Name": location_names[node],
                "Address": location_addresses[node],
                "Arrival_Time": time_str
            })
            
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_dist += dist_matrix[manager.IndexToNode(previous_index)][manager.IndexToNode(index)]
        
        node = manager.IndexToNode(index)
        route_nodes.append(node)
        time_var = time_dimension.CumulVar(index)
        arr_min = solution.Min(time_var)
        total_minutes = 10 * 60 + 30 + arr_min
        arr_hour = total_minutes // 60
        arr_minute = total_minutes % 60
        route_log += f"{location_names[node]} ({_t('log_return')} {arr_hour:02d}:{arr_minute:02d})"
        
        export_data.append({
            "Truck_ID": f"{depot_name}-{vehicle_id + 1}",
            "Stop_Order": order,
            "Location_Name": location_names[node],
            "Address": location_addresses[node],
            "Arrival_Time": f"{arr_hour:02d}:{arr_minute:02d}"
        })
        
        routes_text.append(route_log)
        total_dist_optimized += route_dist
        
        cache_key = tuple(route_nodes)
        if cache_key not in st.session_state.route_geometry_cache:
            st.session_state.route_geometry_cache[cache_key] = get_osrm_route_geometry(cache_key, all_locs_tuple)
        
        road_coords = st.session_state.route_geometry_cache[cache_key]
        is_road = len(road_coords) > len(route_nodes)
        map_polylines.append((road_coords, color, is_road))
        
    all_schools = set(range(2, len(locations)))
    dropped_schools = all_schools - visited_nodes
    
    baseline_dist = 0.0
    for i in range(2, 18, 2):
        baseline_dist += dist_matrix[0][i] + dist_matrix[i][i+1] + dist_matrix[i+1][0]
    baseline_dist += dist_matrix[0][18] * 2  
    for i in range(19, 29, 2):
        baseline_dist += dist_matrix[1][i] + dist_matrix[i][i+1] + dist_matrix[i+1][1]
    baseline_dist += dist_matrix[1][29] * 2  
        
    base_cost = baseline_dist * config.cost_per_km
    opt_cost = total_dist_optimized * config.cost_per_km
    savings_per_day = max(0, base_cost - opt_cost)
    savings_per_year = savings_per_day * 200

    return VRPResult(
        total_distance=total_dist_optimized,
        used_vehicles=used_vehicles,
        routes_text=routes_text,
        map_polylines=map_polylines,
        visited_nodes=visited_nodes,
        school_labels=school_labels,
        export_data=export_data,
        dropped_schools=dropped_schools,
        baseline_dist=baseline_dist,
        opt_cost=opt_cost,
        savings_per_day=savings_per_day,
        savings_per_year=savings_per_year
    )
