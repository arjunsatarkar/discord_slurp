#!/usr/bin/env python3
import aiosqlite
import discord

import argparse
import json
import pathlib
import time
import tomllib

import parse

DISCORD_SLURP_VERSION = "0.2.0"

parser = argparse.ArgumentParser()
parser.add_argument("config_file")
args = parser.parse_args()

with open(args.config_file, "rb") as config_file:
    config = tomllib.load(config_file)

db_path = pathlib.Path(config["db_dir"]) / "discord_slurp.db"
token: str = config["token"]
max_reaction_users = getattr(config, "max_reaction_users", float("inf"))
if max_reaction_users < 0:
    max_reaction_users = float("inf")
record_types: dict[str, int]
record_version_id: int

client = discord.Client(intents=discord.Intents.all())


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    current_unix_second = int(time.time())
    data = await parse.parse_message(message, max_reaction_users)

    async with aiosqlite.connect(db_path) as con:
        await con.execute(
            "INSERT INTO records (type_id, data, fetched_at_unix_second, record_version_id) "
            "VALUES (?, ?, ?, ?);",
            (
                record_types["message"],
                json.dumps(data, allow_nan=False, separators=(",", ":")),
                current_unix_second,
                record_version_id,
            ),
        )
        await con.commit()


def init():
    import sqlite3

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    with open("setup.sql", "r") as setup_script_file:
        cur.executescript(setup_script_file.read())

    global record_types, record_version_id
    record_types = {
        type_name: type_id
        for type_id, type_name in cur.execute("SELECT * FROM record_types;").fetchall()
    }

    record_version = (
        f"discord_slurp {DISCORD_SLURP_VERSION}\ndiscord.py {discord.__version__}"
    )
    cur.execute(
        "INSERT OR IGNORE INTO record_versions (version) VALUES (?);",
        (record_version,),
    )
    record_version_id = cur.execute(
        "SELECT id FROM record_versions WHERE version = ?;", (record_version,)
    ).fetchone()[0]
    con.commit()

    client.run(token)


init()
