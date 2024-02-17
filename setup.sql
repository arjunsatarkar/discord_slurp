CREATE TABLE
    IF NOT EXISTS archive_info (info_key TEXT PRIMARY KEY UNIQUE, info_value TEXT) STRICT;

INSERT
OR IGNORE INTO archive_info (info_key, info_value)
VALUES
    (
        "readme",
        "Archive of content from the Discord platform https://discord.com/. Created with Discord Slurp https://scm.arjunsatarkar.net/discord_slurp/"
    ),
    ("archive container version", "0.2.0");

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
        data TEXT CHECK (json_valid (data)),
        fetched_at_unix_second INTEGER,
        record_version_id INTEGER REFERENCES record_versions (id)
    ) STRICT;

CREATE INDEX IF NOT EXISTS idx_records__fetched_at_unix_second ON records (fetched_at_unix_second);

CREATE VIEW
    IF NOT EXISTS view_message_content (
        record_id,
        guild_id,
        channel_id,
        author_id,
        message_id,
        creation_unix_second,
        message_content
    ) AS
SELECT
    id,
    json_extract (data, "$.guild_id"),
    json_extract (data, "$.channel_id"),
    json_extract (data, "$.author_id"),
    json_extract (data, "$.id"),
    json_extract (data, "$.created_at"),
    json_extract (data, "$.content")
FROM
    records
WHERE
    type_id = 3;

CREATE VIRTUAL TABLE IF NOT EXISTS fts_message_content USING fts5 (
    guild_id UNINDEXED,
    channel_id UNINDEXED,
    author_id UNINDEXED,
    message_id UNINDEXED,
    creation_unix_second UNINDEXED,
    message_content,
    content = "view_message_content",
    content_rowid = "record_id",
    tokenize = unicode61
);

CREATE TRIGGER IF NOT EXISTS trig_after_insert_records AFTER INSERT ON records WHEN new.type_id = 3 BEGIN
INSERT INTO
    fts_message_content (rowid, message_content)
VALUES
    (new.id, json_extract (new.data, "$.content"));

END;