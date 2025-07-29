import os
import re
import pandas as pd
import yaml
from mea_pipeline.plotting import plot_snr_bar

def load_config():
    with open("config/config.yaml", "r") as f:
        cfg = yaml.safe_load(f)
        cfg["noise_threshold"] = float(cfg["noise_threshold"])
        cfg["max_valid_snr"] = float(cfg["max_valid_snr"])
        cfg["spike_threshold_multiplier"] = float(cfg["spike_threshold_multiplier"])
        return cfg

def extract_val(pattern, line):
    m = re.search(pattern, line)
    return float(m.group(1)) if m else None

def compute_snr():
    cfg = load_config()
    spike_dir = os.path.join("output", "spike", "data")
    out_dir = os.path.join("output", "snr")
    plot_dir = os.path.join(out_dir, "plots")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(plot_dir, exist_ok=True)

    for chunk in sorted(f.replace("_spikes_raw.txt", "") for f in os.listdir(spike_dir) if f.endswith("_spikes_raw.txt")):
        spikes_file = os.path.join(spike_dir, f"{chunk}_spikes_raw.txt")
        raw_file = os.path.join(spike_dir, f"{chunk}_abs.csv")
        if not os.path.exists(spikes_file) or not os.path.exists(raw_file):
            continue

        df = pd.read_csv(raw_file)
        signal_data = df.drop(columns=["timestamps"])
        spike_means = {}

        with open(spikes_file) as f:
            for line in f:
                ch = re.match(r"(\S+)", line).group(1)
                mean_spike = extract_val(r"Mean Amplitude: ([\d\.\-eE]+)", line)
                if mean_spike is not None:
                    spike_means[ch] = mean_spike

        rows = []
        for ch in spike_means:
            if ch not in signal_data.columns:
                continue
            signal = signal_data[ch]
            noise = signal.copy()
            thresh = signal.mean() + cfg["spike_threshold_multiplier"] * signal.std()
            noise[signal > thresh] = None
            noise_mean = noise.abs().dropna().mean()
            if pd.isna(noise_mean) or noise_mean < cfg["noise_threshold"]:
                continue
            snr = spike_means[ch] / noise_mean
            if snr > cfg["max_valid_snr"]:
                continue
            rows.append({
                "chunk": chunk, "channel": ch,
                "mean_spike": spike_means[ch],
                "mean_noise": noise_mean,
                "SNR": snr
            })

        snr_csv_path = os.path.join(out_dir, f"{chunk}_snr.csv")

        if rows:
            df_out = pd.DataFrame(rows)
            df_out.to_csv(snr_csv_path, index=False)
            plot_snr_bar(df_out, chunk, os.path.join(plot_dir, f"{chunk}_snr.png"))
        else:
            print(f"[Info] No valid SNR rows for {chunk}.")
            df_out = pd.DataFrame(columns=["chunk", "channel", "mean_spike", "mean_noise", "SNR"])
            df_out.to_csv(snr_csv_path, index=False)
