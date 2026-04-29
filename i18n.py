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
    "cost_slider_label": {"ja": "ガソリン代 / km (円)", "en": "Gasoline Cost / km (JPY)"},
    "osrm_success": {"ja": "✅ OSRM APIから正確な現実の道路網距離を取得しました。", "en": "✅ Fetched accurate real-world road distances from OSRM API."},
    "osrm_warning": {"ja": "⚠️ API制限またはエラーのため、直線距離（推定）で代替計算しています。", "en": "⚠️ Using estimated straight-line distances due to API limits or errors."}
}

def get_translator(lang: str):
    def _t(key, **kwargs):
        text = TEXTS.get(key, {}).get(lang, key)
        if kwargs:
            return text.format(**kwargs)
        return text
    return _t
