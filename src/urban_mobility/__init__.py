"""
Urban Mobility Analytics Pipeline

A production-ready implementation for analyzing public transportation networks
using the multi-cloud data pipeline framework.
"""

__version__ = "1.0.0"
__author__ = "Alexandre F. Costa"

from .pipeline import UrbanMobilityPipeline, TransportStop, TransportType

__all__ = ['UrbanMobilityPipeline', 'TransportStop', 'TransportType']
