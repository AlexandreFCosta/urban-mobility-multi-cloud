"""
Urban Mobility Dashboard - Enhanced Version

Melhorias:
- Porto e Lisboa adicionadas
- Detalhes de rotas por linha
- Interface redesenhada
- Busca de linhas específicas
"""

import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, MiniMap
from streamlit_folium import st_folium
import plotly.express as px
from datetime import datetime
import json
from collections import defaultdict

try:
    from urban_mobility.pipeline import UrbanMobilityPipeline, TransportType
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from pipeline import UrbanMobilityPipeline, TransportType

st.set_page_config(
    page_title="Urban Mobility Analytics",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS melhorado
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    * { font-family: 'Poppins', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem; border-radius: 15px; text-align: center;
        margin-bottom: 2rem; box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    .main-title {
        color: white; font-size: 2.5rem; font-weight: 700; margin: 0;
    }
    .metric-card {
        background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);
        border-radius: 15px; padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(102,126,234,0.2);
    }
    .metric-value {
        font-size: 2.5rem; font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .route-card {
        background: white; border-radius: 12px; padding: 1rem; margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea; transition: all 0.3s ease;
    }
    .route-card:hover {
        box-shadow: 0 6px 20px rgba(102,126,234,0.15); transform: translateX(5px);
    }
    .transport-badge {
        display: inline-block; padding: 0.4rem 1rem; border-radius: 20px;
        font-weight: 600; font-size: 0.85rem; margin: 0.25rem;
    }
    .badge-bus { background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; }
    .badge-subway { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; }
    .badge-tram { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; }
    .badge-train { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; }
</style>
""", unsafe_allow_html=True)


def create_map(stops, center_lat, center_lon, show_heatmap=False):
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles='CartoDB Voyager')
    folium.TileLayer('CartoDB Positron', name='Light').add_to(m)
    folium.TileLayer('CartoDB Dark Matter', name='Dark').add_to(m)
    
    config = {
        TransportType.BUS: {'color': 'green', 'icon': 'bus', 'emoji': '🚌'},
        TransportType.SUBWAY: {'color': 'blue', 'icon': 'subway', 'emoji': '🚇'},
        TransportType.TRAM: {'color': 'orange', 'icon': 'train', 'emoji': '🚊'},
        TransportType.TRAIN: {'color': 'purple', 'icon': 'train', 'emoji': '🚆'},
        TransportType.FERRY: {'color': 'lightblue', 'icon': 'ship', 'emoji': '⛴️'}
    }
    
    groups = {t: folium.FeatureGroup(name=f"{config[t]['emoji']} {t.value.title()}") 
              for t in TransportType if t in config}
    
    for stop in stops:
        c = config.get(stop.transport_type, config[TransportType.BUS])
        
        popup_html = f"""
        <div style="font-family: Poppins; width: 280px; padding: 10px;">
            <h3 style="color: #667eea; border-bottom: 2px solid #667eea;">
                {c['emoji']} {stop.name}
            </h3>
            <p><strong>Tipo:</strong> {stop.transport_type.value.title()}</p>
        """
        
        if stop.operator and stop.operator != 'N/A':
            popup_html += f"<p><strong>Operador:</strong> {stop.operator}</p>"
        
        if stop.routes:
            popup_html += "<p><strong>Linhas:</strong><br>"
            for route in stop.routes[:6]:
                popup_html += f'<span style="background:#667eea;color:white;padding:3px 8px;border-radius:5px;margin:2px;display:inline-block;">{route}</span> '
            popup_html += "</p>"
        
        if stop.wheelchair_accessible or stop.has_shelter:
            popup_html += "<p><strong>Acessibilidade:</strong><br>"
            if stop.wheelchair_accessible: popup_html += "♿ Wheelchair "
            if stop.has_shelter: popup_html += "🏠 Shelter "
            popup_html += "</p>"
        
        popup_html += f"<p style='font-size:0.85rem;color:#999;'>📍 {stop.latitude:.6f}, {stop.longitude:.6f}</p></div>"
        
        folium.Marker(
            [stop.latitude, stop.longitude],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{c['emoji']} {stop.name}",
            icon=folium.Icon(color=c['color'], icon=c['icon'], prefix='fa')
        ).add_to(groups[stop.transport_type])
    
    for g in groups.values(): g.add_to(m)
    
    if show_heatmap and stops:
        HeatMap([[s.latitude, s.longitude] for s in stops], name='🔥 Density', radius=15).add_to(m)
    
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    MiniMap().add_to(m)
    return m


def show_routes(stops):
    st.markdown("### 🛤️ Rotas Disponíveis")
    
    routes = defaultdict(list)
    for stop in stops:
        if stop.routes:
            for route in stop.routes:
                routes[route].append({
                    'name': stop.name,
                    'type': stop.transport_type.value,
                    'operator': stop.operator
                })
    
    if not routes:
        st.info("📍 Sem informação de rotas nesta área")
        return
    
    search = st.text_input("🔍 Buscar linha", placeholder="Ex: 107, Metro Linha 3...")
    
    if search:
        routes = {k: v for k, v in routes.items() if search.lower() in k.lower()}
    
    sorted_routes = sorted(routes.items(), key=lambda x: len(x[1]), reverse=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(routes)}</div><p>Linhas</p></div>', unsafe_allow_html=True)
    with col2:
        total = sum(len(s) for s in routes.values())
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total}</div><p>Paradas</p></div>', unsafe_allow_html=True)
    with col3:
        avg = total / len(routes) if routes else 0
        st.markdown(f'<div class="metric-card"><div class="metric-value">{avg:.1f}</div><p>Média</p></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    for i in range(0, len(sorted_routes), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i+j < len(sorted_routes):
                route_name, route_stops = sorted_routes[i+j]
                types = [s['type'] for s in route_stops]
                main_type = max(set(types), key=types.count)
                emoji = {'bus':'🚌','subway':'🚇','tram':'🚊','train':'🚆','ferry':'⛴️'}.get(main_type,'🚏')
                
                with col:
                    with st.expander(f"{emoji} **{route_name}** ({len(route_stops)} paradas)"):
                        ops = list(set([s['operator'] for s in route_stops if s['operator'] and s['operator']!='N/A']))
                        if ops: st.markdown(f"**Operador:** {', '.join(ops)}")
                        st.markdown("**Paradas:**")
                        for idx, stop in enumerate(route_stops[:10], 1):
                            st.markdown(f"{idx}. {stop['name']}")
                        if len(route_stops) > 10:
                            st.markdown(f"*... +{len(route_stops)-10} paradas*")


def main():
    st.markdown('<div class="main-header"><h1 class="main-title">🚇 Urban Mobility Analytics</h1><p>Análise Inteligente de Transporte Público</p></div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("## 🎯 Configuração")
        
        cities = {
            "🇵🇹 Porto, Portugal": (41.1579, -8.6291),
            "🇵🇹 Lisboa, Portugal": (38.7223, -9.1393),
            "🇧🇷 São Paulo, Brasil": (-23.5505, -46.6333),
            "🇧🇷 Rio de Janeiro, Brasil": (-22.9068, -43.1729),
            "🇺🇸 Nova York, EUA": (40.7128, -74.0060),
            "🇬🇧 Londres, Inglaterra": (51.5074, -0.1278),
            "🇯🇵 Tóquio, Japão": (35.6762, 139.6503),
            "🌍 Personalizada": None
        }
        
        city = st.selectbox("Cidade", list(cities.keys()))
        
        if city == "🌍 Personalizada":
            col1, col2 = st.columns(2)
            lat = col1.number_input("Lat", value=41.1579, format="%.6f")
            lon = col2.number_input("Lon", value=-8.6291, format="%.6f")
        else:
            lat, lon = cities[city]
            st.info(f"📍 {lat:.4f}, {lon:.4f}")
        
        st.markdown("---")
        radius = st.slider("Raio (m)", 500, 5000, 2000, 250)
        st.markdown("---")
        show_heatmap = st.checkbox("Mapa de Calor")
        st.markdown("---")
        fetch = st.button("🔍 Buscar", type="primary")
    
    if 'stops' not in st.session_state:
        st.session_state.stops = []
        st.session_state.last_update = None
    
    if fetch:
        with st.spinner("Buscando..."):
            try:
                pipeline = UrbanMobilityPipeline({})
                stops = pipeline.fetch_transport_stops(lat, lon, radius)
                
                if stops:
                    st.session_state.stops = stops
                    st.session_state.last_update = datetime.now()
                    st.success(f"✅ {len(stops)} paradas encontradas!")
                else:
                    st.warning("Nenhuma parada encontrada")
            except Exception as e:
                st.error(f"Erro: {e}")
    
    stops = st.session_state.stops
    
    if stops:
        if st.session_state.last_update:
            st.caption(f"⏰ {st.session_state.last_update.strftime('%d/%m/%Y %H:%M')}")
        
        st.markdown("### 📊 Métricas")
        
        total = len(stops)
        wheelchair = sum(1 for s in stops if s.wheelchair_accessible)
        shelter = sum(1 for s in stops if s.has_shelter)
        with_routes = sum(1 for s in stops if s.routes)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f'<div class="metric-card"><div class="metric-value">{total}</div><p>Paradas</p></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="metric-card"><div class="metric-value">{wheelchair/total*100:.1f}%</div><p>Acessível</p></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="metric-card"><div class="metric-value">{shelter/total*100:.1f}%</div><p>Com Abrigo</p></div>', unsafe_allow_html=True)
        col4.markdown(f'<div class="metric-card"><div class="metric-value">{with_routes}</div><p>Com Rotas</p></div>', unsafe_allow_html=True)
        
        type_counts = {}
        emojis = {'bus':'🚌','subway':'🚇','tram':'🚊','train':'🚆','ferry':'⛴️'}
        for stop in stops:
            type_counts[stop.transport_type.value] = type_counts.get(stop.transport_type.value, 0) + 1
        
        badges = ''.join([f'<span class="transport-badge badge-{t}">{emojis.get(t,"🚏")} {t.upper()}: {c}</span>' 
                         for t,c in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)])
        st.markdown(f'<div style="margin:1rem 0;">{badges}</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Mapa", "🛤️ Rotas", "📊 Análise", "📋 Dados"])
        
        with tab1:
            st.markdown("### 🗺️ Mapa Interativo")
            m = create_map(stops, lat, lon, show_heatmap)
            st_folium(m, width=1400, height=650)
        
        with tab2:
            show_routes(stops)
        
        with tab3:
            st.markdown("### 📊 Gráficos")
            col1, col2 = st.columns(2)
            
            with col1:
                df = pd.DataFrame({'Tipo':[f"{emojis.get(t,'🚏')} {t.title()}" for t in type_counts.keys()],
                                  'Qtd':list(type_counts.values())})
                fig = px.pie(df, values='Qtd', names='Tipo', title='Por Tipo')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                acc = pd.DataFrame({'Recurso':['♿ Wheelchair','🏠 Shelter','💺 Bench'],
                                   'Qtd':[wheelchair, shelter, sum(1 for s in stops if s.has_bench)]})
                fig = px.bar(acc, x='Recurso', y='Qtd', title='Acessibilidade')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            st.markdown("### 📋 Tabela")
            
            col1, col2, col3 = st.columns(3)
            ftypes = col1.multiselect("Tipo", list(set(s.transport_type.value for s in stops)), list(set(s.transport_type.value for s in stops)))
            fwheel = col2.checkbox("Acessível")
            froutes = col3.checkbox("Com Rotas")
            
            filtered = [s for s in stops if s.transport_type.value in ftypes 
                       and (not fwheel or s.wheelchair_accessible)
                       and (not froutes or s.routes)]
            
            data = pd.DataFrame([{
                'Nome': s.name,
                'Tipo': f"{emojis.get(s.transport_type.value,'🚏')} {s.transport_type.value.title()}",
                'Operador': s.operator or 'N/A',
                'Linhas': ', '.join(s.routes[:3]) if s.routes else 'N/A',
                '♿': '✅' if s.wheelchair_accessible else '❌',
                '🏠': '✅' if s.has_shelter else '❌',
                'Lat': f"{s.latitude:.6f}",
                'Lon': f"{s.longitude:.6f}"
            } for s in filtered])
            
            st.dataframe(data, use_container_width=True, height=400)
            st.caption(f"{len(filtered)} de {len(stops)} paradas")
            
            col1, col2 = st.columns(2)
            col1.download_button("📥 CSV", data.to_csv(index=False).encode('utf-8'), 
                                f"mobility_{datetime.now():%Y%m%d}.csv", use_container_width=True)
            col2.download_button("📥 JSON", json.dumps([s.to_dict() for s in filtered], indent=2), 
                                f"mobility_{datetime.now():%Y%m%d}.json", use_container_width=True)
    else:
        st.info("👈 Selecione uma cidade e clique em **Buscar**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🎯 Recursos")
            st.markdown("- 🗺️ Mapas interativos\n- 🛤️ Detalhes de rotas\n- 📊 Análises visuais\n- ♿ Métricas de acessibilidade\n- 🔍 Busca de linhas\n- 📥 Export CSV/JSON")
        with col2:
            st.markdown("### 🌍 Cidades")
            st.markdown("- 🇵🇹 Porto e Lisboa\n- 🇧🇷 São Paulo e Rio\n- 🇺🇸 Nova York\n- 🇬🇧 Londres\n- 🇯🇵 Tóquio\n- 🌍 Personalizada")

if __name__ == "__main__":
    main()
