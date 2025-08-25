import os
import matplotlib.pyplot as plt
import seaborn as sns

def ensure_dir(path):
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)

def _finalize_plot(out_path, show=False):
    plt.tight_layout()
    if out_path:
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        print(f"Saved plot → {out_path}")
    if show:
        plt.show()
    plt.close()

def plot_spikes(timestamps, signal, spike_indices, threshold, title, out_path=None, show=False):
    ensure_dir(out_path)
    plt.figure(figsize=(12, 4))
    plt.plot(timestamps, signal, label="Signal")
    plt.axhline(threshold, color="red", linestyle="--", label="Threshold")
    plt.axhline(-threshold, color="red", linestyle="--")
    plt.scatter(timestamps[spike_indices], signal[spike_indices], color="green", s=10, label="Spikes")
    plt.title(title)
    plt.legend()
    _finalize_plot(out_path, show)

def plot_artifact_mask(timestamps, summed_signal, artifact_mask, threshold, out_path=None, show=False):
    ensure_dir(out_path)
    plt.figure(figsize=(12, 4))
    plt.plot(timestamps, summed_signal, label="Summed Signal")
    plt.axhline(threshold, color="red", linestyle="--")
    plt.scatter(timestamps[artifact_mask], summed_signal[artifact_mask], color="red", s=10)
    plt.title("Artifact Detection")
    _finalize_plot(out_path, show)

def plot_multi_channel_signals(timestamps, signals, title, out_path=None, show=False):
    ensure_dir(out_path)
    fig, axs = plt.subplots(signals.shape[1], 1, figsize=(12, 2*signals.shape[1]), sharex=True)
    for i, col in enumerate(signals.columns):
        axs[i].plot(timestamps, signals[col])
        axs[i].set_title(col)
    fig.suptitle(title)
    _finalize_plot(out_path, show)

def plot_snr_bar(df, chunk_name, out_path=None, show=False):
    ensure_dir(out_path)
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x="channel", y="SNR", palette="Set2", errorbar=None)
    plt.xticks(rotation=90)
    plt.title(f"SNR per Channel – {chunk_name}")
    plt.xlabel("Channel")
    plt.ylabel("SNR")
    _finalize_plot(out_path, show)

def plot_group_feature_bar(df, feature, out_path=None, show=False):
    if feature not in df.columns:
        return

    ensure_dir(out_path)
    plt.figure(figsize=(6, 5))

    group_means = df.groupby("group")[feature].mean().reindex(["Healthy", "SMA"])
    sns.barplot(x=group_means.index, y=group_means.values, palette="Set2", errorbar=None)

    plt.ylabel(feature)
    plt.title(f"{feature} – Healthy vs SMA")
    _finalize_plot(out_path, show)

def plot_all_group_features(df, out_dir="output/features", show=False):
    features = ["spike_count", "firing_rate", "isi_mean", "burst_count", "mean_spikes_per_burst"]
    for feat in features:
        if feat in df.columns:
            out_path = os.path.join(out_dir, f"{feat}_barplot.png")
            plot_group_feature_bar(df, feat, out_path, show)
