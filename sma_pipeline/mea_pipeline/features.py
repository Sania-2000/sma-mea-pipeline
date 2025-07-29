import os
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
from mea_pipeline.plotting import plot_spikes

def extract_features():
    input_dir = "Data/cleaned"
    snr_dir = "output/snr"
    output_dir = "output/features"
    plot_dir = os.path.join(output_dir, "plots")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    FS = 30303.03
    THRESHOLD_STD = 7
    MIN_SPIKE_INTERVAL = 0.001
    BURST_END_MAX_INTERVAL = 0.2
    MIN_BURST_DURATION = 0.5
    MIN_SPIKES_PER_BURST = 5

    all_features = []

    for fname in sorted(os.listdir(input_dir)):
        if not fname.endswith("_cleaned.csv"):
            continue

        base = fname.replace("_cleaned.csv", "")
        file_path = os.path.join(input_dir, fname)
        df = pd.read_csv(file_path)
        timestamps = df["timestamps"].to_numpy()
        duration = timestamps[-1] - timestamps[0]
        channels = [c for c in df.columns if c != "timestamps"]

        # Load SNR data
        snr_path = os.path.join(snr_dir, f"{base}_snr.csv")
        snr_data = pd.read_csv(snr_path) if os.path.exists(snr_path) else pd.DataFrame()

        for ch in channels:
            signal = df[ch].to_numpy()
            threshold = THRESHOLD_STD * np.std(signal)
            min_samples = int(MIN_SPIKE_INTERVAL * FS)
            spike_indices, _ = find_peaks(signal, height=threshold, distance=min_samples)
            spike_times = timestamps[spike_indices]
            isis = np.diff(spike_times)

            # Burst detection
            bursts = []
            current = []

            for i in range(len(spike_times)):
                if not current:
                    current.append(spike_times[i])
                else:
                    interval = spike_times[i] - spike_times[i - 1]
                    if interval <= BURST_END_MAX_INTERVAL:
                        current.append(spike_times[i])
                    else:
                        if len(current) >= MIN_SPIKES_PER_BURST and (current[-1] - current[0]) >= MIN_BURST_DURATION:
                            bursts.append(current)
                        current = [spike_times[i]]

            if current and len(current) >= MIN_SPIKES_PER_BURST and (current[-1] - current[0]) >= MIN_BURST_DURATION:
                bursts.append(current)

            burst_durations = [b[-1] - b[0] for b in bursts]
            spikes_per_burst = [len(b) for b in bursts]
            amplitudes = signal[spike_indices] if len(spike_indices) > 0 else []
            snr_row = snr_data[snr_data["channel"] == ch]
            snr_val = snr_row["SNR"].values[0] if not snr_row.empty else None

            all_features.append({
                "chunk": base,
                "channel": ch,
                "duration_sec": duration,
                "spike_count": len(spike_indices),
                "firing_rate_hz": len(spike_indices) / duration if duration > 0 else 0,
                "mean_isi": np.mean(isis) if len(isis) > 0 else np.nan,
                "median_isi": np.median(isis) if len(isis) > 0 else np.nan,
                "cv_isi": np.std(isis) / np.mean(isis) if len(isis) > 1 and np.mean(isis) > 0 else np.nan,
                "burst_count": len(bursts),
                "mean_burst_duration": np.mean(burst_durations) if burst_durations else np.nan,
                "mean_spikes_per_burst": np.mean(spikes_per_burst) if spikes_per_burst else np.nan,
                "max_amplitude": np.max(amplitudes) if len(amplitudes) > 0 else np.nan,
                "mean_amplitude": np.mean(amplitudes) if len(amplitudes) > 0 else np.nan,
                "snr": snr_val
            })

            #  Only plot the first channel per file
            if ch == channels[0]:
                plot_path = os.path.join(plot_dir, f"{base}_{ch}_features.png")
                plot_spikes(
                    timestamps=timestamps,
                    signal=signal,
                    spike_indices=spike_indices,
                    threshold=threshold,
                    title=f"{base} – {ch}",
                    out_path=plot_path
                )

    df_out = pd.DataFrame(all_features)
    df_out.to_csv(os.path.join(output_dir, "features_summary.csv"), index=False)
    print("✔ Full feature extraction completed.")
