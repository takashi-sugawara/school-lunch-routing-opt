import streamlit as st
import pandas as pd
import numpy as np
import math
import folium
from streamlit_folium import st_folium
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import requests

# ---------------------------------------------------------
# 0. 多言語対応 (i18n) 辞書
# ---------------------------------------------------------
TEXTS = {
    "title": {
        "ja": "🚚 学校給食 配送ルート最適化デモ",
        "en": "🚚 School Lunch Delivery Routing Optimization"
    },
    "subtitle": {
        "ja": "立川市の東・西共同調理場から、管轄の小中学校28校へ給食を配送するシミュレーションです。",
        "en": "A simulation of delivering school lunches from Tachikawa's East and West Kitchens to 28 schools."
    },
    "tab_map": {"ja": "🗺️ シミュレーションマップ", "en": "🗺️ Simulation Map"},
    "tab_desc": {"ja": "📋 問題定義・制約条件", "en": "📋 Problem & Constraints"},
    "tab_data": {"ja": "🏫 拠点データ一覧", "en": "🏫 Location Data"},
    "desc_header": {"ja": "📋 今回の最適化シナリオについて", "en": "📋 Optimization Scenario Details"},
    "desc_body": {
        "ja": """
本デモは、立川市の実際の給食配送モデルをベースにした「時間枠付き複数拠点車両経路問題（MDVRPTW）」のシミュレーションです。
以下のビジネス要件（制約条件）をすべて満たしつつ、最もコストが安くなるルートを数理最適化エンジン（OR-Tools）が探索します。

### 🏫 配送エリアと対象校（立川市に固定）
* **東共同調理場（みんなのくるりんキッチン）**
  * 担当: 小学校8校、中学校9校（計17校）
  * 推定トラック稼働台数: 約10〜12台
* **西共同調理場**
  * 担当: 小学校11校
  * 推定トラック稼働台数: 約7〜8台
*(※デモの安定稼働のため、拠点の緯度経度はAPI取得ではなく固定値を使用しています)*

### ⏱️ 厳しい時間制約（Time Windows）
* **配送完了枠 [11:00 - 11:30]**: 学校の運用上、必ずこの30分間に配送を完了させる必要があります。
* **荷下ろし時間 [10分]**: 各学校での給食の積み下ろし作業に10分間を要します。
* **トラックの積載容量制限**: 1台のトラックにつき、最大 **2校分** までしか積載できません（配送後はデポに戻る必要があります）。
* **衛生管理基準（2時間ルール）**: 文部科学省の「調理終了から喫食開始まで2時間以内」を満たす必要があるため、トラックの出発可能時刻は **10:30以降** に制限されます。

### 💰 コストの算出基準
* トラックの燃費は 5km/L と仮定し、**立川市のガソリン代を 1リットル160円** として、最適化によるガソリン代の節約額を算出しています。
        """,
        "en": """
This demo is a simulation of the "Multi-Depot Vehicle Routing Problem with Time Windows (MDVRPTW)" based on the actual school lunch delivery model in Tachikawa City.
The mathematical optimization engine (OR-Tools) will find the most cost-effective routes while strictly satisfying all business constraints below.

### 🏫 Delivery Areas and Target Schools
* **East Joint Kitchen**
  * Targets: 8 Elementary Schools, 9 Junior High Schools (Total: 17)
  * Estimated active trucks: 10-12
* **West Joint Kitchen**
  * Targets: 11 Elementary Schools
  * Estimated active trucks: 7-8
*(Note: To ensure demo stability, location coordinates are hardcoded rather than fetched via API)*

### ⏱️ Strict Time Constraints (Time Windows)
* **Delivery Window [11:00 - 11:30]**: Deliveries must be completed exactly within this 30-minute window due to school schedules.
* **Unloading Time [10 mins]**: It takes 10 minutes to unload the lunches at each school.
* **Capacity Constraint**: A single truck can carry meals for a maximum of **2 schools** (must return to depot afterwards).
* **Hygiene Standard (2-Hour Rule)**: To meet the Ministry of Education's requirement of "eating within 2 hours after cooking finishes", trucks cannot depart before **10:30**.

### 💰 Cost Calculation Basis
* Assuming a truck fuel efficiency of 5km/L and **a gasoline price of 160 JPY/L**, we calculate the monetary savings achieved by the route optimization.
        """
    },
    "data_header": {"ja": "🏫 拠点データ一覧", "en": "🏫 Location Data List"},
    "sidebar_header": {"ja": "🔧 シミュレーション設定", "en": "🔧 Simulation Settings"},
    "weather_label": {"ja": "天候・路面状況", "en": "Weather / Traffic Conditions"},
    "trucks_header": {"ja": "**🚚 稼働トラック数（ドライバー出勤数）**", "en": "**🚚 Active Trucks (Driver Availability)**"},
    "east_slider": {"ja": "東共同調理場 (通常12台)", "en": "East Kitchen (Default: 12)"},
    "west_slider": {"ja": "西共同調理場 (通常8台)", "en": "West Kitchen (Default: 8)"},
    "search_time_slider": {"ja": "最適化エンジン探索時間 (秒)", "en": "Optimization Engine Search Time (sec)"},
    "btn_run": {"ja": "🚀 最適化を実行する", "en": "🚀 Run Optimization"},
    "spinner": {"ja": "数理最適化エンジンが最良ルートを探索中...", "en": "The mathematical optimization engine is searching for the best routes..."},
    "success": {"ja": "✅ 最適化が完了しました！", "en": "✅ Optimization Complete!"},
    "kpi_header": {"ja": "### 📊 コスト削減・最適化ダッシュボード", "en": "### 📊 Cost Savings & Optimization Dashboard"},
    "kpi_trucks": {"ja": "稼働トラック台数", "en": "Active Trucks"},
    "kpi_trucks_sub": {"ja": "用意した {total}台中", "en": "{total} trucks available"},
    "kpi_drop_title": {"ja": "⚠️ 配送失敗(遅延)校数", "en": "⚠️ Failed Deliveries (Delayed)"},
    "kpi_drop_sub": {"ja": "時間枠に間に合いません", "en": "Missed Time Window"},
    "drop_error": {"ja": "以下の学校は配送できませんでした（原因: トラック不足、時間制約過剰、または地理的偏り）: {schools}", "en": "Delivery abandoned for the following schools (Causes: Truck shortage, strict time windows, or geographic bias): {schools}"},
    "kpi_success_title": {"ja": "✨ 配送完了校数", "en": "✨ Successful Deliveries"},
    "kpi_success_sub": {"ja": "全校 11:30までに完了！", "en": "All 28 schools delivered by 11:30!"},
    "kpi_dist": {"ja": "総走行距離", "en": "Total Distance"},
    "kpi_dist_sub": {"ja": "ピストン輸送だと {base} km", "en": "{base} km if round-trip"},
    "kpi_cost": {"ja": "💰 1日あたりのガソリン代", "en": "💰 Daily Gasoline Cost"},
    "kpi_cost_sub": {"ja": "-{saved} 円節約！", "en": "Saved {saved} JPY!"},
    "saving_info": {
        "ja": "💡 もしこの最適化を導入した場合、単純なピストン輸送に比べて **年間約 {yearly_manen} 万円** のガソリン代（およびそれに比例するCO2排出）を削減できます。",
        "en": "💡 Implementing this optimization saves approximately **{yearly_formatted} JPY per year** in gasoline costs (and proportional CO2 emissions) compared to simple round-trips."
    },
    "expander_title": {"ja": "📝 各トラックの配送スケジュール詳細（クリックで展開）", "en": "📝 Detailed Delivery Schedule per Truck (Click to expand)"},
    "fail_opt": {"ja": "最適解が見つかりませんでした。条件が厳しすぎる可能性があります（トラック台数を増やしてみてください）。", "en": "No optimal solution found. The constraints might be too strict (try increasing the number of trucks)."},
    "info_start": {"ja": "左側のサイドバーで条件を設定し、「🚀 最適化を実行する」ボタンを押してください。", "en": "Set the conditions in the left sidebar and click '🚀 Run Optimization'."},
    "col_name": {"ja": "拠点名", "en": "Location Name"},
    "col_address": {"ja": "住所", "en": "Address"},
    "col_lat": {"ja": "緯度", "en": "Lat"},
    "col_lon": {"ja": "経度", "en": "Lon"},
    "col_area": {"ja": "担当エリア", "en": "Area"},
    "area_east_depot": {"ja": "デポ(東)", "en": "Depot (East)"},
    "area_west_depot": {"ja": "デポ(西)", "en": "Depot (West)"},
    "area_east": {"ja": "東エリア", "en": "East Area"},
    "area_west": {"ja": "西エリア", "en": "West Area"},
    "depot_east": {"ja": "東", "en": "East"},
    "depot_west": {"ja": "西", "en": "West"},
    "log_return": {"ja": "帰還", "en": "Return"},
    "log_truck": {"ja": "**🚚 [{depot_name}] トラック {v_id}** : ", "en": "**🚚 [{depot_name}] Truck {v_id}** : "},
    "metric_trucks_val": {"ja": "{val}", "en": "{val} trucks"},
    "metric_cost_val": {"ja": "{val}", "en": "{val} JPY"},
    "popup_failed": {"ja": "⚠️ {name}（配送失敗）", "en": "⚠️ {name} (Failed)"},
    "cost_slider_label": {"ja": "ガソリン代 / km (円)", "en": "Gasoline Cost / km (JPY)"}
}

# ---------------------------------------------------------
# 1. ユーティリティ・データ準備
# ---------------------------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    """2点間の緯度経度から距離(km)を計算する（ハベサイン公式）"""
    R = 6371.0 # 地球の半径(km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@st.cache_data
def generate_real_data(lang="ja"):
    depots = {
        "East_Depot": [35.7170, 139.4230],
        "West_Depot": [35.7190, 139.3900]
    }
    east_schools = [
        # 小学校 8校
        [35.695, 139.415], [35.700, 139.420], [35.693, 139.425],
        [35.698, 139.405], [35.705, 139.418], [35.690, 139.430],
        [35.692, 139.420], [35.715, 139.435],
        # 中学校 9校 (ダミーからよりリアルな分散座標へ)
        [35.705, 139.400], [35.710, 139.405], [35.698, 139.425],
        [35.702, 139.430], [35.690, 139.410], [35.712, 139.420],
        [35.718, 139.415], [35.688, 139.422], [35.708, 139.435]
    ]
    if lang == "ja":
        east_names = [
            "第一小", "第二小", "第三小", "第四小", "第五小", "第六小", "第七小", "第八小",
            "第一中", "第二中", "第三中", "第四中", "第五中", "第六中", "第七中", "第八中", "第九中"
        ]
        west_names = [
            "第九小", "第十小", "西砂小", "南砂小", "幸小", 
            "松中小", "大山小", "柏小", "上砂川小", "新生小", "若葉台小"
        ]
        depot_names = ["東共同調理場", "西共同調理場"]
    else:
        east_names = [
            "1st ES", "2nd ES", "3rd ES", "4th ES", "5th ES", "6th ES", "7th ES", "8th ES",
            "1st JHS", "2nd JHS", "3rd JHS", "4th JHS", "5th JHS", "6th JHS", "7th JHS", "8th JHS", "9th JHS"
        ]
        west_names = [
            "9th ES", "10th ES", "Nishisuna ES", "Minamisuna ES", "Saiwai ES", 
            "Matsunaka ES", "Oyama ES", "Kashiwa ES", "Kamisunagawa ES", "Shinsei ES", "Wakabadai ES"
        ]
        depot_names = ["East Joint Kitchen", "West Joint Kitchen"]
        
    west_schools = [
        [35.725, 139.385], [35.728, 139.410], [35.720, 139.370],
        [35.715, 139.405], [35.720, 139.420], [35.728, 139.380],
        [35.722, 139.395], [35.730, 139.415], [35.735, 139.390],
        [35.705, 139.395], [35.725, 139.390]
    ]
    
    # Addresses stay in Japanese to represent real Japan addresses, but we can suffix them in English
    depot_addresses = ["立川市泉町1156-14 (Izumi-cho)", "立川市一番町6-10-1 (Ichiban-cho)"]
    east_addresses = [
        "立川市柴崎町2-20-3", "立川市曙町3-23-1", "立川市錦町3-4-1", "立川市富士見町4-4-1",
        "立川市高松町1-12-25", "立川市羽衣町2-29-22", "立川市錦町5-6-43", "立川市幸町2-1-1",
        "立川市柴崎町1-3-4", "立川市曙町3-29-46", "立川市羽衣町3-25-6", "立川市幸町5-49-1",
        "立川市上砂町3-27-1", "立川市泉町786-16", "立川市西砂町6-28-3", "立川市富士見町7-24-1", "立川市若葉町3-19-5"
    ]
    west_addresses = [
        "立川市上砂町2-18-1", "立川市柏町1-31-1", "立川市西砂町2-34-2", "立川市栄町2-2-1",
        "立川市幸町5-68-1", "立川市一番町5-8-5", "立川市上砂町1-5-33", "立川市柏町4-8-4",
        "立川市上砂町5-12-2", "立川市富士見町6-69-1", "立川市若葉町1-13-1"
    ]
    
    locations = [depots["East_Depot"], depots["West_Depot"]] + east_schools + west_schools
    names = depot_names + east_names + west_names
    addresses = depot_addresses + east_addresses + west_addresses
    return locations, names, addresses

# ---------------------------------------------------------
# 2. UI と サイドバー
# ---------------------------------------------------------
st.set_page_config(page_title="VRP Demo", layout="wide")

# 初期化
if "lang" not in st.session_state:
    st.session_state.lang = "ja"
if "run_opt" not in st.session_state:
    st.session_state.run_opt = False

# 言語設定
lang_choice = st.sidebar.radio("🌐 Language / 言語", ["日本語", "English"])
new_lang = "ja" if lang_choice == "日本語" else "en"

if st.session_state.lang != new_lang:
    st.session_state.lang = new_lang
    st.session_state.run_opt = False
    st.rerun()

lang = st.session_state.lang

# Helper function for translations
def _t(key, **kwargs):
    text = TEXTS.get(key, {}).get(lang, key)
    if kwargs:
        return text.format(**kwargs)
    return text

locations, location_names, location_addresses = generate_real_data(lang)

@st.cache_data
def fetch_osrm_matrices(locs):
    n = len(locs)
    dist_mat = np.zeros((n, n))
    dur_mat = np.zeros((n, n))
    
    coords_str = ";".join([f"{lon},{lat}" for lat, lon in locs])
    url = f"http://router.project-osrm.org/table/v1/driving/{coords_str}?annotations=duration,distance"
    
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("code") == "Ok" and "distances" in data and "durations" in data:
            for i in range(n):
                for j in range(n):
                    # meters to km, seconds to minutes
                    dist_mat[i][j] = data["distances"][i][j] / 1000.0
                    dur_mat[i][j] = data["durations"][i][j] / 60.0
            return dist_mat, dur_mat, True
    except Exception:
        pass
        
    # Fallback to haversine if API fails or blocks
    FALLBACK_SPEED_KM_PER_H = 20.0
    for i in range(n):
        for j in range(n):
            if i == j: continue
            d = haversine(locs[i][0], locs[i][1], locs[j][0], locs[j][1]) * 1.3
            dist_mat[i][j] = d
            dur_mat[i][j] = (d / FALLBACK_SPEED_KM_PER_H) * 60.0
    return dist_mat, dur_mat, False

@st.cache_data
def get_coordinates_only():
    data, _, _ = generate_real_data("ja")  # 座標データ自体は言語共通
    return tuple(map(tuple, data))

@st.cache_data
def get_osrm_route_geometry(route_nodes_tuple, all_locs):
    locs = [all_locs[n] for n in route_nodes_tuple]
    coords_str = ";".join([f"{lon},{lat}" for lat, lon in locs])
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?geometries=geojson&overview=full"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get("code") == "Ok":
            # geojson coordinates are [lon, lat], folium expects [lat, lon]
            geom = data["routes"][0]["geometry"]["coordinates"]
            return [[lat, lon] for lon, lat in geom]
    except Exception:
        pass
    # OSRM失敗時やタイムアウト時は、ノード座標をそのまま返す（地図上では直線で描画される）
    return locs

# OSRM APIを利用して現実の道路網に基づく距離・時間マトリックスを取得し、キャッシュ
dist_matrix, base_duration_matrix, osrm_ok = fetch_osrm_matrices(get_coordinates_only())
num_locations = len(locations)

if not osrm_ok:
    st.warning("OSRM APIに接続できませんでした。直線距離で代替しています。")

st.title(_t("title"))
st.markdown(_t("subtitle"))

tab1, tab2, tab3 = st.tabs([_t("tab_map"), _t("tab_desc"), _t("tab_data")])

with tab2:
    st.header(_t("desc_header"))
    st.markdown(_t("desc_body"))

with tab3:
    st.header(_t("data_header"))
    df_locations = pd.DataFrame({
        "ID": range(len(location_names)),
        _t("col_name"): location_names,
        _t("col_address"): location_addresses,
        _t("col_lat"): [loc[0] for loc in locations],
        _t("col_lon"): [loc[1] for loc in locations],
        _t("col_area"): [_t("area_east_depot"), _t("area_west_depot")] + [_t("area_east")]*17 + [_t("area_west")]*11
    })
    st.dataframe(df_locations, use_container_width=True)

st.sidebar.header(_t("sidebar_header"))
weather_options = {
    "ja": {"☀️ 晴れ (通常)": 1.0, "☔️ 雨 (移動時間1.2倍)": 1.2, "⛄️ 雪 (移動時間1.5倍)": 1.5},
    "en": {"☀️ Sunny (Normal)": 1.0, "☔️ Rain (1.2x Travel Time)": 1.2, "⛄️ Snow (1.5x Travel Time)": 1.5}
}
selected_weather = st.sidebar.selectbox(_t("weather_label"), list(weather_options[lang].keys()))
weather_multiplier = weather_options[lang][selected_weather]

st.sidebar.markdown(_t("trucks_header"))
num_east_trucks = st.sidebar.slider(_t("east_slider"), min_value=5, max_value=15, value=12)
num_west_trucks = st.sidebar.slider(_t("west_slider"), min_value=3, max_value=10, value=8)
search_time_limit = st.sidebar.slider(_t("search_time_slider"), min_value=1, max_value=10, value=3)
cost_per_km = st.sidebar.number_input(_t("cost_slider_label"), min_value=10, max_value=100, value=32)



if st.sidebar.button(_t("btn_run"), type="primary"):
    st.session_state.run_opt = True

if st.session_state.run_opt:
    with st.spinner(_t("spinner")):
        # ---------------------------------------------------------
        # 3. マトリックス計算とOR-Toolsモデル構築
        time_matrix = np.zeros((num_locations, num_locations), dtype=int)
        
        SERVICE_TIME = 10 
        
        for i in range(num_locations):
            for j in range(num_locations):
                if i == j: continue
                # OSRMの基準所要時間に、天候倍率を掛ける
                travel_time = base_duration_matrix[i][j] * weather_multiplier
                service = SERVICE_TIME if i >= 2 else 0
                time_matrix[i][j] = int(travel_time + service)

        num_vehicles = num_east_trucks + num_west_trucks
        starts = [0] * num_east_trucks + [1] * num_west_trucks
        ends = [0] * num_east_trucks + [1] * num_west_trucks

        manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, starts, ends)
        routing = pywrapcp.RoutingModel(manager)

        def time_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return time_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(time_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # 容量制約 (1台につき最大2校分)
        demands = [0, 0] + [1] * 28
        def demand_callback(from_index):
            return demands[manager.IndexToNode(from_index)]
        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,
            [2] * num_vehicles,
            True,
            'Capacity'
        )

        routing.AddDimension(
            transit_callback_index,
            30,  
            180, 
            False, 
            'Time'
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
        search_parameters.time_limit.seconds = search_time_limit

        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            # ---------------------------------------------------------
            # 4. 結果の集計と可視化
            # ---------------------------------------------------------
            total_dist_optimized = 0.0
            used_vehicles = 0
            routes_text = []
            map_polylines = []
            visited_nodes = set()
            school_labels = {}
            
            for vehicle_id in range(num_vehicles):
                index = routing.Start(vehicle_id)
                route_dist = 0.0
                route_nodes = []
                
                if routing.IsEnd(solution.Value(routing.NextVar(index))):
                    continue
                    
                used_vehicles += 1
                is_east = (vehicle_id < num_east_trucks)
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
                    
                    previous_index = index
                    index = solution.Value(routing.NextVar(index))
                    # 次のノードへの距離を加算（最後の学校から帰還デポまでの距離もここで加算されます）
                    route_dist += dist_matrix[manager.IndexToNode(previous_index)][manager.IndexToNode(index)]
                
                node = manager.IndexToNode(index)
                route_nodes.append(node)
                time_var = time_dimension.CumulVar(index)
                arr_min = solution.Min(time_var)
                total_minutes = 10 * 60 + 30 + arr_min
                arr_hour = total_minutes // 60
                arr_minute = total_minutes % 60
                route_log += f"{location_names[node]} ({_t('log_return')} {arr_hour:02d}:{arr_minute:02d})"
                
                routes_text.append(route_log)
                total_dist_optimized += route_dist
                
                # 直線ではなく実際の道路経路を取得して描画（セッションキャッシュ活用）
                if "route_geometry_cache" not in st.session_state:
                    st.session_state.route_geometry_cache = {}
                
                cache_key = tuple(route_nodes)
                if cache_key not in st.session_state.route_geometry_cache:
                    st.session_state.route_geometry_cache[cache_key] = \
                        get_osrm_route_geometry(cache_key, get_coordinates_only())
                
                road_coords = st.session_state.route_geometry_cache[cache_key]
                is_road = len(road_coords) > len(route_nodes)  # 経由点が増えていればOSRM成功（道路経路）
                map_polylines.append((road_coords, color, is_road))
                
            all_schools = set(range(2, len(locations)))
            dropped_schools = all_schools - visited_nodes
            
            # ベースライン計算（容量2を考慮し、2件ずつペアで巡回するナイーブな配送モデル）
            baseline_dist = 0.0
            # 東エリア (2〜18)
            for i in range(2, 18, 2):
                baseline_dist += dist_matrix[0][i] + dist_matrix[i][i+1] + dist_matrix[i+1][0]
            baseline_dist += dist_matrix[0][18] * 2  # 余りの1校はピストン
            
            # 西エリア (19〜29)
            for i in range(19, 29, 2):
                baseline_dist += dist_matrix[1][i] + dist_matrix[i][i+1] + dist_matrix[i+1][1]
            baseline_dist += dist_matrix[1][29] * 2  # 余りの1校はピストン
                
            base_cost = baseline_dist * cost_per_km
            opt_cost = total_dist_optimized * cost_per_km
            savings_per_day = max(0, base_cost - opt_cost)
            savings_per_year = savings_per_day * 200

            with tab1:
                st.success(_t("success"))
                
                st.markdown(_t("kpi_header"))
                col1, col2, col3, col4 = st.columns(4)
                col1.metric(_t("kpi_trucks"), _t("metric_trucks_val", val=used_vehicles), _t("kpi_trucks_sub", total=num_vehicles), delta_color="off")
                
                if len(dropped_schools) > 0:
                    dropped_names = [location_names[n] for n in dropped_schools]
                    col2.metric(_t("kpi_drop_title"), f"{len(dropped_schools)}", help=_t("kpi_drop_sub"))
                    st.error(_t("drop_error", schools=', '.join(dropped_names)))
                else:
                    col2.metric(_t("kpi_success_title"), "28", _t("kpi_success_sub"))
                
                col3.metric(_t("kpi_dist"), f"{total_dist_optimized:.1f} km", _t("kpi_dist_sub", base=round(baseline_dist, 1)))
                col4.metric(_t("kpi_cost"), _t("metric_cost_val", val=f"{int(opt_cost):,}"), _t("kpi_cost_sub", saved=f"{int(savings_per_day):,}"))
                
                if lang == "ja":
                    st.info(_t("saving_info", yearly_manen=int(savings_per_year / 10000)))
                else:
                    st.info(_t("saving_info", yearly_formatted=f"{int(savings_per_year):,}"))

                m = folium.Map(location=[35.710, 139.405], zoom_start=13)
                
                for coords, color, is_road in map_polylines:
                    folium.PolyLine(coords, color=color, weight=3, opacity=0.8, dash_array=None if is_road else "5 5").add_to(m)

                folium.Marker(locations[0], popup=location_names[0], icon=folium.Icon(color="red", icon="home")).add_to(m)
                folium.Marker(locations[1], popup=location_names[1], icon=folium.Icon(color="blue", icon="home")).add_to(m)
                for i, loc in enumerate(locations[2:30]):
                    node = i + 2
                    color = "red" if node < 19 else "blue"
                    label = school_labels.get(node, "")
                    if label:
                        html = f'<div style="background-color: {color}; color: white; border-radius: 12px; width: 32px; height: 24px; text-align: center; line-height: 24px; font-size: 8pt; font-weight: bold; border: 1px solid white;">{label}</div>'
                        folium.Marker(loc, popup=location_names[node], icon=folium.DivIcon(html=html, icon_anchor=(16, 12))).add_to(m)
                    else:
                        is_dropped = node in dropped_schools
                        marker_color = "gray" if is_dropped else color
                        opacity = 0.4 if is_dropped else 1.0
                        popup_text = _t("popup_failed", name=location_names[node]) if is_dropped else location_names[node]
                        folium.CircleMarker(loc, radius=6, color=marker_color, fill=True, fill_opacity=opacity, popup=popup_text).add_to(m)
                
                st_folium(m, width=900, height=500)

                with st.expander(_t("expander_title")):
                    for text in routes_text:
                        st.markdown(text)
        else:
            st.error(_t("fail_opt"))
else:
    with tab1:
        st.info(_t("info_start"))
        m = folium.Map(location=[35.710, 139.405], zoom_start=13)
        folium.Marker(locations[0], popup=location_names[0], icon=folium.Icon(color="red", icon="home")).add_to(m)
        folium.Marker(locations[1], popup=location_names[1], icon=folium.Icon(color="blue", icon="home")).add_to(m)
        for i, loc in enumerate(locations[2:30]):
            node = i + 2
            color = "red" if node < 19 else "blue"
            folium.CircleMarker(loc, radius=6, color=color, fill=True, popup=location_names[node]).add_to(m)
        st_folium(m, width=900, height=500)
