import os
import pandas as pd
import numpy as np
import yaml
from mea_pipeline.plotting import plot_spikes

def load_config():
    with open("config/config.yaml", "r") as f:
        cfg = yaml.safe_load(f)
        cfg["spike_threshold_multiplier"] = float(cfg["spike_threshold_multiplier"])
        return cfg

def detect_spikes():
    cfg = load_config()
    input_dir = cfg["cleaned_dir"]
    data_dir = os.path.join("output", "spike", "data")
    plot_dir = os.path.join("output", "spike", "plots")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith("_cleaned.csv"):
            continue

        filepath = os.path.join(input_dir, filename)
        df = pd.read_csv(filepath)
        if "timestamps" not in df.columns:
            continue

        timestamps = df["timestamps"]
        cleaned_signals = df.drop(columns=["timestamps"])
        abs_signals = cleaned_signals.abs()
        stats_raw = {}

        for col in abs_signals.columns:
            signal = abs_signals[col]
            threshold = signal.mean() + cfg["spike_threshold_multiplier"] * signal.std()
            spike_mask = signal > threshold
            spikes = signal[spike_mask]

            stats_raw[col] = {
                "spike_count": spike_mask.sum(),
                "max_amplitude": spikes.max() if not spikes.empty else 0.0,
                "mean_spike": spikes.mean() if not spikes.empty else 0.0,
                "spike_indices": spikes.index.tolist()
            }

        base = os.path.splitext(filename)[0].replace("_cleaned", "").replace("_CLEANED", "")
        abs_out = abs_signals.copy()
        abs_out.insert(0, "timestamps", timestamps)
        abs_out.to_csv(os.path.join(data_dir, f"{base}_abs.csv"), index=False)

        with open(os.path.join(data_dir, f"{base}_spikes_raw.txt"), "w") as f:
            for ch, data in stats_raw.items():
                f.write(f"{ch}\tSpikes: {data['spike_count']}\tMax Amplitude: {data['max_amplitude']:.3f}\t"
                        f"Mean Amplitude: {data['mean_spike']:.3f}\n")

        sample_col = abs_signals.columns[0]
        s = abs_signals[sample_col]
        ixs = stats_raw[sample_col]["spike_indices"]
        thresh = s.mean() + cfg["spike_threshold_multiplier"] * s.std()

        plot_spikes(
            timestamps, s, ixs, thresh,
            f"{base} – {sample_col}",
            os.path.join(plot_dir, f"{base}_spikes_sample.png")
        )
