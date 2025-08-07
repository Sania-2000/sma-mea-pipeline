import os
import pandas as pd
import numpy as np
import yaml

def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def detect_spikes():
    cfg = load_config()

    input_dir = os.path.join(cfg["output_dir"], "cleaned")
    raw_out_dir = os.path.join(cfg["output_dir"], "spike", "data")
    data_out_dir = os.path.join(cfg["output_dir"], "spike", "values")
    os.makedirs(raw_out_dir, exist_ok=True)
    os.makedirs(data_out_dir, exist_ok=True)

    threshold_multiplier = float(cfg["spike_threshold_multiplier"])

    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith(".csv"):
            continue

        print(f"Detecting spikes in: {filename}")
        filepath = os.path.join(input_dir, filename)
        df = pd.read_csv(filepath)
        timestamps = df["timestamps"].values

        spike_report = []
        spike_df = pd.DataFrame({"timestamps": timestamps})

        for ch in df.columns[1:]:
            signal = df[ch].values
            abs_signal = np.abs(signal)

            mean = np.mean(abs_signal)
            std = np.std(abs_signal)
            threshold = mean + threshold_multiplier * std

            spike_mask = abs_signal > threshold
            spike_times = timestamps[spike_mask]
            spike_amplitudes = signal[spike_mask]

            spike_df[ch] = spike_mask.astype(int)

            spike_count = len(spike_times)
            max_amp = np.max(spike_amplitudes) if spike_count > 0 else 0
            mean_amp = np.mean(np.abs(spike_amplitudes)) if spike_count > 0 else 0

            spike_report.append(
                f"{ch}\tSpike count: {spike_count}\tMax amp: {max_amp:.4f}\tMean amp: {mean_amp:.4f}"
            )

       
        csv_out = os.path.join(data_out_dir, filename.replace(".csv", "_spikes.csv"))
        spike_df.to_csv(csv_out, index=False)

      
        txt_out = os.path.join(raw_out_dir, filename.replace(".csv", "_spikes_raw.txt"))
        with open(txt_out, "w") as f:
            f.write("\n".join(spike_report))

        print(f"Saved spike mask: {csv_out}")
        print(f"Saved summary log: {txt_out}")
