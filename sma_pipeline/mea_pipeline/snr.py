import os
import pandas as pd
import numpy as np
import yaml
from mea_pipeline.plotting import plot_snr_bar

def load_config():
    with open("config/config.yaml", "r") as f:
        cfg = yaml.safe_load(f)
        cfg["noise_threshold"] = float(cfg["noise_threshold"])
        return cfg

def compute_snr():
    cfg = load_config()
    input_dir = os.path.join(cfg["output_dir"], "cleaned")
    output_dir = os.path.join(cfg["output_dir"], "snr")
    os.makedirs(output_dir, exist_ok=True)

    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith("_cleaned.csv"):
            continue

        filepath = os.path.join(input_dir, filename)
        df = pd.read_csv(filepath)
        if "timestamps" not in df.columns:
            continue

        signals = df.drop(columns=["timestamps"])
        snr_results = []

        for col in signals.columns:
            signal = signals[col]
            noise_std = signal[signal.abs() < cfg["noise_threshold"]].std()
            signal_max = signal.max()
            snr = signal_max / noise_std if noise_std != 0 else 0.0
            snr_results.append((col, snr))

        base = os.path.splitext(filename)[0]

     
        out_txt = os.path.join(output_dir, f"{base}_snr.txt")
        with open(out_txt, "w") as f:
            for ch, snr_val in snr_results:
                f.write(f"{ch}\tSNR: {snr_val:.3f}\n")
        print(f"Saved SNR report: {out_txt}")

        df_snr = pd.DataFrame(snr_results, columns=["channel", "SNR"])
        out_png = os.path.join(output_dir, f"{base}_snr.png")
        plot_snr_bar(df_snr, base, out_png)
