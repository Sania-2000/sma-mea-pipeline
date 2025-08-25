import os
import pandas as pd
import numpy as np
import yaml
from scipy.signal import find_peaks
from mea_pipeline.plotting import plot_spikes

def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def detect_spikes():
    cfg = load_config()

    input_dir = os.path.join(cfg["output_dir"], "cleaned")
    mask_out_dir = os.path.join(cfg["output_dir"], "spike", "masks")
    info_out_dir = os.path.join(cfg["output_dir"], "spike", "info")
    os.makedirs(mask_out_dir, exist_ok=True)
    os.makedirs(info_out_dir, exist_ok=True)

    thresh_mult = float(cfg["spike_threshold_multiplier"])

    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith(".csv"):
            continue

        print(f"Detecting spikes in: {filename}")
        filepath = os.path.join(input_dir, filename)
        df = pd.read_csv(filepath)
        timestamps = df["timestamps"].values
        duration = timestamps[-1] - timestamps[0]

        spike_df = pd.DataFrame({"timestamps": timestamps})
        channel_info = []

        for ch in df.columns[1:]:
            signal = df[ch].values
            noise_std = np.std(signal)

           
            threshold = thresh_mult * noise_std
            spike_idx_pos, _ = find_peaks(signal, height=threshold, distance=int(0.001 * cfg["fs"]))
            spike_idx_neg, _ = find_peaks(-signal, height=threshold, distance=int(0.001 * cfg["fs"]))
            spike_indices = np.sort(np.concatenate([spike_idx_pos, spike_idx_neg]))

            spike_times = timestamps[spike_indices]
            spike_df[ch] = 0
            spike_df.loc[spike_indices, ch] = 1

            isis = np.diff(spike_times)

            channel_info.append({
                "file": filename,
                "channel": ch,
                "spike_count": len(spike_indices),
                "firing_rate": len(spike_indices) / duration if duration > 0 else 0,
                "isi_mean": np.mean(isis) if len(isis) > 0 else np.nan,
                "isi_std": np.std(isis) if len(isis) > 0 else np.nan,
                "isi_cv": np.std(isis)/np.mean(isis) if len(isis) > 1 and np.mean(isis) > 0 else np.nan,
                "max_amplitude": np.max(signal[spike_indices]) if len(spike_indices) > 0 else np.nan,
                "mean_amplitude": np.mean(signal[spike_indices]) if len(spike_indices) > 0 else np.nan
            })

            if list(df.columns[1:]).index(ch) < 3:  
                plot_spikes(timestamps, signal, spike_indices, threshold, f"{filename} – {ch}",
                            os.path.join(info_out_dir, f"{filename.replace('.csv','')}_{ch}_spikes.png"))

        spike_df.to_csv(os.path.join(mask_out_dir, filename.replace(".csv", "_spikes.csv")), index=False)
        pd.DataFrame(channel_info).to_csv(os.path.join(info_out_dir, filename.replace(".csv", "_spikes_info.csv")), index=False)

        print(f"Saved mask and info for {filename}")
