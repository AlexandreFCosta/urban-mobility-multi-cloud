"""
Urban Mobility Live - V5 UBER-INSPIRED
Complete bilingual interface with route filtering and vehicle tracking

Features:
- Bilingual EN/PT
- Uber-inspired design
- Individual route filtering
- Real-time vehicle tracking with current/last/next stop
- Route names extraction
- Live vehicle panel
"""

import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from collections import defaultdict
import random
import time
import re

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
        'config': 'Configuration',
        'select_city': 'Select City',
        'custom_location': 'Custom Location',
        'search_radius': 'Search Radius (meters)',
        'visualization': 'Visualization Options',
        'show_vehicles': 'Show Vehicles',
        'show_routes': 'Show Routes',
        'update_data': 'Update Data',
        'last_update': 'Last update',
        'metrics': 'Overview',
        'total_stops': 'Total Stops',
        'accessible': 'Accessible',
        'with_shelter': 'With Shelter',
        'with_routes': 'With Routes',
        'radius': 'radius',
        'stops': 'stops',
        'map_view': 'Live Map',
        'routes_lines': 'Routes & Lines',
        'analytics': 'Analytics',
        'search_route': 'Search for line or route',
        'placeholder_search': 'Type line number, name or operator...',
        'lines_found': 'Lines',
        'total_stops_routes': 'Total Stops',
        'avg_per_line': 'Avg/Line',
        'operators': 'Operators',
        'select_routes': 'Select routes to display on map:',
        'routes_selected': 'routes selected',
        'operator': 'Operator',
        'type': 'Type',
        'active_vehicles': 'Active Vehicles',
        'stops_list': 'Stops',
        'more_stops': 'and {n} more stops',
        'welcome': 'Welcome!',
        'welcome_msg': 'Select a city from the sidebar and click <strong>"Update Data"</strong> to start.',
        'features': 'Key Features',
        'feature_routes': 'Traced Routes',
        'feature_routes_desc': 'Complete route visualization with all stops connected',
        'feature_vehicles': 'Live Vehicles',
        'feature_vehicles_desc': 'Track vehicles in real-time on the map',
        'feature_modern': 'Modern Interface',
        'feature_modern_desc': 'Professional design with smooth animations',
        'feature_cities': 'Global Coverage',
        'feature_cities_desc': 'Support for 9 cities worldwide',
        'distribution_type': 'Distribution by Transport Type',
        'accessibility_resources': 'Accessibility Features',
        'data_table': 'Data Table',
        'filter_by_type': 'Filter by Type',
        'only_accessible': 'Only Accessible',
        'only_with_routes': 'Only with Routes',
        'showing': 'Showing {filtered} of {total} stops',
        'vehicle_tracker': 'Live Vehicle Tracker',
        'filter_by_route': 'Filter by Route',
        'all_routes': 'All Routes',
        'vehicle': 'Vehicle',
        'route': 'Route',
        'current_stop': 'Current Stop',
        'last_stop': 'Last Stop',
        'next_stop': 'Next Stop',
        'status': 'Status',
        'in_transit': 'In Transit',
        'at_stop': 'At Stop',
        'eta': 'ETA',
        'minutes': 'min',
        'no_vehicles': 'No vehicles available. Enable "Show Vehicles" and select routes.',
    },
    'pt': {
        'title': 'Urban Mobility Live',
        'subtitle': 'Inteligência de Transporte em Tempo Real',
        'live_badge': 'AO VIVO',
        'config': 'Configuração',
        'select_city': 'Selecionar Cidade',
        'custom_location': 'Localização Personalizada',
        'search_radius': 'Raio de Busca (metros)',
        'visualization': 'Opções de Visualização',
        'show_vehicles': 'Mostrar Veículos',
        'show_routes': 'Mostrar Rotas',
        'update_data': 'Atualizar Dados',
        'last_update': 'Última atualização',
        'metrics': 'Visão Geral',
        'total_stops': 'Total de Paradas',
        'accessible': 'Acessível',
        'with_shelter': 'Com Abrigo',
        'with_routes': 'Com Rotas',
        'radius': 'raio',
        'stops': 'paradas',
        'map_view': 'Mapa ao Vivo',
        'routes_lines': 'Rotas e Linhas',
        'analytics': 'Análises',
        'search_route': 'Buscar linha ou rota',
        'placeholder_search': 'Digite número, nome ou operador...',
        'lines_found': 'Linhas',
        'total_stops_routes': 'Total Paradas',
        'avg_per_line': 'Média/Linha',
        'operators': 'Operadores',
        'select_routes': 'Selecione rotas para exibir no mapa:',
        'routes_selected': 'rotas selecionadas',
        'operator': 'Operador',
        'type': 'Tipo',
        'active_vehicles': 'Veículos Ativos',
        'stops_list': 'Paradas',
        'more_stops': 'e mais {n} paradas',
        'welcome': 'Bem-vindo!',
        'welcome_msg': 'Selecione uma cidade no menu lateral e clique em <strong>"Atualizar Dados"</strong> para começar.',
        'features': 'Principais Recursos',
        'feature_routes': 'Rotas Traçadas',
        'feature_routes_desc': 'Visualização completa de rotas com todas as paradas',
        'feature_vehicles': 'Veículos ao Vivo',
        'feature_vehicles_desc': 'Rastreie veículos em tempo real no mapa',
        'feature_modern': 'Interface Moderna',
        'feature_modern_desc': 'Design profissional com animações suaves',
        'feature_cities': 'Cobertura Global',
        'feature_cities_desc': 'Suporte para 9 cidades ao redor do mundo',
        'distribution_type': 'Distribuição por Tipo de Transporte',
        'accessibility_resources': 'Recursos de Acessibilidade',
        'data_table': 'Tabela de Dados',
        'filter_by_type': 'Filtrar por Tipo',
        'only_accessible': 'Apenas Acessível',
        'only_with_routes': 'Apenas com Rotas',
        'showing': 'Mostrando {filtered} de {total} paradas',
        'vehicle_tracker': 'Rastreador de Veículos ao Vivo',
        'filter_by_route': 'Filtrar por Rota',
        'all_routes': 'Todas as Rotas',
        'vehicle': 'Veículo',
        'route': 'Rota',
        'current_stop': 'Parada Atual',
        'last_stop': 'Última Parada',
        'next_stop': 'Próxima Parada',
        'status': 'Status',
        'in_transit': 'Em Trânsito',
        'at_stop': 'Na Parada',
        'eta': 'Previsão',
        'minutes': 'min',
        'no_vehicles': 'Nenhum veículo disponível. Ative "Mostrar Veículos" e selecione rotas.',
    }
}

def t(key, lang='en'):
    """Get translation"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

# Uber-inspired CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Uber+Move:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', 'Uber Move', -apple-system, BlinkMacSystemFont, sans-serif;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Uber Black Background */
    .stApp {
        background: #000000;
    }
    
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Header - Uber Style */
    .uber-header {
        background: #000000;
        border-bottom: 1px solid #333333;
        padding: 1.5rem 2rem;
        margin: -1.5rem -2rem 2rem -2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .uber-logo {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .uber-title {
        color: #FFFFFF;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .uber-subtitle {
        color: #999999;
        font-size: 0.95rem;
        font-weight: 400;
        margin-top: 0.2rem;
    }
    
    .live-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: #000000;
        border: 1px solid #333333;
        padding: 0.5rem 1rem;
        border-radius: 50px;
    }
    
    .live-dot {
        width: 8px;
        height: 8px;
        background: #00E600;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.1); }
    }
    
    .live-text {
        color: #00E600;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Language Switcher */
    .lang-switch {
        display: flex;
        gap: 0.5rem;
        background: #1A1A1A;
        padding: 0.3rem;
        border-radius: 8px;
        border: 1px solid #333333;
    }
    
    .lang-btn {
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        color: #999999;
        font-weight: 500;
        cursor: pointer;
        border: none;
        background: transparent;
        font-size: 0.85rem;
    }
    
    .lang-btn.active {
        background: #000000;
        color: #FFFFFF;
    }
    
    /* Cards - Uber Style */
    .uber-card {
        background: #1A1A1A;
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1.5rem;
        transition: all 0.2s ease;
    }
    
    .uber-card:hover {
        border-color: #555555;
        transform: translateY(-2px);
    }
    
    /* Metrics */
    .metric-uber {
        text-align: center;
    }
    
    .metric-value-uber {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-label-uber {
        color: #999999;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-change-uber {
        color: #00E600;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 0.3rem;
    }
    
    /* Route Card */
    .route-card-uber {
        background: #1A1A1A;
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .route-card-uber:hover {
        border-color: #00E600;
        background: #222222;
    }
    
    .route-header-uber {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.75rem;
    }
    
    .route-number {
        background: #FFFFFF;
        color: #000000;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.1rem;
        min-width: 60px;
        text-align: center;
    }
    
    .route-name-uber {
        color: #FFFFFF;
        font-weight: 600;
        font-size: 1rem;
        flex: 1;
        margin-left: 1rem;
    }
    
    .vehicles-count {
        background: #00E600;
        color: #000000;
        padding: 0.3rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    
    .route-meta-uber {
        display: flex;
        gap: 1.5rem;
        color: #999999;
        font-size: 0.85rem;
        margin-top: 0.75rem;
    }
    
    /* Vehicle Tracker */
    .vehicle-card {
        background: #1A1A1A;
        border: 1px solid #333333;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .vehicle-header {
        display: flex;
        justify-content: between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .vehicle-id-uber {
        color: #FFFFFF;
        font-weight: 700;
        font-size: 1.05rem;
    }
    
    .vehicle-status {
        background: #00E600;
        color: #000000;
        padding: 0.25rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    
    .vehicle-stops {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
        margin-top: 0.75rem;
    }
    
    .stop-info {
        background: #000000;
        padding: 0.5rem;
        border-radius: 8px;
        border: 1px solid #333333;
    }
    
    .stop-label {
        color: #999999;
        font-size: 0.7rem;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    
    .stop-name {
        color: #FFFFFF;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton>button {
        background: #FFFFFF;
        color: #000000;
        border: none;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        border-radius: 8px;
        width: 100%;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background: #00E600;
        transform: translateY(-1px);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #000000;
        border-right: 1px solid #333333;
    }
    
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #FFFFFF;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
    
    [data-testid="stSidebar"] label {
        color: #999999 !important;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        border-bottom: 1px solid #333333;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 0;
        padding: 1rem 1.5rem;
        font-weight: 600;
        color: #999999;
        border: none;
        border-bottom: 2px solid transparent;
        background: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        color: #FFFFFF;
        border-bottom-color: #00E600;
        background: transparent;
    }
    
    /* Input Fields */
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background: #1A1A1A !important;
        border: 1px solid #333333 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #00E600 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #000000;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #333333;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555555;
    }
    
    /* Text Colors */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #FFFFFF;
    }
    
    .stMarkdown {
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)


def extract_route_name(route_str):
    """Extract readable route name from OSM tags"""
    # Common patterns: "201", "Line 3", "Metro Blue", etc.
    if not route_str:
        return "Unknown"
    
    # Clean up
    route_str = str(route_str).strip()
    
    # If it's just a number, format it
    if route_str.isdigit():
        return f"Line {route_str}"
    
    # If it has "ref:", extract the reference
    if "ref:" in route_str.lower():
        parts = route_str.split(":")
        if len(parts) > 1:
            return parts[1].strip()
    
    # If it's already formatted, return as is
    return route_str


def generate_route_polyline(stops, route_name):
    """Generate polyline connecting stops of a specific route"""
    route_stops = [s for s in stops if route_name in (s.routes or [])]
    if len(route_stops) < 2:
        return None
    
    # Sort by geographic proximity (nearest neighbor)
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
    """Simulate vehicle position with current/last/next stop info"""
    if not route_points or len(route_points) < 2:
        return None
    
    # Position vehicles uniformly along route
    progress = (vehicle_id / total_vehicles + (time.time() % 60) / 600) % 1.0
    total_segments = len(route_points) - 1
    current_segment_float = progress * total_segments
    current_segment = int(current_segment_float)
    
    if current_segment >= total_segments:
        current_segment = total_segments - 1
    
    # Determine stops
    last_stop_idx = current_segment
    next_stop_idx = min(current_segment + 1, len(route_stops) - 1)
    
    last_stop = route_stops[last_stop_idx].name if last_stop_idx < len(route_stops) else "Unknown"
    next_stop = route_stops[next_stop_idx].name if next_stop_idx < len(route_stops) else "Terminal"
    
    # Interpolate position
    local_progress = current_segment_float - current_segment
    p1 = route_points[current_segment]
    p2 = route_points[min(current_segment + 1, len(route_points) - 1)]
    
    lat = p1[0] + (p2[0] - p1[0]) * local_progress
    lon = p1[1] + (p2[1] - p1[1]) * local_progress
    
    # Current stop (if close to a stop)
    if local_progress < 0.1:  # Near last stop
        current_stop = last_stop
        status = "At Stop"
        eta = 0
    elif local_progress > 0.9:  # Near next stop
        current_stop = next_stop
        status = "Arriving"
        eta = 1
    else:  # In between
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


def create_uber_map(stops, center_lat, center_lon, selected_routes=None, show_vehicles=False, lang='en'):
    """Create Uber-inspired map"""
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles='CartoDB Dark Matter'  # Uber uses dark maps
    )
    
    # Uber color palette
    uber_green = '#00E600'
    uber_black = '#000000'
    
    config = {
        TransportType.BUS: {'color': uber_green, 'icon': 'bus', 'emoji': '🚌'},
        TransportType.SUBWAY: {'color': '#1E90FF', 'icon': 'subway', 'emoji': '🚇'},
        TransportType.TRAM: {'color': '#FFA500', 'icon': 'train', 'emoji': '🚊'},
        TransportType.TRAIN: {'color': '#9370DB', 'icon': 'train', 'emoji': '🚆'},
        TransportType.FERRY: {'color': '#00CED1', 'icon': 'ship', 'emoji': '⛴️'}
    }
    
    # Feature groups
    routes_group = folium.FeatureGroup(name='🛤️ Routes', show=True)
    stops_group = folium.FeatureGroup(name='🚏 Stops', show=True)
    vehicles_group = folium.FeatureGroup(name='🚍 Live Vehicles', show=show_vehicles)
    
    # Organize routes
    routes_dict = defaultdict(list)
    for stop in stops:
        if stop.routes:
            for route in stop.routes:
                routes_dict[route].append(stop)
    
    # Colors for routes
    route_colors = [uber_green, '#1E90FF', '#FFA500', '#9370DB', '#FF1493', 
                    '#00CED1', '#FFD700', '#FF4500', '#32CD32']
    
    # Draw selected routes
    routes_to_draw = selected_routes if selected_routes else list(routes_dict.keys())[:10]
    
    # Store vehicles for panel
    if 'vehicles' not in st.session_state:
        st.session_state.vehicles = []
    st.session_state.vehicles = []
    
    for idx, route_name in enumerate(routes_to_draw):
        if route_name not in routes_dict:
            continue
            
        route_stops_list = routes_dict[route_name]
        if len(route_stops_list) < 2:
            continue
        
        # Generate polyline
        result = generate_route_polyline(stops, route_name)
        if not result:
            continue
            
        route_points, ordered_stops = result
        color = route_colors[idx % len(route_colors)]
        
        # Draw route line
        folium.PolyLine(
            route_points,
            color=color,
            weight=4,
            opacity=0.9,
            popup=f"<b>{extract_route_name(route_name)}</b><br>{len(route_stops_list)} stops",
            tooltip=extract_route_name(route_name)
        ).add_to(routes_group)
        
        # Start/End markers
        folium.CircleMarker(
            route_points[0],
            radius=8,
            color='white',
            fillColor=color,
            fillOpacity=1,
            weight=2,
            popup=f"<b>Start: {extract_route_name(route_name)}</b>",
        ).add_to(routes_group)
        
        folium.CircleMarker(
            route_points[-1],
            radius=8,
            color='white',
            fillColor='#FF0000',
            fillOpacity=1,
            weight=2,
            popup=f"<b>End: {extract_route_name(route_name)}</b>",
        ).add_to(routes_group)
        
        # Simulate vehicles
        if show_vehicles and len(route_points) > 2:
            num_vehicles = random.randint(2, 4)
            for v_id in range(num_vehicles):
                vehicle_info = simulate_vehicle_position(route_points, ordered_stops, v_id, num_vehicles)
                if vehicle_info:
                    pos = vehicle_info['position']
                    
                    # Store vehicle info for panel
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
                    
                    # Vehicle popup
                    vehicle_html = f"""
                    <div style="font-family: Inter; width: 250px; padding: 1rem; background: #1A1A1A; color: white; border-radius: 8px;">
                        <div style="font-size: 1.5rem; text-align: center; margin-bottom: 0.5rem;">🚌</div>
                        <div style="background: white; color: black; padding: 0.4rem; border-radius: 6px; 
                                    text-align: center; font-weight: 700; margin-bottom: 0.75rem;">
                            {extract_route_name(route_name)}
                        </div>
                        <div style="font-size: 0.85rem; line-height: 1.6;">
                            <strong>Vehicle:</strong> #{v_id + 1}<br>
                            <strong>Status:</strong> {vehicle_info['status']}<br>
                            <strong>Current:</strong> {vehicle_info['current_stop']}<br>
                            <strong>Next:</strong> {vehicle_info['next_stop']}<br>
                            <strong>ETA:</strong> {vehicle_info['eta']} min
                        </div>
                    </div>
                    """
                    
                    folium.Marker(
                        pos,
                        icon=folium.DivIcon(html=f'<div style="font-size: 28px;">🚌</div>'),
                        popup=folium.Popup(vehicle_html, max_width=250),
                        tooltip=f"🚌 {extract_route_name(route_name)} - Vehicle #{v_id + 1}"
                    ).add_to(vehicles_group)
    
    # Add stops
    for stop in stops:
        c = config.get(stop.transport_type, config[TransportType.BUS])
        
        folium.CircleMarker(
            [stop.latitude, stop.longitude],
            radius=6,
            color='white',
            fillColor=c['color'],
            fillOpacity=0.8,
            weight=2,
            popup=f"<b>{stop.name}</b>",
            tooltip=stop.name
        ).add_to(stops_group)
    
    # Add to map
    routes_group.add_to(m)
    stops_group.add_to(m)
    vehicles_group.add_to(m)
    
    folium.LayerControl(position='topright').add_to(m)
    plugins.Fullscreen().add_to(m)
    
    return m


def main():
    # Language selection
    if 'lang' not in st.session_state:
        st.session_state.lang = 'en'
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"""
        <div class="uber-header">
            <div class="uber-logo">
                <div>
                    <h1 class="uber-title">{t('title', st.session_state.lang)}</h1>
                    <div class="uber-subtitle">{t('subtitle', st.session_state.lang)}</div>
                </div>
            </div>
            <div class="live-indicator">
                <div class="live-dot"></div>
                <div class="live-text">{t('live_badge', st.session_state.lang)}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Language switcher
        col_en, col_pt = st.columns(2)
        with col_en:
            if st.button("🇺🇸 EN", key="lang_en", use_container_width=True):
                st.session_state.lang = 'en'
                st.rerun()
        with col_pt:
            if st.button("🇵🇹 PT", key="lang_pt", use_container_width=True):
                st.session_state.lang = 'pt'
                st.rerun()
    
    lang = st.session_state.lang
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"## {t('config', lang)}")
        
        cities = {
            "🇵🇹 Porto": (41.1579, -8.6291),
            "🇵🇹 Lisboa": (38.7223, -9.1393),
            "🇧🇷 São Paulo": (-23.5505, -46.6333),
            "🇧🇷 Rio de Janeiro": (-22.9068, -43.1729),
            "🇺🇸 New York": (40.7128, -74.0060),
            "🇬🇧 London": (51.5074, -0.1278),
            "🇯🇵 Tokyo": (35.6762, 139.6503),
            f"🌍 {t('custom_location', lang)}": None
        }
        
        city = st.selectbox(t('select_city', lang), list(cities.keys()))
        
        if t('custom_location', lang) in city:
            col1, col2 = st.columns(2)
            lat = col1.number_input("Lat", value=41.1579, format="%.6f")
            lon = col2.number_input("Lon", value=-8.6291, format="%.6f")
        else:
            lat, lon = cities[city]
        
        st.markdown("---")
        radius = st.slider(t('search_radius', lang), 500, 5000, 2000, 250)
        
        st.markdown("---")
        st.markdown(f"#### {t('visualization', lang)}")
        show_vehicles = st.checkbox(t('show_vehicles', lang), value=True)
        show_routes = st.checkbox(t('show_routes', lang), value=True)
        
        st.markdown("---")
        fetch = st.button(f"🔄 {t('update_data', lang)}", type="primary")
        
        if st.session_state.get('last_update'):
            st.caption(f"{t('last_update', lang)}: {st.session_state.last_update.strftime('%H:%M:%S')}")
    
    # Session state
    if 'stops' not in st.session_state:
        st.session_state.stops = []
        st.session_state.last_update = None
        st.session_state.selected_routes = []
    
    # Fetch
    if fetch:
        with st.spinner("🔄"):
            try:
                pipeline = UrbanMobilityPipeline({})
                stops = pipeline.fetch_transport_stops(lat, lon, radius)
                
                if stops:
                    st.session_state.stops = stops
                    st.session_state.last_update = datetime.now()
                    st.success(f"✅ {len(stops)} {t('stops', lang)}")
                else:
                    st.warning("⚠️")
            except Exception as e:
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
        
        with col1:
            st.markdown(f"""
            <div class="uber-card metric-uber">
                <div class="metric-value-uber">{total}</div>
                <div class="metric-label-uber">{t('total_stops', lang)}</div>
                <div class="metric-change-uber">{radius}m {t('radius', lang)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            pct = (wheelchair/total*100) if total > 0 else 0
            st.markdown(f"""
            <div class="uber-card metric-uber">
                <div class="metric-value-uber">{pct:.1f}%</div>
                <div class="metric-label-uber">{t('accessible', lang)}</div>
                <div class="metric-change-uber">{wheelchair} {t('stops', lang)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            pct = (shelter/total*100) if total > 0 else 0
            st.markdown(f"""
            <div class="uber-card metric-uber">
                <div class="metric-value-uber">{pct:.1f}%</div>
                <div class="metric-label-uber">{t('with_shelter', lang)}</div>
                <div class="metric-change-uber">{shelter} {t('stops', lang)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="uber-card metric-uber">
                <div class="metric-value-uber">{with_routes}</div>
                <div class="metric-label-uber">{t('with_routes', lang)}</div>
                <div class="metric-change-uber">{(with_routes/total*100):.1f}%</div>
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
            
            selected_routes = st.session_state.get('selected_routes', [])
            
            uber_map = create_uber_map(
                stops, lat, lon, 
                selected_routes=selected_routes if selected_routes else None,
                show_vehicles=show_vehicles,
                lang=lang
            )
            
            st_folium(uber_map, width=1400, height=700)
        
        with tab2:
            st.markdown(f"### {t('routes_lines', lang)}")
            
            # Organize routes
            routes_dict = defaultdict(lambda: {
                'stops': [],
                'operators': set(),
                'types': []
            })
            
            for stop in stops:
                if stop.routes:
                    for route in stop.routes:
                        routes_dict[route]['stops'].append(stop)
                        if stop.operator and stop.operator != 'N/A':
                            routes_dict[route]['operators'].add(stop.operator)
                        routes_dict[route]['types'].append(stop.transport_type.value)
            
            if not routes_dict:
                st.info(f"📍 {t('no_vehicles', lang)}")
            else:
                # Search
                search = st.text_input(
                    t('search_route', lang),
                    placeholder=t('placeholder_search', lang)
                )
                
                if search:
                    routes_dict = {k: v for k, v in routes_dict.items() 
                                 if search.lower() in k.lower() or 
                                 any(search.lower() in op.lower() for op in v['operators'])}
                
                sorted_routes = sorted(routes_dict.items(), 
                                      key=lambda x: len(x[1]['stops']), 
                                      reverse=True)
                
                # Stats
                col1, col2, col3, col4 = st.columns(4)
                
                total_stops_routes = sum(len(v['stops']) for v in routes_dict.values())
                avg = total_stops_routes / len(routes_dict) if routes_dict else 0
                operators = set()
                for v in routes_dict.values():
                    operators.update(v['operators'])
                
                with col1:
                    st.markdown(f"""
                    <div class="uber-card metric-uber">
                        <div class="metric-value-uber">{len(routes_dict)}</div>
                        <div class="metric-label-uber">{t('lines_found', lang)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="uber-card metric-uber">
                        <div class="metric-value-uber">{total_stops_routes}</div>
                        <div class="metric-label-uber">{t('total_stops_routes', lang)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="uber-card metric-uber">
                        <div class="metric-value-uber">{avg:.1f}</div>
                        <div class="metric-label-uber">{t('avg_per_line', lang)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div class="uber-card metric-uber">
                        <div class="metric-value-uber">{len(operators)}</div>
                        <div class="metric-label-uber">{t('operators', lang)}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Route selection
                st.markdown(f"**{t('select_routes', lang)}**")
                route_names = [name for name, _ in sorted_routes]
                selected = st.multiselect(
                    "routes",
                    options=route_names,
                    default=route_names[:3] if len(route_names) >= 3 else route_names,
                    label_visibility="collapsed"
                )
                st.session_state.selected_routes = selected
                
                if selected:
                    st.success(f"✅ {len(selected)} {t('routes_selected', lang)}")
                
                # Display routes
                for route_name, route_data in sorted_routes[:20]:
                    types = route_data['types']
                    main_type = max(set(types), key=types.count)
                    emojis = {'bus':'🚌','subway':'🚇','tram':'🚊','train':'🚆','ferry':'⛴️'}
                    emoji = emojis.get(main_type,'🚏')
                    num_vehicles = random.randint(2, 4)
                    
                    with st.expander(f"{emoji} {extract_route_name(route_name)} · {len(route_data['stops'])} {t('stops', lang)}"):
                        if route_data['operators']:
                            ops = ', '.join(sorted(route_data['operators']))
                            st.markdown(f"**{t('operator', lang)}:** {ops}")
                        
                        st.markdown(f"**{t('type', lang)}:** {main_type.title()}")
                        st.markdown(f"**{t('active_vehicles', lang)}:** {num_vehicles}")
                        
                        st.markdown("---")
                        st.markdown(f"**{t('stops_list', lang)} ({len(route_data['stops'])}):**")
                        
                        for idx, stop in enumerate(route_data['stops'][:15], 1):
                            acc = []
                            if stop.wheelchair_accessible: acc.append("♿")
                            if stop.has_shelter: acc.append("🏠")
                            acc_str = ' '.join(acc) if acc else ''
                            st.markdown(f"{idx}. **{stop.name}** {acc_str}")
                        
                        if len(route_data['stops']) > 15:
                            st.markdown(f"*{t('more_stops', lang).format(n=len(route_data['stops'])-15)}*")
        
        with tab3:
            st.markdown(f"### {t('vehicle_tracker', lang)}")
            
            vehicles = st.session_state.get('vehicles', [])
            
            if not vehicles:
                st.info(t('no_vehicles', lang))
            else:
                # Filter by route
                all_routes_option = t('all_routes', lang)
                unique_routes = list(set(v['route_display'] for v in vehicles))
                route_filter = st.selectbox(
                    t('filter_by_route', lang),
                    options=[all_routes_option] + unique_routes
                )
                
                filtered_vehicles = vehicles if route_filter == all_routes_option else [
                    v for v in vehicles if v['route_display'] == route_filter
                ]
                
                st.markdown(f"**{len(filtered_vehicles)} {t('active_vehicles', lang).lower()}**")
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Display vehicles
                for vehicle in filtered_vehicles:
                    status_color = "#00E600" if vehicle['status'] == "At Stop" else "#FFA500"
                    status_text = t('at_stop', lang) if vehicle['status'] == "At Stop" else t('in_transit', lang)
                    
                    st.markdown(f"""
                    <div class="vehicle-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                            <div class="vehicle-id-uber">🚌 {vehicle['id']}</div>
                            <div style="background: {status_color}; color: #000; padding: 0.25rem 0.6rem; 
                                        border-radius: 12px; font-size: 0.75rem; font-weight: 700;">
                                {status_text}
                            </div>
                        </div>
                        <div style="background: #FFFFFF; color: #000; padding: 0.4rem; border-radius: 6px; 
                                    text-align: center; font-weight: 700; margin-bottom: 0.75rem;">
                            {vehicle['route_display']}
                        </div>
                        <div class="vehicle-stops">
                            <div class="stop-info">
                                <div class="stop-label">{t('last_stop', lang)}</div>
                                <div class="stop-name">{vehicle['last_stop'][:25]}</div>
                            </div>
                            <div class="stop-info">
                                <div class="stop-label">{t('current_stop', lang)}</div>
                                <div class="stop-name">{vehicle['current_stop'][:25]}</div>
                            </div>
                            <div class="stop-info">
                                <div class="stop-label">{t('next_stop', lang)}</div>
                                <div class="stop-name">{vehicle['next_stop'][:25]}</div>
                            </div>
                        </div>
                        <div style="text-align: center; margin-top: 0.75rem; color: #00E600; font-weight: 600;">
                            {t('eta', lang)}: {vehicle['eta']} {t('minutes', lang)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    else:
        # Welcome
        st.markdown(f"""
        <div class="uber-card" style="text-align: center; padding: 3rem;">
            <h2 style="color: #FFFFFF; margin-bottom: 1rem;">👋 {t('welcome', lang)}</h2>
            <p style="font-size: 1.1rem; color: #999999; margin-bottom: 2rem;">
                {t('welcome_msg', lang)}
            </p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
