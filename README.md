# IslandEdge

IslandEdge is a portfolio MVP for forecasting Love Island USA outcomes with a mix of public social signals, Google Trends-style demand, show-state features, TikTok observations, and personal episode notes.

The MVP is intentionally transparent: it starts with an interpretable weighted scoring model instead of a black-box classifier. That makes it easier to learn what each signal is doing, inspect ablations, and later replace the scorer with sklearn/XGBoost once more labeled history exists.

## What Is Built

- Current-season dashboard for Love Island USA Season 8.
- Historical backtest tab for Season 7.
- Draggable timeline cursor that drives contestant cards.
- Smooth scrubber control under the chart for finer cursor movement.
- Monte Carlo-style projection fan after the cursor.
- Source toggles for Reddit, Twitter/X, Google Trends, TikTok, episode data, and personal notes.
- Two local forms:
  - TikTok observation form.
  - Post-episode personal-opinion form.
- Python scaffolding for future Agent-Reach ingestion and aggregate-feature storage.

## Run Locally

```bash
npm install
npm run dev
```

Open the local URL printed by Next.js, usually `http://localhost:3000`.

## Data Sources

Seed contestant and outcome data comes from:

- Season 8 page: https://loveisland.fandom.com/wiki/Love_Island_USA_(Season_8)
- Season 7 page: https://loveisland.fandom.com/wiki/Love_Island_USA_(Season_7)

Fandom content is community-maintained and should be rechecked as Season 8 changes.

## Privacy And Portfolio Policy

The public repo should store aggregate feature rows and model outputs only. Do not commit:

- Raw scraped posts or comments.
- Twitter/X or Reddit cookies.
- API keys.
- Personal session data.

## Islander Images

Drop preview photos into `public/islanders` using lowercase first-name filenames such as `bryce.jpg` or `trinity.jpg`. Missing images fall back to initial avatars.

## Agent-Reach Notes

The ingestion scaffolding is designed to call Agent-Reach CLI tools locally after authentication. The MVP does not bypass platform auth, rate limits, or terms.

### Future Agent-Reach Setup

1. Install Agent-Reach using its official project instructions.
2. Log in locally to the platforms you want to collect from, starting with Reddit and Twitter/X.
3. Confirm the Agent-Reach commands work outside this app by running a tiny test search.
4. Create `.env.local` from your local settings and set:

```bash
ISLANDEDGE_SEASON=8
ISLANDEDGE_DB=data/islandedge.sqlite
AGENT_REACH_TIMEOUT_SECONDS=60
```

5. Preview the exact daily queries before collecting:

```bash
python scripts/collect_daily.py --day 28 --date 2026-06-29 --source all --dry-run
```

6. Collect the day once the queries look right:

```bash
python scripts/collect_daily.py --day 28 --date 2026-06-29 --source all
```

7. Build model features and prediction rows:

```bash
python scripts/build_features.py --day 28 --date 2026-06-29
```

8. Export frontend-ready prediction JSON:

```bash
python scripts/export_predictions.py
```

Or run the full daily local pipeline in one command:

```bash
python scripts/run_daily_pipeline.py --day 28 --date 2026-06-29
```

Use `--skip-scrape` to rebuild from existing local data after editing show priors or adding manual notes:

```bash
python scripts/run_daily_pipeline.py --day 28 --date 2026-06-29 --skip-scrape
```

9. Run the app and refresh the Season 8 tab:

```bash
npm run dev
```

Raw scraped posts stay in the local SQLite database only. Commit aggregate exports only when they are safe for the portfolio repo.
