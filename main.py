import os
import logging
import sys
import traceback
import pandas as pd

import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

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
    logger.info("Splitting duplicates")

    duplicates_mask=df.duplicated(subset=['ids'], keep='first')
    df_clean_raw=df[~duplicates_mask].reset_index(drop=True)
    df_reject_raw=df[duplicates_mask].reset_index(drop=True)

    logger.info(f"Total rows in clean data: {len(df_clean_raw)}")
    logger.info(f"Total rows in rejected data: {len(df_reject_raw)}")
    return df_clean_raw, df_reject_raw

def transform_data(df):
    logger.info("Transforming data")

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

    logger.debug(f"Transformed DataFrame:\n{df_trans.head()}")
    return df_trans

def list_to_pg_array(lst):
    if not lst:
        return '{}'
    escaped_items = [f'"{item}"' for item in lst]
    return '{' + ','.join(escaped_items) + '}'

def prep_df_db(df):
    logger.info("Preparing DataFrame for database insertion")

    df_db=df.copy()
    df_db['genres']=df_db['genres'].apply(list_to_pg_array)
    df_db['feat_track_ids']=df_db['feat_track_ids'].apply(list_to_pg_array)

    logger.debug(f"Prepared DataFrame for DB:\n{df_db.head()}")
    return df_db

def get_db_connection():
    logger.info("Opening database connection")

    try:
        conn=psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres'),
            dbname=os.getenv('DB_NAME', 'mydb')
        )

        logger.info("Database connection successful")
        return conn
    
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {e}")
        logger.debug(traceback.format_exc())
        raise

def create_tables(conn):
    ddl_path=os.path.join(os.path.dirname(__file__), 'ddl.sql')

    logger.info(f"Executing DDL from {ddl_path}")

    try:
        with open(ddl_path, 'r') as f:
            ddl_script = f.read()
        with conn.cursor() as cur:
            cur.execute(ddl_script)
        conn.commit()

        logger.info("Tables created or already exist")

    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        logger.debug(traceback.format_exc())
        raise

def insert_dataframe(conn, df, table_name):
    if df.empty:
        logger.warning(f"DataFrame is empty, no data inserted into {table_name}")
        return

    columns = [
        'dates', 'ids', 'names', 'monthly_listeners', 'popularity',
        'followers', 'genres', 'first_release', 'last_release',
        'num_releases', 'num_tracks', 'playlists_found', 'feat_track_ids'
    ]
    df_to_insert = df[columns]
    records = [tuple(row) for row in df_to_insert.to_numpy()]
    insert_query = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
        sql.Identifier(table_name),
        sql.SQL(', ').join(map(sql.Identifier, columns))
    )

    logger.info(f"Inserting {len(records)} rows into table {table_name}")

    try:
        with conn.cursor() as cur:
            execute_values(cur, insert_query, records)
        conn.commit()

        logger.info(f"Successfully inserted {len(records)} rows into {table_name}")
        
    except Exception as e:
        logger.error(f"Failed to insert into {table_name}: {e}")
        logger.debug(traceback.format_exc())
        raise
