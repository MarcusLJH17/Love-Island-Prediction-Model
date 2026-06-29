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

The ingestion scaffolding is designed to call Agent-Reach CLI tools locally after authentication. Follow Agent-Reach's project instructions for installation and account/session setup. The MVP does not bypass platform auth, rate limits, or terms.
