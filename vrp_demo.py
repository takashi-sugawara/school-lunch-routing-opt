import streamlit as st
import pandas as pd
from models import VRPConfig
from i18n import get_translator
from data import generate_real_data, get_coordinates_only
from osrm import fetch_osrm_matrices
from routing import solve_vrp
from viz import render_kpis, render_map, render_exports_and_details

st.set_page_config(page_title="VRP Demo", layout="wide")

if "lang" not in st.session_state:
    st.session_state.lang = "ja"
if "run_opt" not in st.session_state:
    st.session_state.run_opt = False

lang_choice = st.sidebar.radio("🌐 Language / 言語", ["日本語", "English"])
new_lang = "ja" if lang_choice == "日本語" else "en"

if st.session_state.lang != new_lang:
    st.session_state.lang = new_lang
    st.session_state.run_opt = False
    st.rerun()

lang = st.session_state.lang
_t = get_translator(lang)

# Data Initialization
locations, location_names, location_addresses = generate_real_data(lang)
dist_matrix, base_duration_matrix, osrm_ok = fetch_osrm_matrices(get_coordinates_only())

# Main UI setup
if osrm_ok:
    st.success(_t("osrm_success"))
else:
    st.warning(_t("osrm_warning"))

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
        _t("col_lat"): [f"{loc[0]:.6f}" for loc in locations],
        _t("col_lon"): [f"{loc[1]:.6f}" for loc in locations],
        _t("col_area"): [_t("area_east_depot"), _t("area_west_depot")] + [_t("area_east")]*17 + [_t("area_west")]*11
    })
    st.dataframe(df_locations, width='stretch')

# Sidebar Configuration
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

# Main Execution Flow
if st.session_state.run_opt:
    with st.spinner(_t("spinner")):
        config = VRPConfig(
            num_east_trucks=num_east_trucks,
            num_west_trucks=num_west_trucks,
            weather_multiplier=weather_multiplier,
            cost_per_km=cost_per_km,
            search_time_limit=search_time_limit
        )
        
        result = solve_vrp(
            config, locations, location_names, location_addresses,
            dist_matrix, base_duration_matrix, lang
        )
        
        if result:
            with tab1:
                st.success(_t("success"))
                render_kpis(result, config, location_names, lang)
                render_map(result, locations, location_names, lang)
                render_exports_and_details(result, lang)
        else:
            with tab1:
                st.error(_t("fail_opt"))
                render_map(None, locations, location_names, lang)
else:
    with tab1:
        st.info(_t("info_start"))
        render_map(None, locations, location_names, lang)
