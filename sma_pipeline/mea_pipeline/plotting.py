import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def plot_spikes(timestamps, signal, spike_indices, threshold, title, out_path):
    plt.figure(figsize=(12, 4))
    plt.plot(timestamps, signal, label="Signal")
    plt.axhline(threshold, color='red', linestyle='--', label="Threshold")
    plt.scatter(timestamps[spike_indices], signal[spike_indices], color='green', s=10, label="Spikes")
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def plot_snr_bar(df, chunk_name, out_path):
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x="channel", y="SNR")
    plt.xticks(rotation=90)
    plt.title(f"SNR per Channel – {chunk_name}")
    plt.xlabel("Channel")
    plt.ylabel("SNR")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def plot_artifact_mask(timestamps, summed_signal, artifact_mask, threshold, out_path):
    plt.figure(figsize=(12, 4))
    plt.plot(timestamps, summed_signal, label="Summed Signal")
    plt.axhline(threshold, color='red', linestyle='--', label="Artifact Threshold")
    plt.scatter(timestamps[artifact_mask], summed_signal[artifact_mask], color='red', s=10, label="Artifacts")
    plt.title("Artifact Detection Diagnostic")
    plt.xlabel("Time (s)")
    plt.ylabel("Summed Signal")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def plot_multi_channel_signals(timestamps, signals, title, out_path):
    n_channels = signals.shape[1]
    fig, axs = plt.subplots(n_channels, 1, figsize=(12, 2.5 * n_channels), sharex=True)
    for i, col in enumerate(signals.columns):
        axs[i].plot(timestamps, signals[col])
        axs[i].set_title(col)
        axs[i].grid(True)
    fig.suptitle(title)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

def plot_group_feature_boxplot(df, feature, out_path):
    if "group" not in df.columns:
        print(f"[Warning] 'group' column missing – skipping {feature}")
        return
    if df["group"].nunique() < 2:
        print(f"[Warning] Only one group found – skipping {feature}")
        return

    plt.figure(figsize=(8, 5))
    sns.boxplot(x="group", y=feature, data=df, palette="Set2")
    plt.title(f"{feature} – SMA vs Healthy")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
    print(f"Saved: {out_path}")

def plot_group_means_barplot(mean_csv_path, out_path):
    df = pd.read_csv(mean_csv_path)

    
    df_melted = df.melt(id_vars="Feature", var_name="Group", value_name="MeanValue")

    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_melted, x="Feature", y="MeanValue", hue="Group", palette="Set2")
    plt.title("Feature Mean Comparison: SMA vs Healthy")
    plt.xticks(rotation=45, ha='right')
    plt.ylabel("Mean Value")
    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path)
    plt.close()
    print(f"Saved mean comparison plot: {out_path}")
def plot_feature_summary_bars(summary_csv_path, out_dir):
    df = pd.read_csv(summary_csv_path)
    if df.empty:
        print("⚠ No feature data to plot.")
        return

    os.makedirs(out_dir, exist_ok=True)
    feature_keys = [col for col in df.columns if "_count" in col or "_rate" in col or "_isi_" in col]

    feature_groups = {
        "Spike Count": [k for k in feature_keys if "_count" in k],
        "Firing Rate": [k for k in feature_keys if "_rate" in k],
        "ISI Mean": [k for k in feature_keys if "_isi_mean" in k],
        "ISI Std": [k for k in feature_keys if "_isi_std" in k],
    }

    for label, cols in feature_groups.items():
        if not cols:
            continue

        values = df[cols].iloc[0]
        channels = [c.replace("_count", "").replace("_rate", "").replace("_isi_mean", "").replace("_isi_std", "") for c in cols]

        plt.figure(figsize=(12, 4))
        plt.bar(channels, values)
        plt.title(f"{label} per Channel")
        plt.xlabel("Channel")
        plt.ylabel(label)
        plt.xticks(rotation=45)
        plt.tight_layout()
        path = os.path.join(out_dir, f"{label.replace(' ', '_').lower()}.png")
        plt.savefig(path)
        plt.close()
        print(f" Saved: {path}")
