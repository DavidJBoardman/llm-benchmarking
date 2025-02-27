# LLM Benchmarking Tool

This tool provides benchmarking capabilities for Large Language Models (LLMs), collecting performance metrics and visualizing results through a Streamlit dashboard.

## Project Structure

This is a self-contained project with all paths relative to the Benchmarks directory:

```
./
├── .env.example           # Template for environment variables
├── .gitignore             # Git ignore file
├── 1_Dashboard.py         # Main Streamlit dashboard
├── benchmark.py           # Benchmark analysis script
├── collect_metrics.bash   # Script to collect performance metrics
├── info.txt               # Information about metrics collected
├── init_db.py             # Database initialization script
├── migrate_data.py        # Script to migrate data to new structure
├── setup.sh               # Setup script for environment
├── pages/                 # Additional Streamlit dashboard pages
│   ├── 2_Chat_Viewer.py   # View chat logs from benchmark runs
│   ├── 3_Chat_Audit.py    # Audit chat responses for quality
│   └── 4_Audit_History.py # View history of chat audits
├── requirements.txt       # Python dependencies
├── utils/                 # Utility functions
│   └── db.py              # Database connection utilities
└── data/                  # Directory for benchmark results (see below)
    ├── RTX4090/           # Results from RTX4090 GPU
    ├── RTX4080S/          # Results from RTX4080S GPU
    ├── ADA6000/           # Results from ADA6000 GPU
    └── ADA6000-Latest/    # Latest results from ADA6000 GPU
```

## Setup Instructions

1. Clone the repository
2. Navigate to the Benchmarks directory and run the setup script:
   ```
   cd Benchmarks
   bash setup.sh
   ```
   
   This will:
   - Create a virtual environment
   - Install dependencies
   - Set up the data directory structure
   - Create a .env file from the template

3. If you have existing benchmark data, migrate it to the new structure:
   ```
   python migrate_data.py
   ```

## Running the Benchmark

To collect benchmark metrics:

```bash
bash collect_metrics.bash
```

This script will:
1. List available language models
2. Prompt you to select a model
3. Run the model and collect performance metrics
4. Save results to a CSV file in the appropriate data directory based on your GPU

## Viewing Results

Launch the Streamlit dashboard:

```bash
streamlit run 1_Dashboard.py
```

The dashboard provides:
- Main Dashboard (1_Dashboard.py): Visualizations of GPU performance metrics, memory usage, processing times, and comparative analysis between models
- Chat Viewer (pages/2_Chat_Viewer.py): View and compare chat logs from different models and GPUs
- Chat Audit (pages/3_Chat_Audit.py): Audit chat responses for quality
- Audit History (pages/4_Audit_History.py): View history of chat audits and quality metrics

## Data Management

Benchmark results are organized by GPU type in the `data/` directory. Each directory contains:
- CSV files with raw metrics data
- TXT files with summary information
- Subdirectories for specific model configurations with log files

## Contributing

When contributing to this project:
1. Create a new branch for your changes
2. Follow the existing code style
3. Add appropriate documentation
4. Submit a pull request

## License

[Specify your license here] 