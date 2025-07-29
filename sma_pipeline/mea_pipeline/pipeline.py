from mea_pipeline.preProcessing import clean_signals
from mea_pipeline.spikes import detect_spikes
from mea_pipeline.snr import compute_snr
from mea_pipeline.features import extract_features  

def run_pipeline():
    clean_signals()
    detect_spikes()
    compute_snr()
    extract_features() 

