# IslandEdge

IslandEdge is a portfolio MVP for forecasting Love Island USA outcomes with a mix of public social signals, Google Trends-style demand, show-state features, TikTok observations, and personal episode notes.

The MVP is intentionally transparent: it starts with an interpretable weighted scoring model instead of a black-box classifier. That makes it easier to learn what each signal is doing, inspect ablations, and later replace the scorer with sklearn/XGBoost once more labeled history exists.

Season 8 is now finalized in the app: Bryce and Trinity won, Aniya and Carl finished second, Melanie and Sincere finished third, and Kayda and Zach finished fourth. The Season 8 tab preserves the prediction history and locks the finale point to the actual result.

## What Is Built

- Current-season dashboard for Love Island USA Season 8.
- Historical backtest tab for Season 7.
- Draggable timeline cursor that drives contestant cards.
- Smooth scrubber control under the chart for finer cursor movement.
- Monte Carlo-style projection fan after the cursor.
- Source toggles for Reddit, Twitter/X, Google Trends, TikTok, episode data, and personal notes.
- Source-attributed show recap events that can be toggled separately from personal notes.
- Two local forms:
  - TikTok observation form.
  - Post-episode personal-opinion form.
- Python scaffolding for future Agent-Reach ingestion and aggregate-feature storage.

## How The Model Works

IslandEdge currently uses an interpretable weighted scoring model, not a black-box machine learning model. For each active contestant, it combines public social sentiment, recent momentum, Google Trends demand, sourced show recap events, optional TikTok/manual notes, and basic show structure into one strength score. The app then converts all active contestants' scores into percentages that add up to 100%.

Current score formula:

```text
score =
  0.24 * blended_social
+ 0.16 * social_3_day
+ 0.06 * social_7_day
+ 0.08 * google_trends
+ 0.64 * show_recap
+ 0.10 * tiktok_input
+ 0.10 * episode_input
+ 0.10 * personal_input
+ 0.18 * structure
```

`blended_social` averages today's Reddit/Twitter signal with 3-day social momentum. Reddit and Twitter/X use sentiment, mention volume, and engagement. Google Trends is upside-only, so sparse search data can help but does not punish a contestant. Missing TikTok or personal entries are ignored rather than treated as negative.

Percentages are produced with a softmax:

```text
raw_i = e ^ (4.6 * score_i)
probability_i = raw_i / sum(raw_for_all_active_contestants)
```

The UI displays a 1% minimum for readability, but the exported model probability can still be below 1%. If the model weights, inputs, or probability conversion change, update this section in the same change.

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
python scripts/run_daily_pipeline.py --date 2026-07-01
```

That command collects Reddit, Twitter/X, and Google Trends, then rebuilds features and exports frontend JSON. Use `--skip-trends` if Google Trends is rate-limited and you want the social scrape to continue.

Use `--skip-scrape` to rebuild from existing local data after editing show priors or adding manual notes:

```bash
python scripts/run_daily_pipeline.py --date 2026-07-01 --skip-scrape
```

The pipeline can infer the Love Island season day from the date, using Season 8's June 2, 2026 start date. For a just-after-midnight end-of-day scrape, use yesterday's date automatically:

```bash
python scripts/run_daily_pipeline.py --target-date yesterday
```

Season 8's finale date is configured as July 12, 2026. The daily pipeline runs through that finale date, then exits without scraping for later dates unless `--force-after-finale` is passed.

After the finale, `scripts/finalize_season8.py` writes the actual final placements into the local prediction store before exporting frontend JSON.

9. Run the app and refresh the Season 8 tab:

```bash
npm run dev
```

Raw scraped posts stay in the local SQLite database only. Commit aggregate exports only when they are safe for the portfolio repo.

### Show Recap Events

Show-state context comes from `data/config/recap_events.season8.json`. Each row cites a public recap URL and a short event sentence. The pipeline scores those event sentences for sentiment and applies them as the `show` source.

This replaces manual contestant priors. If the `Show Recaps` toggle is off, recap-event effects are removed from exported probabilities in the frontend.

### Daily Automation On Windows

Install the local scheduled task:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_daily_task.ps1
```

This creates a Windows Task Scheduler job named `IslandEdge Daily Update` that runs at 12:05 AM every day. It scrapes Reddit and Twitter/X plus Google Trends for the previous calendar day, rebuilds features, and exports the frontend JSON. Logs are written locally to `data/logs/` and are ignored by git.

The automation updates your local app data. It does not auto-commit or auto-push by default, so personal notes, scraped raw text, and credentials stay local unless you intentionally publish aggregate outputs.
