# Learning log

Record completed work and evidence here. Planned work belongs in the charter.

## 2026-10-05 — Milestone 1 preparation

- Defined the bike-share operations problem, local stack, and project milestones.
- Distinguished completed trip demand from unmet demand and observed station availability.
- Made station-placement clustering conditional on suitable public location data.
- Added VS Code interpreter settings and extension recommendations.

Verification:

- Renamed the local folder and GitHub repository to `bike-share-ops`, preserving Git history.
- Updated dbt identifiers to `bike_share_ops`, package metadata, documentation, and Git origin.
- Repaired environment launchers after the move and reinstalled the local editable project without upgrading dbt dependencies.
- `dbt debug`: all checks passed, including the DuckDB connection.
- `dbt --no-partial-parse parse`: passed in the renamed folder.
- Re-authorized the project `.envrc` at its new path.

No analytical models or business findings exist yet; these checks validate setup only.

## Next learning task

Read the charter and explain, in your own words:

1. What decision will the project help an operator make?
2. What is the difference between Python ingestion and dbt transformation?
3. Why cannot completed trips alone measure unmet demand?

Then inspect a small historical trip file together and define the grain of its raw table before building a model.
