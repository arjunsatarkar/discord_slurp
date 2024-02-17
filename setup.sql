CREATE TABLE
    IF NOT EXISTS archive_info (info_key TEXT PRIMARY KEY UNIQUE, info_value TEXT) STRICT;

INSERT
OR IGNORE INTO archive_info (info_key, info_value)
VALUES
    (
        "readme",
        "Archive of content from the Discord platform https://discord.com/. Created with Discord Slurp https://scm.arjunsatarkar.net/discord_slurp/"
    ),
    ("archive container version", "0.1.0");

CREATE TABLE
    IF NOT EXISTS record_versions (id INTEGER PRIMARY KEY, version TEXT UNIQUE) STRICT;

CREATE TABLE
    IF NOT EXISTS record_types (id INTEGER PRIMARY KEY, name TEXT) STRICT;

INSERT
OR IGNORE INTO record_types (id, name)
VALUES
    (0, "revisit"),
    (1, "guild"),
    (2, "channel"), -- Includes threads
    (3, "message"),
    (4, "member");

CREATE TABLE
    IF NOT EXISTS records (
        id INTEGER PRIMARY KEY, -- A row ID, *not* the discord snowflake
        type_id INTEGER REFERENCES record_types (id),
        data TEXT,
        fetched_at_unix_second INTEGER,
        record_version_id INTEGER REFERENCES record_versions (id)
    ) STRICT;