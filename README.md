# pei-nwdaf-network-producer

> Project for PEI evaluation 25/26

## Overview

Data producer component that reads network measurement data from CSV files and streams it to the NWDAF ingestion service. Simulates real-time data streaming for ML-driven 5G network analysis using the DoNext dataset.

## Technologies

- **Python** 3.11+
- **Pandas** 2.3.3 - CSV reading and data manipulation
- **Requests** 2.32.5 / **HTTPx** 0.28.1 - HTTP clients
- **FastAPI** 0.121.3 - For testing endpoints
- **pytest** 9.0.1 - Testing framework
- **Docker/Docker Compose** - Containerization
- **uv** - Python package installer and runner

## Key Features

- **CSV streaming**: Chunk-based reading for memory efficiency (10K rows/chunk)
- **Batch sending**: Configurable batch size and time-based flushing
- **HTTP integration**: POST requests to FastAPI ingestion service
- **Timestamp attachment**: Automatic timestamp addition to data
- **Flexible configuration**: CLI arguments for file path, interval, API URL
- **Error handling**: Timeouts and retry logic

## Usage

Extract datasets:
```bash
tar -xJf data.tar.xz
```

Run producer:
```bash
python main.py -f merged/latency_data.csv -i 0.5 -a http://data-ingestion:7000/receive
```

### CLI Arguments

- `-f/--file`: Path to CSV file
- `-i/--interval`: Delay between reading lines (seconds)
- `-a/--api`: Target API URL
- `-s/--send`: Batch send interval
- `-y/--type`: Data type identifier

## Docker

```bash
docker-compose up
```

## Directory Structure

```
producer/
├── main.py              # Entry point - CLI for running producer
├── src/
│   ├── csv_reader.py    # CSV streaming reader with chunking
│   ├── sender.py        # HTTP sender for batching
│   └── __init__.py
├── tests/
│   ├── test_csv_reader.py  # CSV functionality tests
│   ├── test_sender.py      # HTTP sending tests
│   ├── test.csv            # Sample test data
│   └── api_app.py          # Mock API for testing
├── merged/              # Dataset files directory
└── data.tar.xz          # Compressed dataset archive
```

## Dataset Attribution

Uses the **DoNext dataset** from Schippers et al. (2025):

```
@Article{Schippers.etal/2025a,
    Author = {Hendrik Schippers and Melina Geis and Stefan B{\"o}cker and Christian Wietfeld},
    Title = {{DoNext: A}n Open-Access Measurement Dataset for Machine Learning-Driven {5G} Mobile Network Analysis},
    Journal = {{IEEE} Transactions on Machine Learning in Communications and Networking},
    Volume = {3},
    Number = {},
    Pages = {585-604},
    Year = {2025},
    Month = {apr},
    Doi = {10.1109/TMLCN.2025.3564239},
  	Keywords = {5G new radio; 6G; dataset; machine learning; predictive QoS; multi-MNO; channel modelling; transfer learning},
    Project = {6GEM, CC5G.NRW, VIZIT},
}
```

**Note:** The dataset has been altered (merged) for this project.

## Testing

```bash
pytest tests/
```

Includes unit tests for CSV reader operations and HTTP sender integration tests with mock FastAPI server.
