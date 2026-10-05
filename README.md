# Bike Share Ops

A portfolio project learning data engineering and dbt through bike-share demand, station availability, and rebalancing analysis.

**Status:** Milestone 1 — project definition and local setup. Ingestion, analytical models, CI, and business findings are planned; they are not implemented yet.

## Business problem

Help an operator identify stations with availability problems and prioritize limited rebalancing resources. Explore additional parking or docking capacity only where the available data supports a defensible conclusion.

## Local stack

Python → raw JSON/Parquet → DuckDB → dbt → analytical marts → dashboard.

The project will run without paid cloud services, trial accounts, or cloud credentials. Live collection depends on the local computer being available; observation gaps will be recorded.

## Start here

```sh
cd ~/dev/github/bike-share-ops
# With direnv installed and its shell hook enabled:
direnv allow
dbt debug
dbt parse
```

See [SETUP.md](SETUP.md) for setup and VS Code instructions, [the project charter](docs/PROJECT_CHARTER.md) for scope and acceptance criteria, and [the learning log](docs/LEARNING_LOG.md) for verified progress.

There are currently no models to build. The next milestone selects and profiles a bounded historical dataset before implementing the first transformation.
