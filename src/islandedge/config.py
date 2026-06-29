from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    database_path: Path
    season: int
    agent_reach_timeout_seconds: int


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        database_path=Path(os.getenv("ISLANDEDGE_DB", "data/islandedge.sqlite")),
        season=int(os.getenv("ISLANDEDGE_SEASON", "8")),
        agent_reach_timeout_seconds=int(os.getenv("AGENT_REACH_TIMEOUT_SECONDS", "60")),
    )
