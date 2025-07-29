import os
import matplotlib.pyplot as plt
import seaborn as sns

def plot_spikes(timestamps, signal, spike_indices, threshold, title, out_path):
    plt.figure(figsize=(12, 4))
    plt.plot(timestamps, signal, label="Signal")
    plt.axhline(threshold, color='red', linestyle='--', label=f"Threshold")
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
