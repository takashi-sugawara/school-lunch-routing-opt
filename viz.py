import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from models import VRPResult, VRPConfig
from i18n import get_translator

def render_kpis(result: VRPResult, config: VRPConfig, location_names: list, lang: str):
    _t = get_translator(lang)
    num_vehicles = config.num_east_trucks + config.num_west_trucks
    
    st.markdown(_t("kpi_header"))
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(_t("kpi_trucks"), _t("metric_trucks_val", val=result.used_vehicles), _t("kpi_trucks_sub", total=num_vehicles), delta_color="off")
    
    if len(result.dropped_schools) > 0:
        dropped_names = [location_names[n] for n in result.dropped_schools]
        col2.metric(_t("kpi_drop_title"), f"{len(result.dropped_schools)}", help=_t("kpi_drop_sub"))
        st.error(_t("drop_error", schools=', '.join(dropped_names)))
    else:
        col2.metric(_t("kpi_success_title"), "28", _t("kpi_success_sub"))
    
    col3.metric(_t("kpi_dist"), f"{result.total_distance:.1f} km", _t("kpi_dist_sub", base=round(result.baseline_dist, 1)))
    col4.metric(_t("kpi_cost"), _t("metric_cost_val", val=f"{int(result.opt_cost):,}"), _t("kpi_cost_sub", saved=f"{int(result.savings_per_day):,}"))
    
    if lang == "ja":
        st.info(_t("saving_info", yearly_manen=int(result.savings_per_year / 10000)))
    else:
        st.info(_t("saving_info", yearly_formatted=f"{int(result.savings_per_year):,}"))

def render_map(result: VRPResult, locations: list, location_names: list, lang: str):
    _t = get_translator(lang)
    m = folium.Map(location=[35.710, 139.405], zoom_start=13)
    
    if result:
        for coords, color, is_road in result.map_polylines:
            folium.PolyLine(coords, color=color, weight=3, opacity=0.8, dash_array=None if is_road else "5 5").add_to(m)

    folium.Marker(locations[0], popup=location_names[0], icon=folium.Icon(color="red", icon="home")).add_to(m)
    folium.Marker(locations[1], popup=location_names[1], icon=folium.Icon(color="blue", icon="home")).add_to(m)
    
    for i, loc in enumerate(locations[2:]):
        node = i + 2
        color = "red" if node < 19 else "blue"
        
        if result:
            label = result.school_labels.get(node, "")
            if label:
                html = f'<div style="background-color: {color}; color: white; border-radius: 12px; width: 32px; height: 24px; text-align: center; line-height: 24px; font-size: 8pt; font-weight: bold; border: 1px solid white;">{label}</div>'
                folium.Marker(loc, popup=location_names[node], icon=folium.DivIcon(html=html, icon_anchor=(16, 12))).add_to(m)
            else:
                is_dropped = node in result.dropped_schools
                marker_color = "gray" if is_dropped else color
                opacity = 0.4 if is_dropped else 1.0
                popup_text = _t("popup_failed", name=location_names[node]) if is_dropped else location_names[node]
                folium.CircleMarker(loc, radius=6, color=marker_color, fill=True, fill_opacity=opacity, popup=popup_text).add_to(m)
        else:
            folium.CircleMarker(loc, radius=6, color=color, fill=True, popup=location_names[node]).add_to(m)
    
    st_folium(m, width=900, height=500)

def render_exports_and_details(result: VRPResult, lang: str):
    _t = get_translator(lang)
    if result.export_data:
        df_export = pd.DataFrame(result.export_data)
        csv_data = df_export.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Download Routing Schedule (CSV)",
            data=csv_data,
            file_name="routing_schedule.csv",
            mime="text/csv",
        )

    with st.expander(_t("expander_title")):
        for text in result.routes_text:
            st.markdown(text)
