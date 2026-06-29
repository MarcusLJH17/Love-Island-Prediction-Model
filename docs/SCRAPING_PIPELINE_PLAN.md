# IslandEdge Scraping Pipeline Plan

See `outputs/IslandEdge_Scraping_Pipeline_Plan.md` in the Codex workspace for the handoff version of this plan. This repo copy exists so the implementation rationale travels with the code.

## Implementation Slice

1. Expand SQLite schema around daily contestant/source metrics.
2. Add contestant aliases and Love Island context filtering.
3. Add Reddit collection wrapper for `r/LoveIslandUSA`.
4. Add Twitter/X Agent-Reach query builder that searches names and context, not just hashtags.
5. Store raw posts locally, extract contestant mention rows, aggregate daily metrics.
6. Treat missing TikTok/personal entries as unknown/neutral.
7. Export frontend-ready daily predictions JSON.
8. Have the dashboard use exported predictions when present, seeded values as fallback.

