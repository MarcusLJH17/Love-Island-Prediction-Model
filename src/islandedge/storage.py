import sqlite3
from pathlib import Path
from typing import Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS aggregate_features (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  season INTEGER NOT NULL,
  contestant_name TEXT NOT NULL,
  feature_date TEXT NOT NULL,
  source TEXT NOT NULL,
  mention_volume INTEGER NOT NULL DEFAULT 0,
  sentiment_mean REAL NOT NULL DEFAULT 0,
  sentiment_delta REAL NOT NULL DEFAULT 0,
  trend_score REAL NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS manual_tiktok_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  feature_date TEXT NOT NULL,
  contestant_name TEXT NOT NULL,
  positive_sentiment INTEGER NOT NULL,
  visible_edit_volume INTEGER NOT NULL,
  comment_tone INTEGER NOT NULL,
  viral_momentum INTEGER NOT NULL,
  notes TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS manual_episode_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  feature_date TEXT NOT NULL,
  contestant_name TEXT NOT NULL,
  episode_enjoyment INTEGER NOT NULL,
  got_good_edit INTEGER NOT NULL,
  relationship_strength INTEGER NOT NULL,
  risk_of_dumping INTEGER NOT NULL,
  notes TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def connect(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize(database_path: Path) -> None:
    with connect(database_path) as connection:
        connection.executescript(SCHEMA)


def upsert_aggregate_rows(database_path: Path, rows: Iterable[dict]) -> None:
    initialize(database_path)
    with connect(database_path) as connection:
        connection.executemany(
            """
            INSERT INTO aggregate_features (
              season, contestant_name, feature_date, source,
              mention_volume, sentiment_mean, sentiment_delta, trend_score
            )
            VALUES (
              :season, :contestant_name, :feature_date, :source,
              :mention_volume, :sentiment_mean, :sentiment_delta, :trend_score
            )
            """,
            list(rows),
        )
