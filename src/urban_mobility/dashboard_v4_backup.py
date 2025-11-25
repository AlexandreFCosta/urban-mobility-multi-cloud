"""
Urban Mobility Dashboard - V4 ULTIMATE
Real-time vehicle tracking with animated routes

Features:
- Rotas traçadas no mapa (polylines)
- Nomes completos das linhas
- Rastreamento de veículos simulado
- Animações suaves e modernas
- UX profissional
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

# CSS Ultimate - UX Profissional
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Header Hero */
    .hero-header {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 3rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.4);
        animation: fadeInDown 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        color: #666;
        font-size: 1.2rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .live-badge {
        display: inline-block;
        background: #10b981;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-top: 1rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .live-badge::before {
        content: '🔴';
        margin-right: 0.5rem;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }
    
    /* Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px) saturate(180%);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.5);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(102,126,234,0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s;
    }
    
    .glass-card:hover::before {
        opacity: 1;
    }
    
    .glass-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.25);
        border-color: rgba(102, 126, 234, 0.4);
    }
    
    /* Metric Cards */
    .metric-modern {
        text-align: center;
        height: 100%;
    }
    
    .metric-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        display: block;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.95rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-change {
        font-size: 0.85rem;
        color: #10b981;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .metric-change.negative {
        color: #ef4444;
    }
    
    /* Route Card */
    .route-card-modern {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border-left: 5px solid;
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .route-card-modern::after {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 0;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(102,126,234,0.1));
        transition: width 0.3s ease;
    }
    
    .route-card-modern:hover::after {
        width: 100%;
    }
    
    .route-card-modern:hover {
        transform: translateX(8px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
    }
    
    .route-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
    }
    
    .route-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .route-name {
        color: #333;
        font-weight: 600;
        font-size: 1.1rem;
        flex: 1;
        margin-left: 1rem;
    }
    
    .route-meta {
        display: flex;
        gap: 1.5rem;
        color: #666;
        font-size: 0.9rem;
        flex-wrap: wrap;
    }
    
    .route-meta-item {
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    
    .vehicles-live {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        animation: pulse 2s infinite;
    }
    
    /* Vehicle Tracker */
    .vehicle-tracker {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .vehicle-item {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .vehicle-item:hover {
        background: rgba(255, 255, 255, 0.25);
        transform: translateX(5px);
    }
    
    .vehicle-id {
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .vehicle-status {
        display: flex;
        gap: 1rem;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        font-size: 1.05rem;
        font-weight: 600;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
        background: linear-gradient(135deg, #5568d3 0%, #6a3f8d 100%);
    }
    
    .stButton>button:active {
        transform: translateY(0);
    }
    
    /* Search Box */
    .search-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin: 1.5rem 0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(102, 126, 234, 0.2);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        padding: 0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(102, 126, 234, 0.05);
        border-radius: 16px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 1rem 2rem;
        font-weight: 600;
        color: #666;
        border: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Loading Animation */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-spinner {
        border: 4px solid rgba(102, 126, 234, 0.2);
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 2rem auto;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(102, 126, 234, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5568d3 0%, #6a3f8d 100%);
    }
    
    /* Tooltips */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        background: rgba(0, 0, 0, 0.9);
        color: white;
        text-align: center;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.85rem;
        white-space: nowrap;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)


def generate_route_polyline(stops, route_name):
    """Gera polyline conectando paradas de uma rota específica"""
    route_stops = [s for s in stops if route_name in (s.routes or [])]
    if len(route_stops) < 2:
        return None
    
    # Ordenar por proximidade geográfica (simplificado)
    sorted_stops = [route_stops[0]]
    remaining = route_stops[1:]
    
    while remaining:
        last = sorted_stops[-1]
        nearest = min(remaining, key=lambda s: 
                     ((s.latitude - last.latitude)**2 + (s.longitude - last.longitude)**2)**0.5)
        sorted_stops.append(nearest)
        remaining.remove(nearest)
    
    return [(s.latitude, s.longitude) for s in sorted_stops]


def simulate_vehicle_position(route_points, vehicle_id, total_vehicles):
    """Simula posição de veículo ao longo da rota"""
    if not route_points or len(route_points) < 2:
        return None
    
    # Posicionar veículos uniformemente ao longo da rota
    progress = (vehicle_id / total_vehicles) % 1.0
    idx = int(progress * (len(route_points) - 1))
    
    if idx >= len(route_points) - 1:
        return route_points[-1]
    
    # Interpolar entre dois pontos
    p1 = route_points[idx]
    p2 = route_points[idx + 1]
    local_progress = (progress * (len(route_points) - 1)) % 1.0
    
    lat = p1[0] + (p2[0] - p1[0]) * local_progress
    lon = p1[1] + (p2[1] - p1[1]) * local_progress
    
    return (lat, lon)


def create_live_map(stops, center_lat, center_lon, selected_routes=None, show_vehicles=False):
    """Cria mapa com rotas traçadas e veículos em tempo real"""
    
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles='CartoDB Voyager',
        control_scale=True
    )
    
    # Tile layers
    folium.TileLayer('CartoDB Positron', name='🌅 Light Mode').add_to(m)
    folium.TileLayer('CartoDB Dark Matter', name='🌙 Dark Mode').add_to(m)
    
    # Configuração
    config = {
        TransportType.BUS: {'color': '#10b981', 'icon': 'bus', 'emoji': '🚌'},
        TransportType.SUBWAY: {'color': '#3b82f6', 'icon': 'subway', 'emoji': '🚇'},
        TransportType.TRAM: {'color': '#f59e0b', 'icon': 'train', 'emoji': '🚊'},
        TransportType.TRAIN: {'color': '#8b5cf6', 'icon': 'train', 'emoji': '🚆'},
        TransportType.FERRY: {'color': '#06b6d4', 'icon': 'ship', 'emoji': '⛴️'}
    }
    
    # Organizar por rota
    routes_dict = defaultdict(list)
    for stop in stops:
        if stop.routes:
            for route in stop.routes:
                routes_dict[route].append(stop)
    
    # Feature groups
    routes_group = folium.FeatureGroup(name='🛤️ Rotas', show=True)
    stops_group = folium.FeatureGroup(name='🚏 Paradas', show=True)
    vehicles_group = folium.FeatureGroup(name='🚍 Veículos Ao Vivo', show=show_vehicles)
    
    # Cores para rotas
    route_colors = ['#667eea', '#764ba2', '#10b981', '#f59e0b', '#ef4444', 
                    '#8b5cf6', '#06b6d4', '#ec4899', '#14b8a6']
    
    # Desenhar rotas selecionadas
    routes_to_draw = selected_routes if selected_routes else list(routes_dict.keys())[:10]
    
    for idx, route_name in enumerate(routes_to_draw):
        if route_name not in routes_dict:
            continue
            
        route_stops = routes_dict[route_name]
        if len(route_stops) < 2:
            continue
        
        # Gerar polyline
        route_points = generate_route_polyline(stops, route_name)
        
        if route_points:
            color = route_colors[idx % len(route_colors)]
            
            # Desenhar rota
            folium.PolyLine(
                route_points,
                color=color,
                weight=6,
                opacity=0.8,
                popup=f"<b>{route_name}</b><br>{len(route_stops)} paradas",
                tooltip=f"Linha {route_name}"
            ).add_to(routes_group)
            
            # Adicionar marcador de início e fim
            folium.Marker(
                route_points[0],
                icon=folium.Icon(color='green', icon='play', prefix='fa'),
                popup=f"<b>Início: {route_name}</b>",
                tooltip="Terminal Inicial"
            ).add_to(routes_group)
            
            folium.Marker(
                route_points[-1],
                icon=folium.Icon(color='red', icon='stop', prefix='fa'),
                popup=f"<b>Fim: {route_name}</b>",
                tooltip="Terminal Final"
            ).add_to(routes_group)
            
            # Simular veículos
            if show_vehicles:
                num_vehicles = random.randint(2, 5)  # 2-5 veículos por rota
                for v_id in range(num_vehicles):
                    pos = simulate_vehicle_position(route_points, v_id, num_vehicles)
                    if pos:
                        # Ícone de veículo em movimento
                        vehicle_html = f"""
                        <div style="text-align: center;">
                            <div style="font-size: 2rem;">🚌</div>
                            <div style="background: {color}; color: white; padding: 0.3rem 0.6rem; 
                                        border-radius: 8px; font-weight: 600; margin-top: 0.3rem;">
                                {route_name}
                            </div>
                            <div style="font-size: 0.85rem; color: #666; margin-top: 0.3rem;">
                                Veículo #{v_id + 1}<br>
                                🚦 Em trânsito<br>
                                ⏱️ {random.randint(2, 15)} min até próxima parada
                            </div>
                        </div>
                        """
                        
                        folium.Marker(
                            pos,
                            icon=folium.DivIcon(html=f'<div style="font-size: 24px;">🚌</div>'),
                            popup=folium.Popup(vehicle_html, max_width=250),
                            tooltip=f"🚌 {route_name} - Veículo #{v_id + 1}"
                        ).add_to(vehicles_group)
    
    # Adicionar paradas
    for stop in stops:
        c = config.get(stop.transport_type, config[TransportType.BUS])
        
        popup_html = f"""
        <div style="font-family: Inter; width: 320px; padding: 1rem;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1rem; margin: -1rem -1rem 1rem -1rem; border-radius: 8px 8px 0 0;">
                <h3 style="color: white; margin: 0; font-size: 1.2rem;">
                    {c['emoji']} {stop.name}
                </h3>
            </div>
            
            <div style="margin: 1rem 0;">
                <strong style="color: #667eea;">🚉 Tipo:</strong><br>
                <span style="background: #f3f4f6; padding: 0.3rem 0.8rem; border-radius: 6px; 
                             display: inline-block; margin-top: 0.3rem;">
                    {stop.transport_type.value.title()}
                </span>
            </div>
        """
        
        if stop.operator and stop.operator != 'N/A':
            popup_html += f"""
            <div style="margin: 0.8rem 0;">
                <strong style="color: #667eea;">🏢 Operador:</strong> {stop.operator}
            </div>
            """
        
        if stop.routes:
            popup_html += """
            <div style="margin: 1rem 0;">
                <strong style="color: #667eea;">🛤️ Linhas que param aqui:</strong><br>
                <div style="margin-top: 0.5rem; display: flex; flex-wrap: wrap; gap: 0.3rem;">
            """
            for route in stop.routes[:8]:
                popup_html += f"""
                <span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; padding: 0.4rem 0.8rem; border-radius: 8px; 
                      font-size: 0.85rem; font-weight: 600; display: inline-block;">
                    {route}
                </span>
                """
            popup_html += "</div></div>"
        
        if stop.wheelchair_accessible or stop.has_shelter or stop.has_bench:
            popup_html += """
            <div style="margin: 1rem 0; padding: 0.8rem; background: #f0fdf4; border-radius: 8px;">
                <strong style="color: #10b981;">♿ Recursos:</strong><br>
                <div style="margin-top: 0.5rem; font-size: 0.9rem;">
            """
            if stop.wheelchair_accessible:
                popup_html += "✅ Acessível para cadeirantes<br>"
            if stop.has_shelter:
                popup_html += "✅ Abrigo coberto<br>"
            if stop.has_bench:
                popup_html += "✅ Bancos disponíveis<br>"
            popup_html += "</div></div>"
        
        popup_html += f"""
            <div style="margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid #e5e7eb; 
                        font-size: 0.85rem; color: #999;">
                📍 {stop.latitude:.6f}, {stop.longitude:.6f}
            </div>
        </div>
        """
        
        folium.CircleMarker(
            [stop.latitude, stop.longitude],
            radius=8,
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=f"{c['emoji']} {stop.name}",
            color=c['color'],
            fillColor=c['color'],
            fillOpacity=0.7,
            weight=2
        ).add_to(stops_group)
    
    # Adicionar ao mapa
    routes_group.add_to(m)
    stops_group.add_to(m)
    vehicles_group.add_to(m)
    
    # Controles
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    plugins.Fullscreen().add_to(m)
    plugins.MiniMap(toggle_display=True).add_to(m)
    
    return m


def show_route_details_ultimate(stops):
    """Interface moderna para detalhes de rotas com nomes completos"""
    
    st.markdown("### 🛤️ Explorar Rotas e Linhas")
    
    # Organizar rotas
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
        st.info("📍 Nenhuma informação de rota disponível")
        return []
    
    # Search com design moderno
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search = st.text_input(
            "🔍 Buscar linha ou rota",
            placeholder="Digite o número, nome ou operador...",
            label_visibility="collapsed"
        )
    
    with col2:
        show_all = st.checkbox("Mostrar Todas", value=False)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filtrar
    if search:
        filtered = {k: v for k, v in routes_dict.items() 
                   if search.lower() in k.lower() or 
                   any(search.lower() in op.lower() for op in v['operators'])}
    else:
        filtered = routes_dict
    
    # Ordenar por popularidade
    sorted_routes = sorted(filtered.items(), 
                          key=lambda x: len(x[1]['stops']), 
                          reverse=True)
    
    if not show_all:
        sorted_routes = sorted_routes[:12]
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="glass-card metric-modern">
            <span class="metric-icon">🛤️</span>
            <div class="metric-value">{len(filtered)}</div>
            <div class="metric-label">Linhas</div>
            <div class="metric-change">+{len(filtered)-len(sorted_routes)} ocultas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_stops = sum(len(v['stops']) for v in filtered.values())
        st.markdown(f"""
        <div class="glass-card metric-modern">
            <span class="metric-icon">🚏</span>
            <div class="metric-value">{total_stops}</div>
            <div class="metric-label">Paradas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg = total_stops / len(filtered) if filtered else 0
        st.markdown(f"""
        <div class="glass-card metric-modern">
            <span class="metric-icon">📊</span>
            <div class="metric-value">{avg:.1f}</div>
            <div class="metric-label">Média/Linha</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        operators = set()
        for v in filtered.values():
            operators.update(v['operators'])
        st.markdown(f"""
        <div class="glass-card metric-modern">
            <span class="metric-icon">🏢</span>
            <div class="metric-value">{len(operators)}</div>
            <div class="metric-label">Operadores</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Seleção de rotas para visualizar
    st.markdown("**🎯 Selecione rotas para visualizar no mapa:**")
    
    route_names = [name for name, _ in sorted_routes]
    selected_for_map = st.multiselect(
        "Rotas selecionadas",
        options=route_names,
        default=route_names[:3] if len(route_names) >= 3 else route_names,
        label_visibility="collapsed"
    )
    
    # Mostrar rotas
    for i in range(0, len(sorted_routes), 2):
        cols = st.columns(2)
        
        for j, col in enumerate(cols):
            if i + j >= len(sorted_routes):
                break
                
            route_name, route_data = sorted_routes[i + j]
            
            with col:
                # Tipo predominante
                types = route_data['types']
                main_type = max(set(types), key=types.count)
                emojis = {'bus': '🚌', 'subway': '🚇', 'tram': '🚊', 
                         'train': '🚆', 'ferry': '⛴️'}
                emoji = emojis.get(main_type, '🚏')
                
                # Card
                with st.expander(f"{emoji} **{route_name}** · {len(route_data['stops'])} paradas", 
                               expanded=False):
                    
                    # Operadores
                    if route_data['operators']:
                        ops = ', '.join(sorted(route_data['operators']))
                        st.markdown(f"**🏢 Operador:** {ops}")
                    
                    # Tipo
                    st.markdown(f"**🚉 Tipo:** {main_type.title()}")
                    
                    # Número de veículos simulados
                    num_vehicles = random.randint(2, 5)
                    st.markdown(f"**🚍 Veículos Ativos:** {num_vehicles}")
                    
                    st.markdown("---")
                    st.markdown(f"**📍 Paradas ({len(route_data['stops'])}):**")
                    
                    # Listar paradas
                    for idx, stop in enumerate(route_data['stops'][:15], 1):
                        acc = []
                        if stop.wheelchair_accessible: acc.append("♿")
                        if stop.has_shelter: acc.append("🏠")
                        acc_str = ' '.join(acc) if acc else ''
                        
                        st.markdown(f"{idx}. **{stop.name}** {acc_str}")
                    
                    if len(route_data['stops']) > 15:
                        st.markdown(f"*... e mais {len(route_data['stops']) - 15} paradas*")
    
    return selected_for_map


def main():
    # Hero Header
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">🚇 Urban Mobility Live</h1>
        <p class="hero-subtitle">Rastreamento em Tempo Real de Transporte Público</p>
        <span class="live-badge">AO VIVO</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 Central de Controle")
        
        cities = {
            "🇵🇹 Porto": (41.1579, -8.6291),
            "🇵🇹 Lisboa": (38.7223, -9.1393),
            "🇧🇷 São Paulo": (-23.5505, -46.6333),
            "🇧🇷 Rio de Janeiro": (-22.9068, -43.1729),
            "🇺🇸 Nova York": (40.7128, -74.0060),
            "🇬🇧 Londres": (51.5074, -0.1278),
            "🇯🇵 Tóquio": (35.6762, 139.6503),
            "🌍 Personalizada": None
        }
        
        city = st.selectbox("📍 Selecionar Cidade", list(cities.keys()))
        
        if city == "🌍 Personalizada":
            col1, col2 = st.columns(2)
            lat = col1.number_input("Latitude", value=41.1579, format="%.6f")
            lon = col2.number_input("Longitude", value=-8.6291, format="%.6f")
        else:
            lat, lon = cities[city]
        
        st.markdown("---")
        radius = st.slider("🔍 Raio de Busca (metros)", 500, 5000, 2000, 250)
        
        st.markdown("---")
        st.markdown("#### 🎨 Opções de Visualização")
        show_vehicles = st.checkbox("🚍 Mostrar Veículos", value=True)
        
        st.markdown("---")
        fetch = st.button("🔄 Atualizar Dados", type="primary")
        
        if st.session_state.get('last_update'):
            st.caption(f"⏰ Última atualização: {st.session_state.last_update.strftime('%H:%M:%S')}")
    
    # Session state
    if 'stops' not in st.session_state:
        st.session_state.stops = []
        st.session_state.last_update = None
        st.session_state.selected_routes = []
    
    # Fetch data
    if fetch:
        with st.spinner("🔄 Carregando dados..."):
            try:
                pipeline = UrbanMobilityPipeline({})
                stops = pipeline.fetch_transport_stops(lat, lon, radius)
                
                if stops:
                    st.session_state.stops = stops
                    st.session_state.last_update = datetime.now()
                    st.success(f"✅ {len(stops)} paradas encontradas!")
                else:
                    st.warning("⚠️ Nenhuma parada encontrada")
            except Exception as e:
                st.error(f"❌ Erro: {e}")
    
    stops = st.session_state.stops
    
    if stops:
        # Métricas
        st.markdown("### 📊 Painel de Métricas")
        
        total = len(stops)
        wheelchair = sum(1 for s in stops if s.wheelchair_accessible)
        shelter = sum(1 for s in stops if s.has_shelter)
        with_routes = sum(1 for s in stops if s.routes)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="glass-card metric-modern">
                <span class="metric-icon">🚏</span>
                <div class="metric-value">{total}</div>
                <div class="metric-label">Total de Paradas</div>
                <div class="metric-change">Raio de {radius}m</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            pct = (wheelchair/total*100) if total > 0 else 0
            st.markdown(f"""
            <div class="glass-card metric-modern">
                <span class="metric-icon">♿</span>
                <div class="metric-value">{pct:.1f}%</div>
                <div class="metric-label">Acessível</div>
                <div class="metric-change">{wheelchair} paradas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            pct = (shelter/total*100) if total > 0 else 0
            st.markdown(f"""
            <div class="glass-card metric-modern">
                <span class="metric-icon">🏠</span>
                <div class="metric-value">{pct:.1f}%</div>
                <div class="metric-label">Com Abrigo</div>
                <div class="metric-change">{shelter} paradas</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="glass-card metric-modern">
                <span class="metric-icon">🛤️</span>
                <div class="metric-value">{with_routes}</div>
                <div class="metric-label">Com Rotas</div>
                <div class="metric-change">{(with_routes/total*100):.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Tabs
        tab1, tab2, tab3 = st.tabs([
            "🗺️ Mapa ao Vivo", 
            "🛤️ Rotas e Linhas",
            "📊 Analytics"
        ])
        
        with tab1:
            st.markdown("### 🗺️ Visualização em Tempo Real")
            
            selected_routes = st.session_state.get('selected_routes', [])
            
            live_map = create_live_map(
                stops, lat, lon, 
                selected_routes=selected_routes if selected_routes else None,
                show_vehicles=show_vehicles
            )
            
            st_folium(live_map, width=1400, height=700, returned_objects=[])
            
            st.info("💡 **Dica:** Ative a camada '🚍 Veículos Ao Vivo' no controle do mapa para ver veículos simulados em movimento!")
        
        with tab2:
            selected = show_route_details_ultimate(stops)
            st.session_state.selected_routes = selected
            
            if selected:
                st.success(f"✅ {len(selected)} rotas selecionadas para visualização no mapa!")
        
        with tab3:
            st.markdown("### 📊 Análise de Dados")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Distribuição por tipo
                type_counts = {}
                emojis = {'bus':'🚌','subway':'🚇','tram':'🚊','train':'🚆','ferry':'⛴️'}
                for stop in stops:
                    t = stop.transport_type.value
                    type_counts[t] = type_counts.get(t, 0) + 1
                
                df = pd.DataFrame({
                    'Tipo': [f"{emojis.get(t,'🚏')} {t.title()}" for t in type_counts.keys()],
                    'Quantidade': list(type_counts.values())
                })
                
                fig = px.pie(df, values='Quantidade', names='Tipo', 
                           title='Distribuição por Tipo de Transporte',
                           color_discrete_sequence=px.colors.qualitative.Set3,
                           hole=0.4)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Acessibilidade
                acc_data = pd.DataFrame({
                    'Recurso': ['♿ Wheelchair', '🏠 Shelter', '💺 Bench'],
                    'Quantidade': [
                        wheelchair,
                        shelter,
                        sum(1 for s in stops if s.has_bench)
                    ]
                })
                
                fig = px.bar(acc_data, x='Recurso', y='Quantidade',
                           title='Recursos de Acessibilidade',
                           color='Recurso',
                           color_discrete_sequence=['#667eea', '#764ba2', '#10b981'])
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        # Welcome screen
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <h2 style="color: #667eea; margin-bottom: 1rem;">👋 Bem-vindo ao Sistema Live</h2>
            <p style="font-size: 1.1rem; color: #666; margin-bottom: 2rem;">
                Selecione uma cidade no painel lateral e clique em <strong>"🔄 Atualizar Dados"</strong>
            </p>
            
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 2rem; margin-top: 2rem;">
                <div>
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">🛤️</div>
                    <h3 style="color: #667eea;">Rotas Traçadas</h3>
                    <p style="color: #666;">Visualize rotas completas conectando todas as paradas</p>
                </div>
                <div>
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">🚍</div>
                    <h3 style="color: #667eea;">Veículos ao Vivo</h3>
                    <p style="color: #666;">Acompanhe veículos em tempo real no mapa</p>
                </div>
                <div>
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">🎨</div>
                    <h3 style="color: #667eea;">Interface Moderna</h3>
                    <p style="color: #666;">Design profissional com animações suaves</p>
                </div>
                <div>
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">🇵🇹</div>
                    <h3 style="color: #667eea;">Porto & Lisboa</h3>
                    <p style="color: #666;">Suporte completo para cidades portuguesas</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
