# IslandEdge Decisions

## 2026-06-29 - MVP modeling strategy

Use a transparent weighted scoring model for the first MVP instead of XGBoost/PyTorch.

Reason: Season 8 is live and Season 7 provides only a small backtest set, so a heavily trained model would be easy to overfit and hard to explain. The scoring model lets Marcus inspect source contributions, learn feature weighting, and later swap in sklearn or XGBoost behind the same dashboard contract.

## 2026-06-29 - Data retention policy

Store only aggregated public-signal features for portfolio-facing outputs. Raw posts, comments, cookies, and scraped text are excluded from git via `.gitignore`.

Reason: the project should be public-presentable without exposing personal credentials, session cookies, or platform content.

## 2026-06-29 - Manual TikTok and personal-opinion forms

Manual forms count toward the day on which they are submitted. The local MVP stores entries in browser localStorage and recomputes projections immediately.

Reason: this keeps daily collection fast and avoids backend complexity while the product shape is being tested.

## 2026-06-29 - Season 8 seed priors

Season 8 live mode includes a hand-seeded active/Casa roster and gives Bryce and Trinity stronger prior momentum.

Reason: the dashboard is still using synthetic aggregate rows until Agent-Reach/social ingestion is connected, and the placeholder model should reflect obvious current-season favorites rather than imply the scraper has real live signal coverage.
