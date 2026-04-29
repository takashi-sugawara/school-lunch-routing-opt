import streamlit as st
import numpy as np
import requests
from data import haversine

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
                    dist_mat[i][j] = data["distances"][i][j] / 1000.0
                    dur_mat[i][j] = data["durations"][i][j] / 60.0
            return dist_mat, dur_mat, True
    except Exception:
        pass
        
    FALLBACK_SPEED_KM_PER_H = 20.0
    for i in range(n):
        for j in range(n):
            if i == j: continue
            d = haversine(locs[i][0], locs[i][1], locs[j][0], locs[j][1]) * 1.3
            dist_mat[i][j] = d
            dur_mat[i][j] = (d / FALLBACK_SPEED_KM_PER_H) * 60.0
    return dist_mat, dur_mat, False

@st.cache_data
def get_osrm_route_geometry(route_nodes_tuple, all_locs):
    locs = [all_locs[n] for n in route_nodes_tuple]
    coords_str = ";".join([f"{lon},{lat}" for lat, lon in locs])
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?geometries=geojson&overview=full"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get("code") == "Ok":
            geom = data["routes"][0]["geometry"]["coordinates"]
            return [[lat, lon] for lon, lat in geom]
    except Exception:
        pass
    return locs
