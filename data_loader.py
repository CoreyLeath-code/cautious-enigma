# data_loader.py

import pandas as pd
import logging
from config import LOG_DATA_PATH, LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL)

def load_log_data(path=LOG_DATA_PATH):
    try:
        df = pd.read_csv(path)
        logging.info(f"Loaded data from {path} with shape {df.shape}")
        return df
    except Exception as e:
        logging.error(f"Failed to load data: {e}")
        return pd.DataFrame()

def preprocess_logs(df):
    # Example preprocessing: drop nulls, convert timestamps
    if df.empty:
        logging.warning("Empty DataFrame received for preprocessing.")
        return df

    df = df.dropna().copy()
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    logging.info("Preprocessing complete.")
    return df
