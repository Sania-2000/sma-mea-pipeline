import os
import pandas as pd
import numpy as np
import yaml
from mea_pipeline.plotting import plot_group_feature_boxplot

def load_config():
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)

def extract_channel_id(colname):
    parts = colname.split("_")
    for p in parts:
        if "-" in p:
            return p
    return colname

def get_channel_group(channel_id):
    if channel_id.startswith("A") or channel_id.startswith("B"):
        return "SMA"
    elif channel_id.startswith("C") or channel_id.startswith("D"):
        return "Healthy"
    else:
        return "Unknown"

def run_feature_comparison():
    cfg = load_config()

    spike_dir = os.path.join(cfg["output_dir"], "spike", "values")
    output_dir = os.path.join(cfg["output_dir"], "features")
    os.makedirs(output_dir, exist_ok=True)

    all_channel_features = []

    for filename in sorted(os.listdir(spike_dir)):
        if not filename.endswith("_spikes.csv"):
            continue

        filepath = os.path.join(spike_dir, filename)
        df = pd.read_csv(filepath)
        timestamps = df["timestamps"].values
        duration = timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 1

        for col in df.columns[1:]:
            channel_id = extract_channel_id(col)
            group = get_channel_group(channel_id)

            spikes = df[col].values
            spike_times = timestamps[spikes == 1]

            spike_count = len(spike_times)
            firing_rate = spike_count / duration if duration > 0 else 0
            isi = np.diff(spike_times)
            mean_isi = np.mean(isi) if len(isi) > 0 else 0
            std_isi = np.std(isi) if len(isi) > 0 else 0

            all_channel_features.append({
                "file": filename,
                "channel": channel_id,
                "group": group,
                "spike_count": spike_count,
                "firing_rate": firing_rate,
                "isi_mean": mean_isi,
                "isi_std": std_isi
            })

    summary_csv = os.path.join(output_dir, "features_summary.csv")

    if all_channel_features:
        df = pd.DataFrame(all_channel_features)
        df.to_csv(summary_csv, index=False)
        print(f"Feature summary saved: {summary_csv}")
        print(f"Total channel-feature rows: {len(df)}")

        for feature in ["spike_count", "firing_rate", "isi_mean", "isi_std"]:
            out_path = os.path.join(output_dir, f"{feature}_boxplot.png")
            plot_group_feature_boxplot(df, feature, out_path)
    else:
        print("No features extracted! Check spike CSVs.")
