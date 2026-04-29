import streamlit as st
import math

def haversine(lat1, lon1, lat2, lon2):
    """2点間の緯度経度から距離(km)を計算する（ハベサイン公式）"""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@st.cache_data
def generate_real_data(lang="ja"):
    depots = {
        "East_Depot": [35.717028, 139.423011],
        "West_Depot": [35.719055, 139.390082]
    }
    east_schools = [
        # 小学校 8校
        [35.695321, 139.415102], [35.700145, 139.420883], [35.693892, 139.425034],
        [35.698213, 139.405991], [35.705674, 139.418229], [35.690441, 139.430115],
        [35.692338, 139.420776], [35.715891, 139.435442],
        # 中学校 9校
        [35.705112, 139.400554], [35.710893, 139.405667], [35.698445, 139.425331],
        [35.702991, 139.430218], [35.690556, 139.410993], [35.712334, 139.420112],
        [35.718882, 139.415664], [35.688221, 139.422557], [35.708553, 139.435889]
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
        [35.725114, 139.385223], [35.728991, 139.410556], [35.720334, 139.370889],
        [35.715556, 139.405112], [35.720887, 139.420445], [35.728221, 139.380778],
        [35.722665, 139.395332], [35.730112, 139.415994], [35.735443, 139.390221],
        [35.705889, 139.395667], [35.725776, 139.390114]
    ]
    
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

@st.cache_data
def get_coordinates_only():
    data, _, _ = generate_real_data("ja")
    return tuple(map(tuple, data))
