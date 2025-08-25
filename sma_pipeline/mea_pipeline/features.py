import os
import numpy as np
import pandas as pd
from scipy.signal import find_peaks

def extract_features(output_dir="output/features", cleaned_dir="output/cleaned", fs=30000, thresh_mult=4, burst_isi=0.1):
    os.makedirs(output_dir, exist_ok=True)
    all_results = []

    for fname in sorted(os.listdir(cleaned_dir)):
        if not fname.endswith("_cleaned.csv"):
            continue

        cleaned_file = os.path.join(cleaned_dir, fname)
        df = pd.read_csv(cleaned_file)
        if "timestamps" not in df.columns:
            continue

        timestamps = df["timestamps"].values
        ts_sec = timestamps if timestamps[1] - timestamps[0] < 1 else timestamps / fs
        duration = ts_sec[-1] - ts_sec[0]

        all_signals = df.drop(columns=["timestamps"]).values.flatten()
        global_noise_std = np.std(all_signals)
        global_threshold = thresh_mult * global_noise_std

        for col in df.columns:
            if col == "timestamps":
                continue

            signal = df[col].values

            pos_peaks, _ = find_peaks(signal, height=global_threshold, distance=int(0.001 * fs))
            neg_peaks, _ = find_peaks(-signal, height=global_threshold, distance=int(0.001 * fs))
            spike_idx = np.sort(np.concatenate([pos_peaks, neg_peaks]))

            spike_times = ts_sec[spike_idx]
            spike_count = len(spike_times)
            firing_rate = spike_count / duration if duration > 0 else np.nan

            isi = np.diff(spike_times)
            isi_mean = np.mean(isi) if len(isi) > 0 else np.nan

            bursts = []
            if len(isi) > 0:
                current_burst = [spike_times[0]]
                for i in range(1, len(spike_times)):
                    if (spike_times[i] - spike_times[i-1]) <= burst_isi:
                        current_burst.append(spike_times[i])
                    else:
                        if len(current_burst) > 1:
                            bursts.append(current_burst)
                        current_burst = [spike_times[i]]
                if len(current_burst) > 1:
                    bursts.append(current_burst)

            burst_count = len(bursts)
            mean_spikes_per_burst = np.mean([len(b) for b in bursts]) if burst_count > 0 else np.nan

            group = "Healthy" if col.startswith(("highpass_C", "highpass_D")) else "SMA"

        
            if firing_rate > 100 or (isi_mean is not np.nan and isi_mean < 0.002):
                continue

            all_results.append({
                "file": fname,
                "channel": col,
                "spike_count": spike_count,
                "firing_rate": firing_rate,
                "isi_mean": isi_mean,
                "burst_count": burst_count,
                "mean_spikes_per_burst": mean_spikes_per_burst,
                "group": group
            })

    if not all_results:
        print(" No valid features extracted")
        return

    df_out = pd.DataFrame(all_results)
    out_file = os.path.join(output_dir, "features_summary.csv")
    df_out.to_csv(out_file, index=False)
    print(f"Features saved to {out_file}")
    return df_out


if __name__ == "__main__":
    extract_features()
