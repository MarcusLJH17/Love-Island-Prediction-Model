from __future__ import annotations

import sqlite3
import json
from pathlib import Path
from typing import Iterable, Sequence

from islandedge.contestants import Contestant


SCHEMA = """
CREATE TABLE IF NOT EXISTS contestants (
  id TEXT PRIMARY KEY,
  season INTEGER NOT NULL,
  display_name TEXT NOT NULL,
  full_name TEXT NOT NULL,
  gender TEXT NOT NULL,
  entered_day INTEGER NOT NULL,
  exit_day INTEGER,
  aliases_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_social_posts (
  id TEXT PRIMARY KEY,
  season INTEGER NOT NULL,
  source TEXT NOT NULL,
  source_id TEXT NOT NULL,
  source_url TEXT,
  author TEXT,
  text TEXT NOT NULL,
  posted_at TEXT NOT NULL,
  collected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  query TEXT,
  subreddit TEXT,
  engagement REAL NOT NULL DEFAULT 0,
  UNIQUE(source, source_id)
);

CREATE TABLE IF NOT EXISTS contestant_mentions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  raw_post_id TEXT NOT NULL,
  season INTEGER NOT NULL,
  contestant_id TEXT NOT NULL,
  alias TEXT NOT NULL,
  confidence REAL NOT NULL,
  sentiment REAL NOT NULL,
  context_terms TEXT NOT NULL,
  posted_date TEXT NOT NULL,
  source TEXT NOT NULL,
  engagement REAL NOT NULL DEFAULT 0,
  FOREIGN KEY(raw_post_id) REFERENCES raw_social_posts(id)
);

CREATE TABLE IF NOT EXISTS daily_source_metrics (
  season INTEGER NOT NULL,
  contestant_id TEXT NOT NULL,
  feature_date TEXT NOT NULL,
  source TEXT NOT NULL,
  mention_volume INTEGER NOT NULL DEFAULT 0,
  sentiment_mean REAL NOT NULL DEFAULT 0,
  engagement_weighted_sentiment REAL NOT NULL DEFAULT 0,
  engagement_total REAL NOT NULL DEFAULT 0,
  source_available INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (season, contestant_id, feature_date, source)
);

CREATE TABLE IF NOT EXISTS daily_model_features (
  season INTEGER NOT NULL,
  contestant_id TEXT NOT NULL,
  feature_date TEXT NOT NULL,
  day INTEGER NOT NULL,
  reddit_score REAL,
  twitter_score REAL,
  trends_score REAL,
  tiktok_score REAL,
  episode_score REAL,
  personal_score REAL,
  social_3d_score REAL NOT NULL DEFAULT 0,
  social_7d_score REAL NOT NULL DEFAULT 0,
  source_availability_json TEXT NOT NULL,
  PRIMARY KEY (season, contestant_id, feature_date)
);

CREATE TABLE IF NOT EXISTS predictions (
  season INTEGER NOT NULL,
  contestant_id TEXT NOT NULL,
  feature_date TEXT NOT NULL,
  day INTEGER NOT NULL,
  score REAL NOT NULL,
  probability REAL NOT NULL,
  source_breakdown_json TEXT NOT NULL,
  source_availability_json TEXT NOT NULL,
  PRIMARY KEY (season, contestant_id, feature_date)
);

CREATE TABLE IF NOT EXISTS manual_tiktok_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  feature_date TEXT NOT NULL,
  contestant_id TEXT NOT NULL,
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
  contestant_id TEXT NOT NULL,
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


def upsert_contestants(database_path: Path, season: int, contestants: Sequence[Contestant]) -> None:
    initialize(database_path)
    with connect(database_path) as connection:
        connection.executemany(
            """
            INSERT INTO contestants (
              id, season, display_name, full_name, gender, entered_day, exit_day, aliases_json
            )
            VALUES (:id, :season, :display_name, :full_name, :gender, :entered_day, :exit_day, :aliases_json)
            ON CONFLICT(id) DO UPDATE SET
              season = excluded.season,
              display_name = excluded.display_name,
              full_name = excluded.full_name,
              gender = excluded.gender,
              entered_day = excluded.entered_day,
              exit_day = excluded.exit_day,
              aliases_json = excluded.aliases_json
            """,
            [
                {
                    "id": contestant.id,
                    "season": season,
                    "display_name": contestant.display_name,
                    "full_name": contestant.full_name,
                    "gender": contestant.gender,
                    "entered_day": contestant.entered_day,
                    "exit_day": contestant.exit_day,
                    "aliases_json": json.dumps(contestant.aliases),
                }
                for contestant in contestants
            ],
        )


def insert_raw_posts(database_path: Path, rows: Iterable[dict]) -> None:
    initialize(database_path)
    with connect(database_path) as connection:
        connection.executemany(
            """
            INSERT OR IGNORE INTO raw_social_posts (
              id, season, source, source_id, source_url, author, text,
              posted_at, query, subreddit, engagement
            )
            VALUES (
              :id, :season, :source, :source_id, :source_url, :author, :text,
              :posted_at, :query, :subreddit, :engagement
            )
            """,
            list(rows),
        )


def insert_mentions(database_path: Path, rows: Iterable[dict]) -> None:
    initialize(database_path)
    with connect(database_path) as connection:
        connection.executemany(
            """
            INSERT INTO contestant_mentions (
              raw_post_id, season, contestant_id, alias, confidence,
              sentiment, context_terms, posted_date, source, engagement
            )
            VALUES (
              :raw_post_id, :season, :contestant_id, :alias, :confidence,
              :sentiment, :context_terms, :posted_date, :source, :engagement
            )
            """,
            list(rows),
        )


def insert_manual_tiktok_entry(database_path: Path, row: dict) -> None:
    initialize(database_path)
    with connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO manual_tiktok_entries (
              feature_date, contestant_id, positive_sentiment,
              visible_edit_volume, comment_tone, viral_momentum, notes
            )
            VALUES (
              :feature_date, :contestant_id, :positive_sentiment,
              :visible_edit_volume, :comment_tone, :viral_momentum, :notes
            )
            """,
            row,
        )


def insert_manual_episode_entry(database_path: Path, row: dict) -> None:
    initialize(database_path)
    with connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO manual_episode_entries (
              feature_date, contestant_id, episode_enjoyment,
              got_good_edit, relationship_strength, risk_of_dumping, notes
            )
            VALUES (
              :feature_date, :contestant_id, :episode_enjoyment,
              :got_good_edit, :relationship_strength, :risk_of_dumping, :notes
            )
            """,
            row,
        )


def delete_mentions_for_posts(database_path: Path, raw_post_ids: Iterable[str]) -> int:
    initialize(database_path)
    ids = list(dict.fromkeys(raw_post_ids))
    if not ids:
        return 0
    placeholders = ",".join("?" for _ in ids)
    with connect(database_path) as connection:
        cursor = connection.execute(
            f"DELETE FROM contestant_mentions WHERE raw_post_id IN ({placeholders})",
            ids,
        )
        return cursor.rowcount


def replace_daily_source_metrics(database_path: Path, rows: Iterable[dict]) -> None:
    initialize(database_path)
    rows = list(rows)
    with connect(database_path) as connection:
        connection.executemany(
            """
            INSERT INTO daily_source_metrics (
              season, contestant_id, feature_date, source, mention_volume,
              sentiment_mean, engagement_weighted_sentiment, engagement_total, source_available
            )
            VALUES (
              :season, :contestant_id, :feature_date, :source, :mention_volume,
              :sentiment_mean, :engagement_weighted_sentiment, :engagement_total, :source_available
            )
            ON CONFLICT(season, contestant_id, feature_date, source) DO UPDATE SET
              mention_volume = excluded.mention_volume,
              sentiment_mean = excluded.sentiment_mean,
              engagement_weighted_sentiment = excluded.engagement_weighted_sentiment,
              engagement_total = excluded.engagement_total,
              source_available = excluded.source_available
            """,
            rows,
        )


def replace_model_features(database_path: Path, rows: Iterable[dict]) -> None:
    initialize(database_path)
    rows = list(rows)
    with connect(database_path) as connection:
        for season, feature_date in sorted({(row["season"], row["feature_date"]) for row in rows}):
            connection.execute(
                "DELETE FROM daily_model_features WHERE season = ? AND feature_date = ?",
                (season, feature_date),
            )
        connection.executemany(
            """
            INSERT INTO daily_model_features (
              season, contestant_id, feature_date, day, reddit_score, twitter_score,
              trends_score, tiktok_score, episode_score, personal_score,
              social_3d_score, social_7d_score, source_availability_json
            )
            VALUES (
              :season, :contestant_id, :feature_date, :day, :reddit_score, :twitter_score,
              :trends_score, :tiktok_score, :episode_score, :personal_score,
              :social_3d_score, :social_7d_score, :source_availability_json
            )
            ON CONFLICT(season, contestant_id, feature_date) DO UPDATE SET
              day = excluded.day,
              reddit_score = excluded.reddit_score,
              twitter_score = excluded.twitter_score,
              trends_score = excluded.trends_score,
              tiktok_score = excluded.tiktok_score,
              episode_score = excluded.episode_score,
              personal_score = excluded.personal_score,
              social_3d_score = excluded.social_3d_score,
              social_7d_score = excluded.social_7d_score,
              source_availability_json = excluded.source_availability_json
            """,
            rows,
        )


def replace_predictions(database_path: Path, rows: Iterable[dict]) -> None:
    initialize(database_path)
    rows = list(rows)
    with connect(database_path) as connection:
        for season, feature_date in sorted({(row["season"], row["feature_date"]) for row in rows}):
            connection.execute(
                "DELETE FROM predictions WHERE season = ? AND feature_date = ?",
                (season, feature_date),
            )
        connection.executemany(
            """
            INSERT INTO predictions (
              season, contestant_id, feature_date, day, score, probability,
              source_breakdown_json, source_availability_json
            )
            VALUES (
              :season, :contestant_id, :feature_date, :day, :score, :probability,
              :source_breakdown_json, :source_availability_json
            )
            ON CONFLICT(season, contestant_id, feature_date) DO UPDATE SET
              day = excluded.day,
              score = excluded.score,
              probability = excluded.probability,
              source_breakdown_json = excluded.source_breakdown_json,
              source_availability_json = excluded.source_availability_json
            """,
            rows,
        )


def fetch_all(database_path: Path, query: str, params: Sequence[object] = ()) -> list[sqlite3.Row]:
    initialize(database_path)
    with connect(database_path) as connection:
        return list(connection.execute(query, params))
