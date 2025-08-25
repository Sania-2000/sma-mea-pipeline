import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import mannwhitneyu

def run_feature_comparison(features_file="output/features/features_summary.csv", output_dir="output/features"):
    if not os.path.exists(features_file):
        return

    df = pd.read_csv(features_file)
    grouped = df.groupby("group").mean(numeric_only=True)
    grouped.to_csv(os.path.join(output_dir, "grouped_features.csv"))

    features = ["spike_count", "firing_rate", "isi_mean", "burst_count", "mean_spikes_per_burst"]

    sns.set_theme(style="whitegrid")
    sns.set_context("talk")

    for feat in features:
        if feat in df.columns:
            plt.figure(figsize=(7,6))
            ax = sns.barplot(data=df, x="group", y=feat, palette=["#4C72B0", "#55A868"], errorbar=None)
            for patch in ax.patches:
                patch.set_edgecolor("black")
                patch.set_linewidth(1.2)
            plt.title(f"{feat.replace('_',' ').title()} – Healthy vs SMA", fontsize=16, weight="bold")
            plt.ylabel(feat.replace("_"," ").title(), fontsize=14)
            plt.xlabel("")
            plt.xticks(fontsize=13, weight="bold")
            plt.yticks(fontsize=12)
            out_path = os.path.join(output_dir, f"{feat}_barplot.png")
            plt.savefig(out_path, dpi=300, bbox_inches="tight")
            plt.close()

    results = []
    for feat in features:
        if feat in df.columns:
            h_vals = df[df["group"]=="Healthy"][feat].dropna()
            s_vals = df[df["group"]=="SMA"][feat].dropna()
            if len(h_vals) > 0 and len(s_vals) > 0:
                _, p = mannwhitneyu(h_vals, s_vals, alternative="two-sided")
                results.append({"feature": feat, "p_value": p})

    pd.DataFrame(results).to_csv(os.path.join(output_dir, "feature_stats.csv"), index=False)
