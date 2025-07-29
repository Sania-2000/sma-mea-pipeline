import os
import pandas as pd
import numpy as np
import yaml
from mea_pipeline.plotting import plot_artifact_mask, plot_multi_channel_signals

def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def clean_signals():
    cfg = load_config()

    input_dir = cfg["input_dir"]
    output_dir = cfg["cleaned_dir"]
    plot_dir = os.path.join(cfg["output_dir"], "cleaned_plots")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith(".csv"):
            continue

        print(f"Cleaning: {filename}")
        filepath = os.path.join(input_dir, filename)
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()

        timestamps = df["highpass_A-000_timestamps"]
        signal_cols = [col for col in df.columns if col.startswith("highpass_") and col.endswith("_values")]

        dead = []  # No hardcoded dead channels
        live = [col for col in signal_cols if col not in dead]

        signals = df[signal_cols].copy()
        for col in dead:
            if col in signals:
                signals[col] = 0.0

        # Artifact detection
        summed_signal = signals.sum(axis=1)
        mean = summed_signal.mean()
        std = summed_signal.std()
        threshold = mean + cfg["z_score_threshold"] * std
        artifact_mask = np.abs(summed_signal) > threshold
        print(f"  Artifacts detected: {artifact_mask.sum()} timepoints")

        base = os.path.splitext(filename)[0].replace("_cleaned", "").replace("_CLEANED", "")
        plot_artifact_mask(timestamps, summed_signal, artifact_mask, threshold,
                           os.path.join(plot_dir, f"{base}_artifact_debug.png"))

        # Clean signal
        cleaned_signals = signals.copy()
        for col in live:
            cleaned_signals.loc[artifact_mask, col] = np.nan
            cleaned_signals[col] = cleaned_signals[col].interpolate(method="spline", order=2).bfill().ffill()

        cleaned_signals.drop(columns=dead, inplace=True, errors='ignore')
        cleaned_df = cleaned_signals.copy()
        cleaned_df.insert(0, "timestamps", timestamps)
        cleaned_path = os.path.join(output_dir, f"{base}_cleaned.csv")
        cleaned_df.fillna(0.0).to_csv(cleaned_path, index=False)
        print(f"  Saved: {cleaned_path}")

        # Only one sample plot (first N channels)
        d, s, n, c = cfg["duration"], cfg["plot_start_time"], cfg["downsample_factor"], cfg["channels_per_plot"]
        mask_window = (timestamps >= s) & (timestamps <= s + d)
        ts_window = timestamps[mask_window][::n]
        signals_window = cleaned_signals[mask_window].iloc[::n]
        sample_cols = signals_window.columns[:c]

        plot_multi_channel_signals(
            ts_window,
            signals_window[sample_cols],
            f"{base} - Cleaned Sample Channels",
            os.path.join(plot_dir, f"{base}_CLEANED_SAMPLE.png")
        )
