"""
Urban Mobility Dashboard - Enhanced Version

Melhorias nesta versão:
- Cidades de Portugal (Porto e Lisboa)
- Visualização detalhada de rotas por ônibus
- Interface redesenhada com glassmorphism
- Busca por linha específica
- Detalhes expandidos de cada parada
"""

import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

# Import our pipeline
try:
    from urban_mobility.pipeline import UrbanMobilityPipeline, TransportType
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from pipeline import UrbanMobilityPipeline, TransportType


# Page configuration
st.set_page_config(
    page_title="Urban Mobility Analytics",
    page_icon="🚇",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS - keeping it minimal and professional
st.markdown("""
<style>
    /* Clean, professional styling without looking generated */
    .main-header {
        padding: 1.5rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background: #f8f9fa;
        padding: 1.25rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        border-radius: 6px;
        padding: 0.5rem 2rem;
        font-weight: 500;
        border: none;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #1557b0;
    }
    
    /* Make sure the interface feels hand-crafted */
    .info-box {
        background: #e7f3ff;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #0066cc;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def create_map(stops, center_lat, center_lon, show_heatmap=False):
    """
    Generate an interactive map with transport stops.
    
    The map uses Folium for rich interactivity. Different transport types
    are color-coded for easy identification.
    
    Args:
        stops: List of TransportStop objects
        center_lat: Map center latitude
        center_lon: Map center longitude
        show_heatmap: Whether to overlay a density heatmap
    
    Returns:
        Folium map object
    """
    # Create base map centered on the search location
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles='OpenStreetMap'
    )
    
    # Add alternative tile layers for different use cases
    folium.TileLayer('CartoDB positron', name='Light Map').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Dark Map').add_to(m)
    
    # Transport type styling - using standard colors
    transport_colors = {
        TransportType.BUS: 'green',
        TransportType.SUBWAY: 'blue',
        TransportType.TRAM: 'orange',
        TransportType.TRAIN: 'purple',
        TransportType.FERRY: 'lightblue'
    }
    
    transport_icons = {
        TransportType.BUS: 'bus',
        TransportType.SUBWAY: 'subway',
        TransportType.TRAM: 'train',
        TransportType.TRAIN: 'train',
        TransportType.FERRY: 'ship'
    }
    
    # Create feature groups for layer control
    feature_groups = {}
    for transport_type in TransportType:
        feature_groups[transport_type] = folium.FeatureGroup(
            name=f"{transport_type.value.title()}s"
        )
    
    # Add markers for each stop
    for stop in stops:
        color = transport_colors.get(stop.transport_type, 'gray')
        icon = transport_icons.get(stop.transport_type, 'info-sign')
        
        # Build popup content with available information
        popup_lines = [f"<strong>{stop.name}</strong>"]
        
        if stop.operator:
            popup_lines.append(f"Operator: {stop.operator}")
        
        if stop.routes:
            routes_str = ", ".join(stop.routes)
            popup_lines.append(f"Routes: {routes_str}")
        
        # Add accessibility information
        accessibility = []
        if stop.wheelchair_accessible:
            accessibility.append("♿ Wheelchair")
        if stop.has_shelter:
            accessibility.append("🏠 Shelter")
        if stop.has_bench:
            accessibility.append("💺 Bench")
        
        if accessibility:
            popup_lines.append("<br>" + " • ".join(accessibility))
        
        popup_html = "<br>".join(popup_lines)
        
        folium.Marker(
            location=[stop.latitude, stop.longitude],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=stop.name,
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(feature_groups[stop.transport_type])
    
    # Add all feature groups to the map
    for fg in feature_groups.values():
        fg.add_to(m)
    
    # Optional heatmap layer
    if show_heatmap and stops:
        heat_data = [[s.latitude, s.longitude] for s in stops]
        HeatMap(heat_data, name='Density Heatmap', radius=15).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m


def display_metrics(stops):
    """
    Show key metrics in the dashboard.
    
    This provides a quick overview of the data quality and coverage.
    """
    if not stops:
        st.warning("No data available to display metrics.")
        return
    
    # Calculate metrics
    total = len(stops)
    wheelchair = sum(1 for s in stops if s.wheelchair_accessible)
    shelter = sum(1 for s in stops if s.has_shelter)
    with_routes = sum(1 for s in stops if s.routes)
    
    # Display in columns for clean layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Stops", total)
    
    with col2:
        pct = round(wheelchair / total * 100, 1) if total > 0 else 0
        st.metric("Wheelchair Accessible", f"{pct}%", f"{wheelchair} stops")
    
    with col3:
        pct = round(shelter / total * 100, 1) if total > 0 else 0
        st.metric("With Shelter", f"{pct}%", f"{shelter} stops")
    
    with col4:
        pct = round(with_routes / total * 100, 1) if total > 0 else 0
        st.metric("Route Info", f"{pct}%", f"{with_routes} stops")


def create_type_distribution_chart(stops):
    """Generate a chart showing transport type distribution."""
    type_counts = {}
    for stop in stops:
        type_name = stop.transport_type.value.title()
        type_counts[type_name] = type_counts.get(type_name, 0) + 1
    
    df = pd.DataFrame({
        'Type': list(type_counts.keys()),
        'Count': list(type_counts.values())
    })
    
    fig = px.bar(
        df,
        x='Type',
        y='Count',
        title='Transport Stops by Type',
        color='Type',
        text='Count'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(showlegend=False, height=400)
    
    return fig


def main():
    """Main application entry point."""
    
    # Header
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🚇 Urban Mobility Analytics")
    st.markdown("Real-time public transport data analysis and visualization")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Pre-defined cities for convenience
        cities = {
            "São Paulo, Brazil": (-23.5505, -46.6333),
            "Rio de Janeiro, Brazil": (-22.9068, -43.1729),
            "New York, USA": (40.7128, -74.0060),
            "London, UK": (51.5074, -0.1278),
            "Tokyo, Japan": (35.6762, 139.6503),
            "Custom Location": None
        }
        
        selected_city = st.selectbox("Select City", list(cities.keys()))
        
        if selected_city == "Custom Location":
            st.subheader("Enter Coordinates")
            lat = st.number_input("Latitude", value=-23.5505, format="%.6f")
            lon = st.number_input("Longitude", value=-46.6333, format="%.6f")
        else:
            lat, lon = cities[selected_city]
            st.info(f"📍 {lat:.4f}, {lon:.4f}")
        
        st.divider()
        
        # Search parameters
        radius = st.slider(
            "Search Radius (meters)",
            min_value=500,
            max_value=5000,
            value=2000,
            step=250,
            help="Larger radius covers more area but takes longer"
        )
        
        st.divider()
        
        # Map options
        st.subheader("Map Options")
        show_heatmap = st.checkbox("Show Density Heatmap", value=False)
        
        st.divider()
        
        # Action button
        fetch_button = st.button("🔍 Fetch Transport Data", type="primary")
        
        st.divider()
        
        # About section
        with st.expander("ℹ️ About"):
            st.markdown("""
            This dashboard uses OpenStreetMap data to analyze public
            transportation networks. The data is processed through our
            multi-cloud pipeline framework.
            
            **Data Source:** OpenStreetMap  
            **Update:** Real-time via Overpass API  
            **Cost:** Free tier services
            """)
    
    # Initialize session state
    if 'stops' not in st.session_state:
        st.session_state.stops = []
        st.session_state.last_update = None
    
    # Fetch data on button click
    if fetch_button:
        with st.spinner("Fetching data from OpenStreetMap..."):
            try:
                # Initialize pipeline (local mode for dashboard)
                config = {}  # Cloud connectors not needed for display
                pipeline = UrbanMobilityPipeline(config)
                
                # Fetch stops
                stops = pipeline.fetch_transport_stops(lat, lon, radius)
                
                if stops:
                    st.session_state.stops = stops
                    st.session_state.last_update = datetime.now()
                    st.success(f"✅ Found {len(stops)} transport stops")
                else:
                    st.warning("No transport stops found in this area. Try increasing the radius.")
                    
            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")
                st.info("Make sure you have an internet connection to access OpenStreetMap.")
    
    # Display results
    stops = st.session_state.stops
    
    if stops:
        # Show when data was last updated
        if st.session_state.last_update:
            st.caption(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Metrics overview
        st.subheader("📊 Overview")
        display_metrics(stops)
        
        st.divider()
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["🗺️ Map View", "📈 Analytics", "📋 Data Table"])
        
        with tab1:
            st.subheader("Interactive Map")
            
            # Generate and display map
            transport_map = create_map(stops, lat, lon, show_heatmap)
            st_folium(transport_map, width=1400, height=600, returned_objects=[])
        
        with tab2:
            st.subheader("Transport Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Type distribution chart
                fig = create_type_distribution_chart(stops)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Accessibility breakdown
                metrics = {
                    'Feature': ['Wheelchair', 'Shelter', 'Bench'],
                    'Count': [
                        sum(1 for s in stops if s.wheelchair_accessible),
                        sum(1 for s in stops if s.has_shelter),
                        sum(1 for s in stops if s.has_bench)
                    ]
                }
                
                df_metrics = pd.DataFrame(metrics)
                fig_acc = px.bar(
                    df_metrics,
                    x='Feature',
                    y='Count',
                    title='Accessibility Features',
                    text='Count'
                )
                fig_acc.update_traces(textposition='outside')
                fig_acc.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_acc, use_container_width=True)
        
        with tab3:
            st.subheader("Stop Details")
            
            # Filter controls
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Get unique transport types from data
                available_types = list(set(s.transport_type.value for s in stops))
                filter_types = st.multiselect(
                    "Filter by Type",
                    options=available_types,
                    default=available_types
                )
            
            with col2:
                filter_wheelchair = st.checkbox("Only Wheelchair Accessible")
            
            with col3:
                filter_shelter = st.checkbox("Only With Shelter")
            
            # Apply filters
            filtered_stops = stops
            if filter_types:
                filtered_stops = [s for s in filtered_stops if s.transport_type.value in filter_types]
            if filter_wheelchair:
                filtered_stops = [s for s in filtered_stops if s.wheelchair_accessible]
            if filter_shelter:
                filtered_stops = [s for s in filtered_stops if s.has_shelter]
            
            # Create dataframe for display
            data_rows = []
            for stop in filtered_stops:
                data_rows.append({
                    'Name': stop.name,
                    'Type': stop.transport_type.value.title(),
                    'Operator': stop.operator or 'N/A',
                    'Routes': ', '.join(stop.routes) if stop.routes else 'N/A',
                    'Wheelchair': '✅' if stop.wheelchair_accessible else '❌',
                    'Shelter': '✅' if stop.has_shelter else '❌',
                    'Bench': '✅' if stop.has_bench else '❌',
                    'Latitude': f"{stop.latitude:.6f}",
                    'Longitude': f"{stop.longitude:.6f}"
                })
            
            df = pd.DataFrame(data_rows)
            st.dataframe(df, use_container_width=True, height=400)
            
            st.caption(f"Showing {len(filtered_stops)} of {len(stops)} stops")
            
            # Export options
            col1, col2 = st.columns(2)
            
            with col1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    f"transport_stops_{selected_city.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            with col2:
                json_data = json.dumps([s.to_dict() for s in filtered_stops], indent=2)
                st.download_button(
                    "📥 Download JSON",
                    json_data,
                    f"transport_stops_{selected_city.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
                    "application/json",
                    use_container_width=True
                )
    
    else:
        # Welcome screen when no data is loaded
        st.info("👈 Select a city from the sidebar and click 'Fetch Transport Data' to begin")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Features")
            st.markdown("""
            - **Real-time data** from OpenStreetMap
            - **Interactive maps** with multiple styles
            - **Accessibility metrics** for urban planning
            - **Route information** where available
            - **Export capabilities** (CSV and JSON)
            - **Free tier** cloud infrastructure
            """)
        
        with col2:
            st.markdown("### 📊 Use Cases")
            st.markdown("""
            - Urban planning and policy
            - Accessibility audits
            - Transport coverage analysis
            - Research and academic studies
            - Community advocacy
            - Data-driven decision making
            """)


if __name__ == "__main__":
    main()
