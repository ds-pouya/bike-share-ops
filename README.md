# Bike Share Ops

I am building this project to learn dbt and develop my data engineering skills through a practical bike-share operations problem.

The goal is to understand demand across hours, weekdays, and seasons, identify stations with availability problems, and evaluate where limited rebalancing resources could help.

## Project status

**Milestone 1 completed:** repository setup, project scope, and local dbt/DuckDB configuration. The DuckDB connection and dbt project parsing have been verified.

**Milestone 2 in progress:** the January 2025 NYC trip archive has been downloaded and profiled locally: 2,124,475 records across three CSV files. See [source details and initial observations](docs/DATA_SOURCE.md).

**Next:** define raw-table types and inclusion rules, load DuckDB, and build the first dbt staging model. The persistent raw load, analytical models, CI, and business findings are not implemented yet.

## Business questions

- When and where do riders start and finish trips?
- Which stations frequently have no bikes or available docks during observed periods?
- How does demand vary with weather?
- Can a rebalancing policy improve availability compared with a simple baseline?
- If suitable location data is available, where might additional parking or docking capacity be useful?

Completed trips show observed usage. They do not capture trips that never started because no bike was available. Availability analysis will use station observations and report gaps in coverage.

## Planned stack

Python → raw JSON/Parquet → DuckDB → dbt staging and intermediate models → analytical marts → dashboard.

Python will collect data and load raw tables. DuckDB will store the data. dbt will execute SQL transformations in DuckDB, test the results, and document dependencies.

The core project will run locally without paid cloud services, trial accounts, or cloud credentials. Live collection will depend on the local computer being available.

## Local setup

```sh
cd ~/dev/github/bike-share-ops
# With direnv installed and its shell hook enabled:
direnv allow
dbt debug
dbt parse
```

[Setup instructions](SETUP.md) cover the environment and VS Code configuration. The [project charter](docs/PROJECT_CHARTER.md) describes the planned scope, architecture, and completion criteria.
