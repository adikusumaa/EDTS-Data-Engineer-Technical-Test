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

def transform_data(df):
    logger.info("[INFO] Transforming data")

    df_trans = df.copy()
    df_trans['dates']=pd.to_datetime(df_trans['dates'],format='%d/%m/%Y',errors='coerce').dt.strftime('%Y-%m-%d')
    df_trans['names']=df_trans['names'].str.upper()

    num_cols=['monthly_listeners', 'popularity', 'followers', 'num_releases', 'num_tracks']

    for col in num_cols:
        df_trans[col]=pd.to_numeric(df_trans[col],errors='coerce').fillna(0).astype(int)
    df_trans['genres']=df_trans['genres'].apply(
        lambda x: [genre.strip() for genre in str(x).split(',')]
    )   
    df_trans['feat_track_ids']=df_trans['feat_track_ids'].apply(
        lambda x: [track.strip() for track in str(x).split(',')]
    )
    df_trans['first_release']=df_trans['first_release'].astype(str).str.strip()
    df_trans['last_release']=df_trans['last_release'].astype(str).str.strip()

    logger.debug(f"[DEBUG] Transformed DataFrame:\n{df_trans.head()}")
    return df_trans
