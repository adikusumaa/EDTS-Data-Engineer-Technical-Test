import os
import sys
import json
import tempfile
import shutil
from datetime import datetime

import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import main


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'dates': ['01/04/2024', '01/04/2024', '01/04/2024'],
        'ids': ['id1', 'id2', 'id2'],
        'names': ['Artist One', 'Artist Two', 'artist two'],
        'monthly_listeners': ['100', '200', '200'],
        'popularity': ['10', '20', '20'],
        'followers': ['1000', '2000', '2000'],
        'genres': ['rock, pop', 'indie', 'indie'],
        'first_release': ['2010', '2015', '2015'],
        'last_release': ['2020', '2022', '2022'],
        'num_releases': ['1', '2', '2'],
        'num_tracks': ['5', '6', '6'],
        'playlists_found': ['Playlist A', 'Playlist B', 'Playlist B'],
        'feat_track_ids': ['tr1, tr2', 'tr3', 'tr3']
    })


@pytest.fixture
def temp_target_dir(tmp_path):
    old_target = main.TARGET_DIR
    main.TARGET_DIR = str(tmp_path)
    yield str(tmp_path)
    main.TARGET_DIR = old_target


def test_read_csv():
    df = main.read_csv('/app/example/scrap.csv')
    assert len(df) == 3
    assert 'genres' in df.columns
    assert df.iloc[0]['genres'] == 'alternative metal, alternative rock, blues rock, grunge, supergroup'


def test_split_duplicates(sample_df):
    clean, reject = main.split_duplicates(sample_df)
    assert len(clean) == 2
    assert len(reject) == 1
    assert clean['ids'].tolist() == ['id1', 'id2']
    assert reject['ids'].tolist() == ['id2']


def test_transform_data(sample_df):
    transformed = main.transform_data(sample_df.iloc[[0]])
    row = transformed.iloc[0]
    assert row['dates'] == '2024-04-01'
    assert row['names'] == 'ARTIST ONE'
    assert row['monthly_listeners'] == 100
    assert row['popularity'] == 10
    assert row['followers'] == 1000
    assert row['genres'] == ['rock', 'pop']
    assert row['feat_track_ids'] == ['tr1', 'tr2']
    assert row['first_release'] == '2010'
    assert row['last_release'] == '2020'
    assert row['num_releases'] == 1
    assert row['num_tracks'] == 5


def test_list_to_pg_array():
    assert main.list_to_pg_array(['rock', 'pop']) == '{"rock","pop"}'
    assert main.list_to_pg_array([]) == '{}'


def test_prep_df_db(sample_df):
    transformed = main.transform_data(sample_df.iloc[[0]])
    db_ready = main.prep_df_db(transformed)
    assert db_ready.iloc[0]['genres'] == '{"rock","pop"}'
    assert db_ready.iloc[0]['feat_track_ids'] == '{"tr1","tr2"}'


def test_export_clean_to_json(sample_df, temp_target_dir):
    transformed = main.transform_data(sample_df.iloc[:2])
    timestamp = '20240302101010'
    output_path = main.export_clean_to_json(transformed, timestamp)
    assert os.path.exists(output_path)
    with open(output_path, 'r') as f:
        data = json.load(f)
    assert data['row_count'] == 2
    assert len(data['data']) == 2
    assert data['data'][0]['names'] == 'ARTIST ONE'
    assert isinstance(data['data'][0]['genres'], list)
    assert data['data'][0]['dates'] == '2024-04-01'


def test_export_reject_to_csv(sample_df, temp_target_dir):
    _, reject = main.split_duplicates(sample_df)
    timestamp = '20240302101010'
    output_path = main.export_reject_to_csv(reject, timestamp)
    assert os.path.exists(output_path)
    df_csv = pd.read_csv(output_path)
    assert len(df_csv) == 1
    assert df_csv.iloc[0]['ids'] == 'id2'
    assert df_csv.iloc[0]['names'] == 'artist two'
    assert df_csv.iloc[0]['dates'] == '01/04/2024'