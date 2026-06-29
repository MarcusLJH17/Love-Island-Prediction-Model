from islandedge.config import load_settings
from islandedge.storage import initialize


if __name__ == "__main__":
    settings = load_settings()
    initialize(settings.database_path)
    print(f"Initialized {settings.database_path}")
