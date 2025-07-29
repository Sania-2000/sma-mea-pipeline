# SMA-MEA Feature Extraction Pipeline

This repository provides a fully automated pipeline for analyzing microelectrode array (MEA) recordings from iPSC-derived neuromuscular junctions, focused on identifying key neural features for distinguishing Spinal Muscular Atrophy (SMA) from healthy controls.

---

## Features

- Signal cleaning with artifact detection and interpolation
- Spike detection using adaptive thresholds
- SNR (Signal-to-Noise Ratio) analysis
- Extraction of features including:
  - Firing rate
  - ISI (inter-spike intervals)
  - Bursts
  - Spike amplitude
- Organized, reproducible output structure
- Configurable via `config.yaml`

---

## Repository Structure

SMA_PIPELINE/
├── config/
│ └── config.yaml # Pipeline parameters (thresholds, settings)
├── data/
│ ├── raw/ # Input .csv files
│ └── cleaned/ # Output after signal cleaning
├── output/
│ ├── cleaned_plots/ # Plots of cleaned signals
│ ├── spike/
│ │ ├── data/ # Spike metrics (.csv, .txt)
│ │ └── plots/ # Spike detection plots
│ ├── snr/ # SNR results
│ └── features/ # Final feature summaries
├── mea_pipeline/ # Core processing modules
│ ├── cleaner.py # Signal cleaning
│ ├── spikes.py # Spike detection
│ ├── snr.py # SNR calculation
│ ├── features.py # Feature extraction
│ ├── plotting.py # All plotting utilities
│ └── pipeline.py # Pipeline controller
├── run_pipeline.py # Entry-point script
├── requirements.txt # Python dependencies
└── README.md # This file
## Quickstart

### Install Requirements
pip install -r requirements.txt
### Usage
### 1. Prepare Input Data
Place your .csv recordings inside the data/raw/ directory.
Each file must contain:
A timestamps column in seconds
One or more signal channels with names like:
highpass_A-001_values, highpass_B-005_values, etc.

### 2. Run the Pipeline
From the project root directory:
python run_pipeline.py
This will
Clean signals
Detect spikes
Calculate SNR
Extract features
### All results are saved under the output/ directory.
Output Summary
Output File/Folder	Description
data/cleaned/	Cleaned signal CSVs
output/cleaned_plots/	Signal cleaning visualizations
output/spike/data/	Spike metrics for each channel
output/spike/plots/	Spike detection overlays
output/snr/	Per-channel SNR results
output/features/features_summary.csv	Comprehensive feature table

### Configuration
All parameters can be customized in config/config.yaml. Example:
z_score_threshold: 3.0
spike_threshold_multiplier: 4
noise_threshold: 0.001
max_valid_snr: 1000
channels_per_plot: 6
duration: 10
plot_start_time: 0
downsample_factor: 50
dead_channels: []
### Author
Sania Fatima
M1 Genomics – IGMM Internship, 2024
