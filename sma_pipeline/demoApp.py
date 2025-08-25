import os
import glob
import streamlit as st
import pandas as pd
from mea_pipeline.pipeline import run_pipeline

st.set_page_config(page_title="Spike Analysis Pipeline", layout="wide")

st.title("Spike Analysis Pipeline")
st.markdown("Select a raw file")

input_dir = "data/raw"
os.makedirs(input_dir, exist_ok=True)

files = glob.glob(os.path.join(input_dir, "*.csv"))
if not files:
    st.warning("No CSV files found in data/raw/. Please place your recordings there first.")
else:
    selected_file = st.selectbox("Choose a raw file to process", files)

   
    if "pipeline_done" not in st.session_state:
        st.session_state.pipeline_done = False

 
    if st.button("Run Pipeline"):
        with st.spinner(f"Running pipeline on {selected_file}..."):
            run_pipeline()
        st.success("Pipeline finished!")
        st.session_state.pipeline_done = True

    if st.session_state.pipeline_done:
        st.subheader("Choose Outputs to Display")

        show_artifacts = st.checkbox("Show Artifact Detection")
        show_cleaned = st.checkbox("Show Cleaned Signals")
        show_spikes = st.checkbox("Show Spike Plots")
        show_snr = st.checkbox("Show SNR Plots")
        show_features = st.checkbox("Show Feature Comparisons")

        if show_artifacts:
            st.subheader("Artifact Detection")
            art_dir = "output/cleaned_plots"
            if os.path.exists(art_dir):
                for f in sorted(os.listdir(art_dir)):
                    if f.endswith("_artifact_debug.png"):
                        st.image(os.path.join(art_dir, f), caption=f)
            cleaned_file = selected_file.replace("data/raw", "data/cleaned").replace(".csv", "_cleaned.csv")
            if os.path.exists(cleaned_file):
                with open(cleaned_file, "rb") as f:
                    st.download_button("Download Cleaned CSV", f, file_name=os.path.basename(cleaned_file))

    
        if show_cleaned:
            st.subheader("Cleaned Signals")
            clean_dir = "output/cleaned_plots"
            if os.path.exists(clean_dir):
                for f in sorted(os.listdir(clean_dir)):
                    if f.endswith("_CLEANED_SAMPLE.png"):
                        st.image(os.path.join(clean_dir, f), caption=f)

    
        if show_spikes:
            st.subheader("Spike Plots")
            spike_dir = "output/spike/info"
            if os.path.exists(spike_dir):
                for f in sorted(os.listdir(spike_dir)):
                    if f.endswith("_spikes.png"):
                        st.image(os.path.join(spike_dir, f), caption=f)
            spike_file = selected_file.replace("data/raw", "output/spike").replace(".csv", "_spikes.csv")
            if os.path.exists(spike_file):
                with open(spike_file, "rb") as f:
                    st.download_button("Download Spikes CSV", f, file_name=os.path.basename(spike_file))

    
        if show_snr:
            st.subheader("SNR Plots")
            snr_dir = "output/snr"
            if os.path.exists(snr_dir):
                for f in sorted(os.listdir(snr_dir)):
                    if f.endswith("_snr.png"):
                        st.image(os.path.join(snr_dir, f), caption=f)
            snr_file = "output/snr/snr_summary.csv"
            if os.path.exists(snr_file):
                with open(snr_file, "rb") as f:
                    st.download_button("Download SNR Summary", f, file_name="snr_summary.csv")

       
        if show_features:
            st.subheader("Feature Comparisons")
            features_file = "output/features/features_summary.csv"
            if os.path.exists(features_file):
                df = pd.read_csv(features_file)
                st.write("### Features Summary")
                st.dataframe(df.head(20))
                st.write("### Group Means")
                st.dataframe(df.groupby("group").mean(numeric_only=True))

                features = ["spike_count", "firing_rate", "isi_mean", "burst_count", "mean_spikes_per_burst"]
                cols = st.columns(2)
                for i, feat in enumerate(features):
                    plot_path = f"output/features/{feat}_barplot.png"
                    if os.path.exists(plot_path):
                        with cols[i % 2]:
                            st.image(plot_path, caption=f"{feat} – Healthy vs SMA")

                with open(features_file, "rb") as f:
                    st.download_button("Download Features CSV", f, file_name="features_summary.csv")
