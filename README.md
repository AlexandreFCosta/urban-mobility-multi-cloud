# Urban Mobility Analytics Pipeline

A specialized implementation of the [Multi-Cloud Data Pipeline Framework](https://github.com/AlexandreFCosta/multi-cloud-data-pipeline) for analyzing public transportation networks using OpenStreetMap data.

## Overview

This project extends the base multi-cloud pipeline framework with domain-specific functionality for urban mobility analysis. It fetches real-time public transport data, processes it through AWS Lambda and Azure Functions, stores it in GCP BigQuery, and presents interactive visualizations through a Streamlit dashboard.

The pipeline was designed with two primary goals:
1. **Demonstrate practical multi-cloud architecture** - showing how to effectively combine AWS, GCP, and Azure services
2. **Provide actionable urban mobility insights** - helping cities and researchers understand transport accessibility

## Architecture

The system follows a typical data engineering pattern:

```
Data Source (OpenStreetMap)
    ↓
Collection Layer (AWS Lambda)
    ↓
Processing Layer (Azure Functions)
    ↓
Storage Layer (GCP BigQuery)
    ↓
Presentation Layer (Streamlit)
```

### Why Multi-Cloud?

Each cloud provider was chosen for specific strengths:
- **AWS Lambda**: Best cold start times and generous free tier for data collection
- **GCP BigQuery**: Unmatched analytics performance and 1TB/month free queries
- **Azure Functions**: Excellent integration options and reliable execution

## Quick Start

### Local Development (Recommended for Testing)

```bash
# Clone the repository
git clone https://github.com/yourusername/urban-mobility-pipeline
cd urban-mobility-pipeline

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run src/urban_mobility/dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`.

### Production Deployment

For production deployment with full cloud integration:

1. Deploy the base multi-cloud framework (see framework documentation)
2. Configure cloud credentials in environment variables
3. Run the pipeline with cloud connectors enabled

```bash
# Set environment variables
export GCP_PROJECT=your-project-id
export AZURE_STORAGE_ACCOUNT=your-account

# Run pipeline for a specific city
python -m urban_mobility.pipeline \
    --lat -23.5505 \
    --lon -46.6333 \
    --radius 2000 \
    --city sao_paulo
```

## Features

### Data Collection
- Real-time queries to OpenStreetMap Overpass API
- Automatic retry logic and rate limiting
- Support for multiple transport types (bus, metro, tram, train, ferry)
- Route and operator information extraction

### Analytics
- Accessibility metrics (wheelchair, shelter, seating)
- Transport type distribution
- Coverage density analysis
- Route availability tracking

### Visualization
- Interactive maps with multiple tile styles
- Color-coded transport stops
- Density heatmaps
- Detailed popup information
- Filterable data tables

### Data Export
- CSV format for spreadsheet analysis
- JSON format for programmatic access
- BigQuery integration for SQL queries

## Project Structure

```
urban-mobility-pipeline/
├── src/
│   └── urban_mobility/
│       ├── pipeline.py      # Core pipeline logic
│       └── dashboard.py     # Streamlit interface
├── tests/                   # Unit and integration tests
├── terraform/               # Infrastructure as code
├── docs/                    # Additional documentation
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Usage Examples

### Analyzing São Paulo's Metro Network

```python
from urban_mobility.pipeline import UrbanMobilityPipeline

config = {
    'gcp_project': 'my-project',
    'azure_account': 'mystorageaccount'
}

pipeline = UrbanMobilityPipeline(config)

# Fetch stops near Sé station
stops = pipeline.fetch_transport_stops(
    latitude=-23.5504,
    longitude=-46.6334,
    radius=1000
)

# Calculate metrics
metrics = pipeline.calculate_metrics(stops)
print(f"Found {metrics['total_stops']} stops")
print(f"Wheelchair accessible: {metrics['accessibility']['wheelchair_pct']}%")

# Store in BigQuery
pipeline.process_and_store(stops, city='sao_paulo')
```

### Running the Dashboard

The dashboard provides a no-code interface for exploring transport data:

1. Select a city from the dropdown or enter custom coordinates
2. Adjust the search radius
3. Click "Fetch Transport Data"
4. Explore the interactive map and analytics
5. Export data as needed

## Configuration

### Environment Variables

```bash
# GCP Configuration
export GCP_PROJECT=your-project-id
export GCP_DATASET=urban_mobility

# Azure Configuration
export AZURE_STORAGE_ACCOUNT=your-account-name
export AZURE_STORAGE_KEY=your-storage-key

# AWS Configuration (if using Lambda collection)
export AWS_REGION=us-east-1
```

### Pipeline Configuration

Create a `config.yaml` file:

```yaml
cities:
  sao_paulo:
    latitude: -23.5505
    longitude: -46.6333
    radius: 3000
  
  rio:
    latitude: -22.9068
    longitude: -43.1729
    radius: 3000

pipeline:
  batch_size: 100
  retry_attempts: 3
  cache_ttl: 300  # seconds
```

## Cost Considerations

The pipeline is designed to run entirely on free tier services:

| Service | Free Tier | Monthly Cost |
|---------|-----------|--------------|
| AWS Lambda | 1M requests | $0 |
| GCP BigQuery | 1TB queries | $0 |
| Azure Functions | 1M executions | $0 |
| Streamlit Cloud | 1 app | $0 |

**Total: $0/month** for typical usage

If you exceed free tiers (unlikely for most users):
- AWS Lambda: ~$0.20 per additional 1M requests
- GCP BigQuery: ~$5 per additional TB
- Azure Functions: ~$0.20 per additional 1M executions

## Development

### Running Tests

```bash
# Unit tests
pytest tests/

# With coverage
pytest --cov=urban_mobility tests/
```

### Code Style

This project follows standard Python conventions:
- PEP 8 style guide
- Type hints for function signatures
- Docstrings in Google format
- Black for formatting

```bash
# Format code
black src/

# Type checking
mypy src/
```

## Contributing

Contributions are welcome! A few areas where help would be appreciated:

1. **Additional data sources**: Integrating GTFS feeds, real-time APIs
2. **ML features**: Demand prediction, anomaly detection
3. **UI improvements**: Additional visualizations, better mobile support
4. **Documentation**: More examples, tutorials, translations

Please open an issue before starting major work to discuss the approach.

## Roadmap

Planned features for future releases:

- [ ] Real-time data updates via WebSocket
- [ ] Historical trend analysis
- [ ] Predictive analytics (demand forecasting)
- [ ] Multi-language support
- [ ] Mobile app
- [ ] API endpoint for programmatic access
- [ ] Integration with GTFS feeds

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- OpenStreetMap community for providing excellent open data
- Multi-Cloud Data Pipeline Framework for the foundation
- Streamlit team for the dashboard framework

## Contact

**Alexandre F. Costa**
- Email: alexandre.portella03@gmail.com
- GitHub: [@AlexandreFCosta](https://github.com/AlexandreFCosta)
- LinkedIn: [Alexandre Costa](https://www.linkedin.com/in/alexandrefeitosacosta/)

For bugs and feature requests, please use the GitHub issue tracker.

---

*This project was developed as part of a portfolio showcasing data engineering and cloud architecture skills.*
