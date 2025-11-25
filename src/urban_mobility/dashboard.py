"""
Urban Mobility Live - V6 REFINED
Professional Light Theme with Smooth Animations

Features:
- Light gray and white color scheme
- Smooth animations on all interactions
- Loading animation with vehicle icons
- Map persistence (no flickering)
- Route filter on map
- Fully usable and complete interface
"""

import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import st_folium
import plotly.express as px
from datetime import datetime
import json
from collections import defaultdict
import random
import time
import hashlib

try:
    from urban_mobility.pipeline import UrbanMobilityPipeline, TransportType
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from pipeline import UrbanMobilityPipeline, TransportType

st.set_page_config(
    page_title="Urban Mobility Live",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Translations
TRANSLATIONS = {
    'en': {
        'title': 'Urban Mobility Live',
        'subtitle': 'Real-Time Transit Intelligence',
        'live_badge': 'LIVE',
        'select_city': 'Select City',
        'update_data': 'Update Data',
        'last_update': 'Last update',
        'loading': 'Loading',
        'metrics': 'Overview',
        'total_stops': 'Total Stops',
        'accessible': 'Accessible',
        'with_shelter': 'With Shelter',
        'with_routes': 'With Routes',
        'map_view': 'Live Map',
        'routes_lines': 'Routes & Lines',
        'vehicle_tracker': 'Vehicle Tracker',
        'filter_route_map': 'Filter Route on Map',
        'all_routes': 'All Routes',
        'show_all': 'Show All Routes',
        'search_route': 'Search for line',
        'select_routes': 'Select routes to display',
        'vehicle': 'Vehicle',
        'last_stop': 'Last Stop',
        'current_stop': 'Current',
        'next_stop': 'Next Stop',
        'eta': 'ETA',
        'minutes': 'min',
        'stops': 'stops',
        'operator': 'Operator',
        'active_vehicles': 'Active Vehicles',
    },
    'pt': {
        'title': 'Urban Mobility Live',
        'subtitle': 'Inteligência de Transporte em Tempo Real',
        'live_badge': 'AO VIVO',
        'select_city': 'Selecionar Cidade',
        'update_data': 'Atualizar Dados',
        'last_update': 'Última atualização',
        'loading': 'Carregando',
        'metrics': 'Visão Geral',
        'total_stops': 'Total de Paradas',
        'accessible': 'Acessível',
        'with_shelter': 'Com Abrigo',
        'with_routes': 'Com Rotas',
        'map_view': 'Mapa ao Vivo',
        'routes_lines': 'Rotas e Linhas',
        'vehicle_tracker': 'Rastreador de Veículos',
        'filter_route_map': 'Filtrar Rota no Mapa',
        'all_routes': 'Todas as Rotas',
        'show_all': 'Mostrar Todas',
        'search_route': 'Buscar linha',
        'select_routes': 'Selecione rotas para exibir',
        'vehicle': 'Veículo',
        'last_stop': 'Última Parada',
        'current_stop': 'Atual',
        'next_stop': 'Próxima',
        'eta': 'Previsão',
        'minutes': 'min',
        'stops': 'paradas',
        'operator': 'Operador',
        'active_vehicles': 'Veículos Ativos',
    }
}

def t(key, lang='en'):
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

# Professional Light Theme CSS with Animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Light Professional Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }
    
    /* Header */
    .header-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        display: flex;
        align-items: center;
        justify-content: space-between;
        animation: slideDown 0.6s ease-out;
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .header-title {
        color: #2c3e50;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .header-subtitle {
        color: #7f8c8d;
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }
    
    /* Live Indicator */
    .live-indicator {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        background: #10b981;
        padding: 0.5rem 1.2rem;
        border-radius: 50px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }
        50% {
            box-shadow: 0 4px 20px rgba(16, 185, 129, 0.5);
        }
    }
    
    .live-dot {
        width: 8px;
        height: 8px;
        background: white;
        border-radius: 50%;
        animation: blink 1.5s infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    .live-text {
        color: white;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Language Buttons - VISIBLE TEXT */
    .stButton button {
        background: white !important;
        color: #2c3e50 !important;
        border: 2px solid #e0e6ed !important;
        padding: 0.6rem 1.2rem !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
    }
    
    .stButton button:hover {
        background: #667eea !important;
        color: white !important;
        border-color: #667eea !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton button:active {
        transform: translateY(0) !important;
    }
    
    /* Cards */
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 1.8rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        border: 1px solid rgba(0, 0, 0, 0.05);
        animation: fadeInUp 0.5s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .metric-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.15);
        border-color: #667eea;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #7f8c8d;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-change {
        color: #10b981;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }
    
    /* Route Cards */
    .route-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .route-card:hover {
        transform: translateX(8px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2);
        background: #f8f9ff;
    }
    
    .route-number {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.1rem;
        min-width: 60px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Vehicle Cards */
    .vehicle-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        animation: fadeIn 0.4s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .vehicle-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    }
    
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        animation: fadeIn 0.3s ease-out;
    }
    
    .status-active {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-transit {
        background: #fef3c7;
        color: #92400e;
    }
    
    /* Loading Animation */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    }
    
    .loading-icons {
        display: flex;
        gap: 2rem;
        font-size: 3rem;
        margin-bottom: 1.5rem;
    }
    
    .loading-icon {
        animation: bounce 1.5s infinite;
    }
    
    .loading-icon:nth-child(1) {
        animation-delay: 0s;
    }
    
    .loading-icon:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .loading-icon:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes bounce {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-20px);
        }
    }
    
    .loading-text {
        color: #667eea;
        font-size: 1.2rem;
        font-weight: 600;
        animation: pulse 1.5s infinite;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: white;
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        color: #7f8c8d;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #f8f9ff;
        color: #667eea;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
    }
    
    [data-testid="stSidebar"] h2 {
        color: #2c3e50;
        font-weight: 700;
    }
    
    /* Inputs */
    .stTextInput input, .stSelectbox select {
        background: white !important;
        border: 2px solid #e0e6ed !important;
        border-radius: 10px !important;
        color: #2c3e50 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Stop Info Grid */
    .stop-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
        margin-top: 1rem;
    }
    
    .stop-item {
        background: #f8f9ff;
        padding: 0.8rem;
        border-radius: 8px;
        border: 1px solid #e0e6ed;
        transition: all 0.3s ease;
    }
    
    .stop-item:hover {
        background: white;
        border-color: #667eea;
        transform: translateY(-2px);
    }
    
    .stop-label {
        color: #7f8c8d;
        font-size: 0.7rem;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    
    .stop-name {
        color: #2c3e50;
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5568d3 0%, #6a3f8d 100%);
    }
</style>
""", unsafe_allow_html=True)


def extract_route_name(route_str):
    """Extract readable route name"""
    if not route_str:
        return "Unknown"
    route_str = str(route_str).strip()
    if route_str.isdigit():
        return f"Line {route_str}"
    return route_str


def generate_route_polyline(stops, route_name):
    """Generate polyline for route"""
    route_stops = [s for s in stops if route_name in (s.routes or [])]
    if len(route_stops) < 2:
        return None
    
    sorted_stops = [route_stops[0]]
    remaining = route_stops[1:]
    
    while remaining:
        last = sorted_stops[-1]
        nearest = min(remaining, key=lambda s: 
                     ((s.latitude - last.latitude)**2 + (s.longitude - last.longitude)**2)**0.5)
        sorted_stops.append(nearest)
        remaining.remove(nearest)
    
    return [(s.latitude, s.longitude) for s in sorted_stops], sorted_stops


def simulate_vehicle_position(route_points, route_stops, vehicle_id, total_vehicles):
    """Simulate vehicle with stops info"""
    if not route_points or len(route_points) < 2:
        return None
    
    progress = (vehicle_id / total_vehicles + (time.time() % 60) / 600) % 1.0
    total_segments = len(route_points) - 1
    current_segment = int(progress * total_segments)
    
    if current_segment >= total_segments:
        current_segment = total_segments - 1
    
    last_stop_idx = current_segment
    next_stop_idx = min(current_segment + 1, len(route_stops) - 1)
    
    last_stop = route_stops[last_stop_idx].name if last_stop_idx < len(route_stops) else "Unknown"
    next_stop = route_stops[next_stop_idx].name if next_stop_idx < len(route_stops) else "Terminal"
    
    local_progress = (progress * total_segments) - current_segment
    p1 = route_points[current_segment]
    p2 = route_points[min(current_segment + 1, len(route_points) - 1)]
    
    lat = p1[0] + (p2[0] - p1[0]) * local_progress
    lon = p1[1] + (p2[1] - p1[1]) * local_progress
    
    if local_progress < 0.1:
        current_stop = last_stop
        status = "At Stop"
        eta = 0
    elif local_progress > 0.9:
        current_stop = next_stop
        status = "Arriving"
        eta = 1
    else:
        current_stop = last_stop
        status = "In Transit"
        eta = random.randint(2, 8)
    
    return {
        'position': (lat, lon),
        'last_stop': last_stop,
        'current_stop': current_stop,
        'next_stop': next_stop,
        'status': status,
        'eta': eta
    }


def create_persistent_map(stops, center_lat, center_lon, selected_routes=None, show_vehicles=True, lang='en'):
    """Create map with persistence - no flickering"""
    
    # Generate a unique key for map based on data
    map_key = f"{center_lat}_{center_lon}_{len(stops)}_{'-'.join(selected_routes or [])}"
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles='CartoDB Positron'  # Light theme
    )
    
    config = {
        TransportType.BUS: {'color': '#667eea', 'emoji': '🚌'},
        TransportType.SUBWAY: {'color': '#3b82f6', 'emoji': '🚇'},
        TransportType.TRAM: {'color': '#f59e0b', 'emoji': '🚊'},
        TransportType.TRAIN: {'color': '#8b5cf6', 'emoji': '🚆'},
        TransportType.FERRY: {'color': '#06b6d4', 'emoji': '⛴️'}
    }
    
    routes_group = folium.FeatureGroup(name='🛤️ Routes')
    stops_group = folium.FeatureGroup(name='🚏 Stops')
    vehicles_group = folium.FeatureGroup(name='🚍 Vehicles')
    
    routes_dict = defaultdict(list)
    for stop in stops:
        if stop.routes:
            for route in stop.routes:
                routes_dict[route].append(stop)
    
    route_colors = ['#667eea', '#764ba2', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
    
    routes_to_draw = selected_routes if selected_routes else list(routes_dict.keys())[:10]
    
    if 'vehicles' not in st.session_state:
        st.session_state.vehicles = []
    st.session_state.vehicles = []
    
    for idx, route_name in enumerate(routes_to_draw):
        if route_name not in routes_dict:
            continue
            
        result = generate_route_polyline(stops, route_name)
        if not result:
            continue
            
        route_points, ordered_stops = result
        color = route_colors[idx % len(route_colors)]
        
        folium.PolyLine(
            route_points,
            color=color,
            weight=5,
            opacity=0.8,
            popup=f"<b>{extract_route_name(route_name)}</b>",
            tooltip=extract_route_name(route_name)
        ).add_to(routes_group)
        
        folium.CircleMarker(
            route_points[0],
            radius=10,
            color='white',
            fillColor='#10b981',
            fillOpacity=1,
            weight=3
        ).add_to(routes_group)
        
        folium.CircleMarker(
            route_points[-1],
            radius=10,
            color='white',
            fillColor='#ef4444',
            fillOpacity=1,
            weight=3
        ).add_to(routes_group)
        
        if show_vehicles and len(route_points) > 2:
            num_vehicles = random.randint(2, 4)
            for v_id in range(num_vehicles):
                vehicle_info = simulate_vehicle_position(route_points, ordered_stops, v_id, num_vehicles)
                if vehicle_info:
                    pos = vehicle_info['position']
                    
                    st.session_state.vehicles.append({
                        'id': f"{route_name}-V{v_id+1}",
                        'route': route_name,
                        'route_display': extract_route_name(route_name),
                        'last_stop': vehicle_info['last_stop'],
                        'current_stop': vehicle_info['current_stop'],
                        'next_stop': vehicle_info['next_stop'],
                        'status': vehicle_info['status'],
                        'eta': vehicle_info['eta']
                    })
                    
                    folium.Marker(
                        pos,
                        icon=folium.DivIcon(html=f'<div style="font-size: 28px;">🚌</div>'),
                        popup=f"<b>{extract_route_name(route_name)} - V{v_id+1}</b>",
                        tooltip=f"{extract_route_name(route_name)}"
                    ).add_to(vehicles_group)
    
    for stop in stops:
        c = config.get(stop.transport_type, config[TransportType.BUS])
        folium.CircleMarker(
            [stop.latitude, stop.longitude],
            radius=6,
            color='white',
            fillColor=c['color'],
            fillOpacity=0.9,
            weight=2,
            popup=f"<b>{stop.name}</b>",
            tooltip=stop.name
        ).add_to(stops_group)
    
    routes_group.add_to(m)
    stops_group.add_to(m)
    vehicles_group.add_to(m)
    
    folium.LayerControl().add_to(m)
    plugins.Fullscreen().add_to(m)
    
    return m, map_key


def main():
    # Language state
    if 'lang' not in st.session_state:
        st.session_state.lang = 'en'
    
    lang = st.session_state.lang
    
    # Header
    col_header, col_lang = st.columns([4, 1])
    
    with col_header:
        st.markdown(f"""
        <div class="header-container">
            <div>
                <h1 class="header-title">{t('title', lang)}</h1>
                <div class="header-subtitle">{t('subtitle', lang)}</div>
            </div>
            <div class="live-indicator">
                <div class="live-dot"></div>
                <div class="live-text">{t('live_badge', lang)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_lang:
        col_en, col_pt = st.columns(2)
        with col_en:
            if st.button("🇺🇸 EN", key="lang_en"):
                st.session_state.lang = 'en'
                st.rerun()
        with col_pt:
            if st.button("🇵🇹 PT", key="lang_pt"):
                st.session_state.lang = 'pt'
                st.rerun()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"## ⚙️ {t('select_city', lang)}")
        
        cities = {
            "🇵🇹 Porto": (41.1579, -8.6291),
            "🇵🇹 Lisboa": (38.7223, -9.1393),
            "🇧🇷 São Paulo": (-23.5505, -46.6333),
            "🇧🇷 Rio de Janeiro": (-22.9068, -43.1729),
            "🇺🇸 New York": (40.7128, -74.0060),
            "🇬🇧 London": (51.5074, -0.1278),
            "🇯🇵 Tokyo": (35.6762, 139.6503),
        }
        
        city = st.selectbox("City", list(cities.keys()), label_visibility="collapsed")
        lat, lon = cities[city]
        
        radius = st.slider("Radius (m)", 500, 5000, 2000, 250)
        
        st.markdown("---")
        fetch = st.button(f"🔄 {t('update_data', lang)}", type="primary")
        
        if st.session_state.get('last_update'):
            st.caption(f"{t('last_update', lang)}: {st.session_state.last_update.strftime('%H:%M:%S')}")
    
    # Session state
    if 'stops' not in st.session_state:
        st.session_state.stops = []
        st.session_state.selected_routes = []
        st.session_state.map_filter_route = t('all_routes', lang)
    
    # Fetch with loading animation
    if fetch:
        loading_placeholder = st.empty()
        loading_placeholder.markdown(f"""
        <div class="loading-container">
            <div class="loading-icons">
                <div class="loading-icon">🚌</div>
                <div class="loading-icon">✈️</div>
                <div class="loading-icon">⛴️</div>
            </div>
            <div class="loading-text">{t('loading', lang)}...</div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            pipeline = UrbanMobilityPipeline({})
            stops = pipeline.fetch_transport_stops(lat, lon, radius)
            
            if stops:
                st.session_state.stops = stops
                st.session_state.last_update = datetime.now()
                loading_placeholder.empty()
                st.success(f"✅ {len(stops)} {t('stops', lang)}")
            else:
                loading_placeholder.empty()
                st.warning("⚠️ No stops found")
        except Exception as e:
            loading_placeholder.empty()
            st.error(f"❌ {e}")
    
    stops = st.session_state.stops
    
    if stops:
        # Metrics
        st.markdown(f"### {t('metrics', lang)}")
        
        total = len(stops)
        wheelchair = sum(1 for s in stops if s.wheelchair_accessible)
        shelter = sum(1 for s in stops if s.has_shelter)
        with_routes = sum(1 for s in stops if s.routes)
        
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = [
            (col1, total, t('total_stops', lang), f"{radius}m"),
            (col2, f"{(wheelchair/total*100):.1f}%", t('accessible', lang), f"{wheelchair} {t('stops', lang)}"),
            (col3, f"{(shelter/total*100):.1f}%", t('with_shelter', lang), f"{shelter} {t('stops', lang)}"),
            (col4, with_routes, t('with_routes', lang), f"{(with_routes/total*100):.1f}%")
        ]
        
        for col, value, label, change in metrics:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                    <div class="metric-change">{change}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tabs
        tab1, tab2, tab3 = st.tabs([
            f"🗺️ {t('map_view', lang)}",
            f"🛤️ {t('routes_lines', lang)}",
            f"🚍 {t('vehicle_tracker', lang)}"
        ])
        
        with tab1:
            st.markdown(f"### {t('map_view', lang)}")
            
            # Map filter
            routes_dict = defaultdict(list)
            for stop in stops:
                if stop.routes:
                    for route in stop.routes:
                        routes_dict[route].append(stop)
            
            all_route_names = [extract_route_name(r) for r in routes_dict.keys()]
            all_routes_label = t('show_all', lang)
            
            map_filter = st.selectbox(
                t('filter_route_map', lang),
                options=[all_routes_label] + sorted(all_route_names)
            )
            
            # Determine routes to show
            if map_filter == all_routes_label:
                map_selected_routes = list(routes_dict.keys())[:10]
            else:
                # Find original route key
                map_selected_routes = [k for k in routes_dict.keys() 
                                      if extract_route_name(k) == map_filter]
            
            # Create map with key for persistence
            persistent_map, map_key = create_persistent_map(
                stops, lat, lon,
                selected_routes=map_selected_routes,
                show_vehicles=True,
                lang=lang
            )
            
            # Use key to prevent re-rendering
            st_folium(persistent_map, width=1400, height=700, key=f"map_{map_key}")
        
        with tab2:
            st.markdown(f"### {t('routes_lines', lang)}")
            
            routes_dict = defaultdict(lambda: {'stops': [], 'operators': set()})
            for stop in stops:
                if stop.routes:
                    for route in stop.routes:
                        routes_dict[route]['stops'].append(stop)
                        if stop.operator and stop.operator != 'N/A':
                            routes_dict[route]['operators'].add(stop.operator)
            
            search = st.text_input(t('search_route', lang))
            
            if search:
                routes_dict = {k: v for k, v in routes_dict.items() 
                             if search.lower() in extract_route_name(k).lower()}
            
            sorted_routes = sorted(routes_dict.items(), key=lambda x: len(x[1]['stops']), reverse=True)
            
            st.markdown(f"**{len(routes_dict)} {t('routes_lines', lang).lower()}**")
            
            for route_name, route_data in sorted_routes[:15]:
                num_vehicles = random.randint(2, 4)
                
                with st.expander(f"🚌 {extract_route_name(route_name)} · {len(route_data['stops'])} {t('stops', lang)}"):
                    if route_data['operators']:
                        st.markdown(f"**{t('operator', lang)}:** {', '.join(route_data['operators'])}")
                    st.markdown(f"**{t('active_vehicles', lang)}:** {num_vehicles}")
                    
                    for idx, stop in enumerate(route_data['stops'][:10], 1):
                        st.markdown(f"{idx}. {stop.name}")
        
        with tab3:
            st.markdown(f"### {t('vehicle_tracker', lang)}")
            
            vehicles = st.session_state.get('vehicles', [])
            
            if vehicles:
                unique_routes = list(set(v['route_display'] for v in vehicles))
                route_filter = st.selectbox(
                    "Filter",
                    options=[t('all_routes', lang)] + unique_routes,
                    label_visibility="collapsed"
                )
                
                filtered = vehicles if route_filter == t('all_routes', lang) else [
                    v for v in vehicles if v['route_display'] == route_filter
                ]
                
                st.markdown(f"**{len(filtered)} {t('active_vehicles', lang).lower()}**")
                st.markdown("<br>", unsafe_allow_html=True)
                
                for v in filtered:
                    status_class = "status-active" if v['status'] == "At Stop" else "status-transit"
                    
                    st.markdown(f"""
                    <div class="vehicle-card">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
                            <div style="font-weight: 700; font-size: 1.1rem; color: #2c3e50;">
                                🚌 {v['id']}
                            </div>
                            <div class="status-badge {status_class}">
                                {v['status']}
                            </div>
                        </div>
                        <div class="route-number" style="margin-bottom: 1rem;">
                            {v['route_display']}
                        </div>
                        <div class="stop-grid">
                            <div class="stop-item">
                                <div class="stop-label">{t('last_stop', lang)}</div>
                                <div class="stop-name">{v['last_stop'][:20]}</div>
                            </div>
                            <div class="stop-item">
                                <div class="stop-label">{t('current_stop', lang)}</div>
                                <div class="stop-name">{v['current_stop'][:20]}</div>
                            </div>
                            <div class="stop-item">
                                <div class="stop-label">{t('next_stop', lang)}</div>
                                <div class="stop-name">{v['next_stop'][:20]}</div>
                            </div>
                        </div>
                        <div style="text-align: center; margin-top: 1rem; color: #10b981; font-weight: 600;">
                            {t('eta', lang)}: {v['eta']} {t('minutes', lang)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No vehicles available")


if __name__ == "__main__":
    main()
