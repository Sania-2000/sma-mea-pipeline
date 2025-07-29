# SMA-MEA Feature Extraction Pipeline

This project provides a fully automated pipeline for processing microelectrode array (MEA) recordings from iPSC-derived neuromuscular junctions, with a focus on distinguishing **Spinal Muscular Atrophy (SMA)** from healthy controls.

---

## Key Features

- **Signal cleaning** with artifact removal
- **Spike detection** using adaptive thresholding
- **SNR analysis** per channel
- **Feature extraction** (ISI, burst stats, amplitude, etc.)
-  Organized output folders and diagnostic plots

---

##  Folder Structure

SMA_PIPELINE/
├── config/
│ └── config.yaml # Pipeline parameters (e.g. thresholds)
├── data/
│ ├── raw/ # Your input .csv files (recordings)
│ └── cleaned/ # Cleaned versions after artifact removal
├── output/
│ ├── cleaned_plots/ #  Cleaned signal preview plots
│ ├── spike/
│ │ ├── data/ # Spike stats, .csv and .txt
│ │ └── plots/ # Spike visualization
│ ├── snr/ # SNR results per channel
│ └── features/ # Final extracted features (CSV)
├── mea_pipeline/ # Main logic modules
│ ├── cleaner.py # Handles signal cleaning and artifact interpolation
│ ├── spikes.py # Spike detection logic
│ ├── snr.py # Signal-to-noise ratio calculation
│ ├── features.py # Extracts neural features like ISI, bursts
│ ├── plotting.py # All plot utilities in one place
│ └── pipeline.py # Glue code: runs all steps in order
├── run_pipeline.py # Entry-point to run the full pipeline
├── requirements.txt # All Python dependencies
└── README.md # This file


---

## Quickstart

### 1. Install Dependencies

pip install -r requirements.txt
Required: Python ≥ 3.8, numpy, pandas, matplotlib, seaborn, PyYAML

2. Add Your Data
Place your .csv files into:
data/raw/
Each file must contain:

timestamps column (in seconds)
Signal channels named like highpass_A-001_values, etc.

3. Run the Pipeline
python run_pipeline.py
This runs:

cleaner.py: removes dead channels & artifacts

spikes.py: detects spikes above adaptive threshold

snr.py: calculates mean spike-to-noise ratio

features.py: computes burst, firing rate, amplitude

All plots + CSVs are saved in /output/

Outputs
Output	Format	Location
Cleaned signal CSVs	.csv	data/cleaned/
Cleaned plots	.png	output/cleaned_plots/
Spike summaries	.txt	output/spike/data/
Spike detection plots	.png	output/spike/plots/
SNR values per channel	.csv	output/snr/
Full feature table	.csv	output/features/features_summary.csv

Configuration (config/config.yaml)
You can tune:

z_score_threshold: 3.0              # Artifact detection sensitivity
spike_threshold_multiplier: 4       # For spike detection threshold
noise_threshold: 0.001              # For SNR filter
max_valid_snr: 1000
channels_per_plot: 6
duration: 10
plot_start_time: 0
downsample_factor: 50

Author
Sania Fatima
M1 Genomics — IGMM Internship 2024
