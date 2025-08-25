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
    output_dir = os.path.join(cfg["output_dir"], "cleaned")
    mask_dir = os.path.join(cfg["output_dir"], "artifact_masks")
    plot_dir = os.path.join(cfg["output_dir"], "cleaned_plots")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(mask_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith(".csv"):
            continue

        print(f"Cleaning: {filename}")
        filepath = os.path.join(input_dir, filename)
        df = pd.read_csv(filepath)
        df.columns = df.columns.str.strip()

        timestamps = df[df.columns[0]]
        signal_cols = [col for col in df.columns if col.endswith("_values")]
        signals = df[signal_cols].copy()

        base = os.path.splitext(filename)[0].replace("_cleaned", "").replace("_CLEANED", "")

        max_signal = signals.abs().max(axis=1)
        mean = max_signal.mean()
        std = max_signal.std()
        threshold = mean + cfg["z_score_threshold"] * std
        artifact_mask = (max_signal > threshold)
        print(f"  Artifacts detected: {artifact_mask.sum()} timepoints")

        np.save(os.path.join(mask_dir, f"{base}_artifact_mask.npy"), artifact_mask)

        plot_artifact_mask(
            timestamps,
            max_signal,
            artifact_mask,
            threshold,
            os.path.join(plot_dir, f"{base}_artifact_debug.png")
        )

        cleaned_signals = signals.copy()
        for col in cleaned_signals.columns:
            cleaned_signals.loc[artifact_mask, col] = np.nan
            cleaned_signals[col] = cleaned_signals[col].interpolate(method="spline", order=2).bfill().ffill()

        cleaned_df = cleaned_signals.copy()
        cleaned_df.insert(0, "timestamps", timestamps)
        out_path = os.path.join(output_dir, f"{base}_cleaned.csv")
        cleaned_df.to_csv(out_path, index=False)
        print(f"  Saved: {out_path}")

       
        s, d, n, c = cfg["plot_start_time"], cfg["duration"], cfg["downsample_factor"], cfg["channels_per_plot"]
        ts_window = timestamps[(timestamps >= s) & (timestamps <= s + d)][::n]
        signals_window = cleaned_signals[(timestamps >= s) & (timestamps <= s + d)].iloc[::n]

        plot_multi_channel_signals(
            ts_window,
            signals_window.iloc[:, :c],
            f"{base} - Cleaned",
            os.path.join(plot_dir, f"{base}_CLEANED_SAMPLE.png")
        )
