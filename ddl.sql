CREATE TABLE IF NOT EXISTS data (
    dates DATE,
    ids VARCHAR,
    names VARCHAR,
    monthly_listeners INTEGER,
    popularity INTEGER,
    followers INTEGER,
    genres TEXT[],
    first_release VARCHAR(4),
    last_release VARCHAR(4),
    num_releases INTEGER,
    num_tracks INTEGER,
    playlists_found VARCHAR,
    feat_track_ids TEXT[]
);

CREATE TABLE IF NOT EXISTS data_reject (
    dates DATE,
    ids VARCHAR,
    names VARCHAR,
    monthly_listeners INTEGER,
    popularity INTEGER,
    followers INTEGER,
    genres TEXT[],
    first_release VARCHAR(4),
    last_release VARCHAR(4),
    num_releases INTEGER,
    num_tracks INTEGER,
    playlists_found VARCHAR,
    feat_track_ids TEXT[]
);
