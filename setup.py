"""Setup configuration for urban mobility pipeline."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="urban-mobility-pipeline",
    version="1.0.0",
    author="Alexandre F. Costa",
    author_email="alexandre.portella03@gmail.com",
    description="Multi-cloud pipeline for urban mobility analytics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlexandreFCosta/urban-mobility-pipeline",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "streamlit>=1.31.0",
        "folium>=0.15.0",
        "plotly>=5.18.0",
        "pandas>=2.1.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "cloud": [
            "boto3>=1.34.0",
            "google-cloud-bigquery>=3.14.0",
            "azure-functions>=1.18.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "black>=23.12.0",
            "mypy>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "urban-mobility=urban_mobility.pipeline:main",
        ],
    },
)
