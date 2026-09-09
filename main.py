import os
import logging
import sys
import traceback
import pandas as pd

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO').upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('csv_cleaner')

def read_csv(file_path):
    logger.info(f"Reading CSV file: {file_path}")
    try:
        df = pd.read_csv(file_path, quotechar='"')
        logger.info(f"Successfully read CSV, total rows: {len(df)}")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to read CSV: {e}")
        logger.debug(traceback.format_exc())
        raise

def split_duplicates(df):
    logger.info("[INFO] Splitting duplicates")

    duplicates_mask=df.duplicated(subset=['ids'], keep='first')
    df_clean_raw=df[~duplicates_mask].reset_index(drop=True)
    df_reject_raw=df[duplicates_mask].reset_index(drop=True)

    logger.info(f"[INFO] Total rows in clean data: {len(df_clean_raw)}")
    logger.info(f"[INFO] Total rows in rejected data: {len(df_reject_raw)}")
    return df_clean_raw, df_reject_raw

