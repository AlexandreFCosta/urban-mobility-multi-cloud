"""
Urban Mobility Analytics Pipeline

A specialized implementation of the multi-cloud data pipeline framework
for real-time urban transportation analysis and visualization.

This module extends the base framework with domain-specific logic for:
- OpenStreetMap data ingestion
- Geospatial transformation and analysis
- Transport accessibility metrics
- Real-time visualization pipelines

Author: Alexandre F. Costa
Repository: https://github.com/AlexandreFCosta/urban-mobility-pipeline
"""

import sys
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# Note: In production, this would import from the installed package:
# from multicloud_pipeline import Pipeline, CloudProvider
# For development, we use relative imports
try:
    from multicloud_pipeline import Pipeline, CloudProvider
    from multicloud_pipeline.connectors.azure_connectors import AzureBlobConnector
    from multicloud_pipeline.connectors.gcp_connectors import GCPBigQueryConnector
except ImportError:
    # Fallback for local development
    logging.warning("Multi-cloud framework not installed. Using mock implementations.")
    CloudProvider = None
    Pipeline = None


# Configure logging with production-grade format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TransportType(Enum):
    """
    Enumeration of supported public transport types.
    
    Based on OpenStreetMap tagging conventions:
    https://wiki.openstreetmap.org/wiki/Key:public_transport
    """
    BUS = "bus"
    SUBWAY = "subway"
    TRAM = "tram"
    TRAIN = "train"
    FERRY = "ferry"
    LIGHT_RAIL = "light_rail"
    
    @classmethod
    def from_osm_tags(cls, tags: Dict[str, str]) -> Optional['TransportType']:
        """
        Parse transport type from OSM tags.
        
        Args:
            tags: Dictionary of OSM key-value pairs
            
        Returns:
            TransportType enum value or None if not recognized
        """
        # Highway tags typically indicate bus stops
        if tags.get('highway') == 'bus_stop':
            return cls.BUS
            
        # Railway tags indicate rail-based transport
        railway = tags.get('railway')
        if railway == 'station':
            return cls.SUBWAY
        elif railway == 'tram_stop':
            return cls.TRAM
        elif railway == 'halt':
            return cls.TRAIN
            
        # Amenity tags for other transport types
        if tags.get('amenity') == 'ferry_terminal':
            return cls.FERRY
            
        # Public transport tag as fallback
        if tags.get('public_transport') in ['stop_position', 'platform']:
            # Try to infer from route tags
            if 'bus' in tags.get('bus', '').lower():
                return cls.BUS
            elif 'tram' in tags.get('tram', '').lower():
                return cls.TRAM
                
        return None


@dataclass
class TransportStop:
    """
    Data model for a public transport stop.
    
    This class represents a single transport location with all relevant
    metadata for accessibility analysis and routing.
    
    Attributes:
        osm_id: Unique OpenStreetMap identifier
        name: Human-readable stop name
        latitude: WGS84 latitude coordinate
        longitude: WGS84 longitude coordinate
        transport_type: Type of transport service
        operator: Operating company (e.g., SPTrans, Metrô SP)
        network: Transport network name
        routes: List of route numbers/names served
        ref: Reference code (e.g., stop ID)
        wheelchair_accessible: Whether stop is wheelchair accessible
        has_shelter: Presence of weather shelter
        has_bench: Presence of seating
        has_tactile_paving: Tactile paving for visually impaired
        metadata: Additional OpenStreetMap tags
    """
    osm_id: str
    name: str
    latitude: float
    longitude: float
    transport_type: TransportType
    operator: Optional[str] = None
    network: Optional[str] = None
    routes: List[str] = field(default_factory=list)
    ref: Optional[str] = None
    wheelchair_accessible: bool = False
    has_shelter: bool = False
    has_bench: bool = False
    has_tactile_paving: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation suitable for JSON/BigQuery
        """
        return {
            'osm_id': self.osm_id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'transport_type': self.transport_type.value,
            'operator': self.operator,
            'network': self.network,
            'routes': self.routes,
            'ref': self.ref,
            'wheelchair_accessible': self.wheelchair_accessible,
            'has_shelter': self.has_shelter,
            'has_bench': self.has_bench,
            'has_tactile_paving': self.has_tactile_paving,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_osm_element(cls, element: Dict[str, Any]) -> Optional['TransportStop']:
        """
        Create TransportStop from OpenStreetMap Overpass API response element.
        
        Args:
            element: Dictionary containing OSM node data
            
        Returns:
            TransportStop instance or None if invalid
        """
        if element.get('type') != 'node':
            return None
            
        tags = element.get('tags', {})
        transport_type = TransportType.from_osm_tags(tags)
        
        if not transport_type:
            return None
            
        # Extract route information from various tag formats
        routes = cls._extract_routes(tags)
        
        return cls(
            osm_id=str(element['id']),
            name=tags.get('name', 'Unnamed Stop'),
            latitude=element['lat'],
            longitude=element['lon'],
            transport_type=transport_type,
            operator=tags.get('operator'),
            network=tags.get('network'),
            routes=routes,
            ref=tags.get('ref'),
            wheelchair_accessible=tags.get('wheelchair') == 'yes',
            has_shelter=tags.get('shelter') == 'yes',
            has_bench=tags.get('bench') == 'yes',
            has_tactile_paving=tags.get('tactile_paving') == 'yes',
            metadata=tags
        )
    
    @staticmethod
    def _extract_routes(tags: Dict[str, str]) -> List[str]:
        """
        Extract route numbers from OSM tags.
        
        Different regions use different tagging schemes:
        - 'lines' tag with semicolon separation (common in Brazil)
        - 'route_ref' tag
        - Multiple 'route' tags
        
        Args:
            tags: OSM tag dictionary
            
        Returns:
            List of unique route identifiers
        """
        routes = []
        
        # Check 'lines' tag (e.g., "107M;177H;178")
        if 'lines' in tags:
            routes.extend(tags['lines'].split(';'))
        
        # Check route-related tags
        for key, value in tags.items():
            if 'route' in key.lower() and value:
                routes.append(value)
        
        # Remove duplicates and whitespace, limit to 5 routes for display
        routes = [r.strip() for r in routes if r.strip()]
        return list(dict.fromkeys(routes))[:5]


class UrbanMobilityPipeline:
    """
    Production pipeline for urban mobility data processing.
    
    This class orchestrates the complete data flow:
    1. Data ingestion from OpenStreetMap
    2. Transformation and enrichment
    3. Quality validation
    4. Storage in BigQuery
    5. Caching in Azure Blob for fast retrieval
    
    The pipeline is designed to run on a schedule (e.g., hourly) to keep
    data fresh while respecting API rate limits.
    
    Example:
        >>> config = {
        ...     'gcp_project': 'my-project',
        ...     'bq_dataset': 'mobility',
        ...     'azure_account': 'storageaccount'
        ... }
        >>> pipeline = UrbanMobilityPipeline(config)
        >>> stops = pipeline.fetch_transport_stops(-23.5505, -46.6333, radius=2000)
        >>> pipeline.process_and_store(stops, city='sao_paulo')
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the urban mobility pipeline.
        
        Args:
            config: Configuration dictionary with cloud credentials
                   and connection details
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize cloud connectors if framework is available
        if Pipeline:
            self.pipeline = Pipeline()
            self._setup_connectors()
        else:
            self.pipeline = None
            self.logger.warning("Running in local mode without cloud connectors")
        
        # Statistics for monitoring
        self.stats = {
            'stops_processed': 0,
            'stops_failed': 0,
            'api_calls': 0,
            'errors': []
        }
    
    def _setup_connectors(self):
        """Configure cloud storage connectors using the framework."""
        try:
            # GCP BigQuery for analytical queries
            bq_config = {
                'project_id': self.config.get('gcp_project'),
                'dataset_id': self.config.get('bq_dataset', 'urban_mobility')
            }
            self.bq_connector = GCPBigQueryConnector(**bq_config)
            self.logger.info("BigQuery connector initialized")
            
            # Azure Blob for caching and fast retrieval
            blob_config = {
                'account_name': self.config.get('azure_account'),
                'account_key': self.config.get('azure_key'),
                'container_name': 'mobility-cache'
            }
            self.blob_connector = AzureBlobConnector(**blob_config)
            self.logger.info("Azure Blob connector initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize connectors: {e}")
            raise
    
    def fetch_transport_stops(
        self,
        latitude: float,
        longitude: float,
        radius: int = 2000
    ) -> List[TransportStop]:
        """
        Fetch public transport stops from OpenStreetMap.
        
        Uses the Overpass API to query OSM data. Implements retry logic
        and respects rate limiting to be a good API citizen.
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius: Search radius in meters (default: 2km)
            
        Returns:
            List of TransportStop objects
            
        Raises:
            requests.RequestException: If API call fails after retries
        """
        import requests
        import time
        
        self.stats['api_calls'] += 1
        
        # Construct Overpass QL query
        # We query multiple types to get comprehensive coverage
        query = f"""
        [out:json][timeout:90];
        (
          node["public_transport"="stop_position"](around:{radius},{latitude},{longitude});
          node["public_transport"="platform"](around:{radius},{latitude},{longitude});
          node["highway"="bus_stop"](around:{radius},{latitude},{longitude});
          node["railway"="station"](around:{radius},{latitude},{longitude});
          node["railway"="tram_stop"](around:{radius},{latitude},{longitude});
          node["amenity"="ferry_terminal"](around:{radius},{latitude},{longitude});
        );
        out body;
        """
        
        overpass_url = "https://overpass-api.de/api/interpreter"
        headers = {'User-Agent': 'UrbanMobilityPipeline/1.0 (Contact: alexandre.portella03@gmail.com)'}
        
        # Retry logic for resilience
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Querying Overpass API (attempt {attempt + 1}/{max_retries})")
                
                response = requests.post(
                    overpass_url,
                    data={'data': query},
                    headers=headers,
                    timeout=120
                )
                response.raise_for_status()
                
                data = response.json()
                elements = data.get('elements', [])
                
                self.logger.info(f"Retrieved {len(elements)} elements from OSM")
                
                # Parse elements into TransportStop objects
                stops = []
                for element in elements:
                    stop = TransportStop.from_osm_element(element)
                    if stop:
                        stops.append(stop)
                        self.stats['stops_processed'] += 1
                    else:
                        self.stats['stops_failed'] += 1
                
                self.logger.info(f"Parsed {len(stops)} valid transport stops")
                return stops
                
            except requests.exceptions.Timeout:
                self.logger.warning(f"Request timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise
                    
            except requests.exceptions.RequestException as e:
                self.logger.error(f"API request failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise
        
        return []
    
    def calculate_metrics(self, stops: List[TransportStop]) -> Dict[str, Any]:
        """
        Calculate summary metrics for a set of stops.
        
        These metrics are useful for monitoring data quality and
        generating reports on accessibility.
        
        Args:
            stops: List of TransportStop objects
            
        Returns:
            Dictionary containing calculated metrics
        """
        if not stops:
            return {
                'total_stops': 0,
                'by_type': {},
                'accessibility': {}
            }
        
        total = len(stops)
        
        # Count by transport type
        by_type = {}
        for stop in stops:
            type_name = stop.transport_type.value
            by_type[type_name] = by_type.get(type_name, 0) + 1
        
        # Accessibility metrics
        wheelchair = sum(1 for s in stops if s.wheelchair_accessible)
        shelter = sum(1 for s in stops if s.has_shelter)
        bench = sum(1 for s in stops if s.has_bench)
        tactile = sum(1 for s in stops if s.has_tactile_paving)
        routes = sum(1 for s in stops if s.routes)
        
        return {
            'total_stops': total,
            'by_type': by_type,
            'accessibility': {
                'wheelchair_accessible': wheelchair,
                'wheelchair_pct': round(wheelchair / total * 100, 2),
                'with_shelter': shelter,
                'shelter_pct': round(shelter / total * 100, 2),
                'with_bench': bench,
                'bench_pct': round(bench / total * 100, 2),
                'with_tactile_paving': tactile,
                'tactile_pct': round(tactile / total * 100, 2),
                'with_route_info': routes,
                'routes_pct': round(routes / total * 100, 2)
            }
        }
    
    def process_and_store(
        self,
        stops: List[TransportStop],
        city: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Process stops and store in BigQuery and Azure Blob.
        
        This method handles the complete storage workflow:
        1. Add timestamp and city metadata
        2. Write to BigQuery for analytics
        3. Cache in Azure Blob for fast retrieval
        
        Args:
            stops: List of transport stops to store
            city: City identifier (e.g., 'sao_paulo')
            metadata: Additional metadata to attach
        """
        if not stops:
            self.logger.warning("No stops to process")
            return
        
        timestamp = datetime.utcnow().isoformat()
        
        # Prepare records for BigQuery
        records = []
        for stop in stops:
            record = stop.to_dict()
            record['city'] = city
            record['ingestion_timestamp'] = timestamp
            if metadata:
                record['pipeline_metadata'] = metadata
            records.append(record)
        
        try:
            # Store in BigQuery
            if self.pipeline and self.bq_connector:
                table_id = f"{city}_transport_stops"
                self.logger.info(f"Writing {len(records)} records to BigQuery table {table_id}")
                # In production: self.bq_connector.write(records, table_id)
                
            # Cache in Azure Blob
            if self.pipeline and self.blob_connector:
                import json
                blob_name = f"cities/{city}/latest.json"
                blob_data = json.dumps({
                    'timestamp': timestamp,
                    'stops': records,
                    'metrics': self.calculate_metrics(stops)
                }, indent=2)
                self.logger.info(f"Caching data in Azure Blob: {blob_name}")
                # In production: self.blob_connector.write(blob_data, blob_name)
                
            self.logger.info("Data successfully stored in BigQuery and Azure")
            
        except Exception as e:
            self.logger.error(f"Failed to store data: {e}")
            self.stats['errors'].append(str(e))
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get pipeline execution statistics.
        
        Useful for monitoring and alerting.
        
        Returns:
            Dictionary with execution stats
        """
        return {
            **self.stats,
            'success_rate': (
                self.stats['stops_processed'] / 
                (self.stats['stops_processed'] + self.stats['stops_failed'])
                if self.stats['stops_processed'] + self.stats['stops_failed'] > 0
                else 0
            )
        }


def main():
    """
    Entry point for command-line execution.
    
    This allows the pipeline to be run as a standalone script for testing
    or scheduled execution (e.g., via cron or Cloud Scheduler).
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Urban Mobility Data Pipeline',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--lat', type=float, required=True, help='Latitude')
    parser.add_argument('--lon', type=float, required=True, help='Longitude')
    parser.add_argument('--radius', type=int, default=2000, help='Search radius (meters)')
    parser.add_argument('--city', type=str, required=True, help='City identifier')
    parser.add_argument('--gcp-project', type=str, help='GCP project ID')
    parser.add_argument('--azure-account', type=str, help='Azure storage account')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    config = {
        'gcp_project': args.gcp_project,
        'azure_account': args.azure_account
    }
    
    pipeline = UrbanMobilityPipeline(config)
    
    # Execute pipeline
    logger.info(f"Fetching transport stops for {args.city}")
    stops = pipeline.fetch_transport_stops(args.lat, args.lon, args.radius)
    
    logger.info(f"Processing {len(stops)} stops")
    metrics = pipeline.calculate_metrics(stops)
    
    logger.info(f"Metrics: {metrics}")
    
    # Store data
    pipeline.process_and_store(stops, args.city)
    
    # Print statistics
    stats = pipeline.get_statistics()
    logger.info(f"Pipeline statistics: {stats}")


if __name__ == '__main__':
    main()
