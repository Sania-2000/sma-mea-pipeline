import os
import pandas as pd
from mea_pipeline.plotting import (
    plot_group_feature_boxplot,
    plot_group_means_barplot
)


def assign_group(row):
    ch = row["channel"].lower()
    if ch.startswith("highpass_a-") or ch.startswith("highpass_b-"):
        return "SMA"
    elif ch.startswith("highpass_c-") or ch.startswith("highpass_d-"):
        return "Healthy"
    else:
        return "Unknown"

def run_feature_comparison(
    input_csv="output/features/features_summary.csv",
    grouped_csv="output/features/grouped_feature_summary.csv",
    mean_csv="output/features/group_means.csv",
    plot_dir="output/features/plots/group_comparison"
):
   
    df = pd.read_csv(input_csv)
    print(f"Loaded {len(df)} rows from features_summary.csv")


    df["group"] = df.apply(assign_group, axis=1)
    df = df[df["group"].isin(["SMA", "Healthy"])]
    print(f"Grouped rows: {df['group'].value_counts().to_dict()}")

  
    os.makedirs(os.path.dirname(grouped_csv), exist_ok=True)
    df.to_csv(grouped_csv, index=False)
    print(f"Grouped CSV saved to: {grouped_csv}")

  
    feature_cols = [
        "spike_count", "firing_rate_hz", "mean_isi", "cv_isi",
        "burst_count", "mean_burst_duration", "mean_spikes_per_burst",
        "max_amplitude", "mean_amplitude", "snr"
    ]


    group_means = df.groupby("group")[feature_cols].mean().transpose()
    group_means.columns = [f"{g}_Mean" for g in group_means.columns]
    group_means.reset_index(inplace=True)
    group_means.rename(columns={"index": "Feature"}, inplace=True)
    group_means.to_csv(mean_csv, index=False)
    print(f" Group means saved to: {mean_csv}")

  
    os.makedirs(plot_dir, exist_ok=True)
    for feature in feature_cols:
        if feature in df.columns:
            out_path = os.path.join(plot_dir, f"{feature}_group_boxplot.png")
            plot_group_feature_boxplot(df, feature, out_path)

  
    mean_plot_path = os.path.join(plot_dir, "group_mean_barplot.png")
    plot_group_means_barplot(mean_csv, mean_plot_path)
