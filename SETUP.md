# Local setup

This project uses Python 3.13 or later, dbt, and DuckDB. The Python packages are isolated in `.venv`; the local database is stored at `data/analytics.duckdb`.

## Fresh checkout

From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
mkdir -p data
export DBT_PROFILES_DIR="$PWD/.dbt"
dbt debug
dbt parse
```

`dbt debug` validates configuration and tests the DuckDB connection. `dbt parse` validates project files without executing models. There are no analytical models yet; `dbt build` will become the normal workflow after models and tests are added.

## Existing local environment

```sh
cd ~/dev/github/bike-share-ops
source .venv/bin/activate
export DBT_PROFILES_DIR="$PWD/.dbt"
dbt debug
dbt parse
```

The included `.envrc` provides the same activation and profile configuration through direnv, when installed with its shell hook enabled. `direnv allow` authorizes the file for the current location. A modified `.envrc` needs to be authorized again.

## VS Code

The repository includes workspace settings for `.venv/bin/python` and `DBT_PROFILES_DIR`. New integrated terminals receive the local profile path. If VS Code retains an interpreter from a previous folder location, **Python: Select Interpreter** selects the current `.venv/bin/python`.

Recommended extensions:

- [Python by Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-python.python).
- [YAML by Red Hat](https://marketplace.visualstudio.com/itemdetails?itemName=redhat.vscode-yaml).

No dbt extension or cloud account is required. Python environments contain absolute paths; moving a checkout requires repairing or recreating its environment and reopening terminals.

## Project layout

| Path | Purpose |
| --- | --- |
| `.dbt/profiles.yml` | Local DuckDB connection configuration |
| `dbt_project.yml` | dbt project configuration |
| `models/staging/` | Planned source cleanup models |
| `models/marts/` | Planned business-facing models |
| `seeds/` | Small CSV reference data |
| `tests/` | Custom dbt data tests |
| `data/analytics.duckdb` | Generated local database; ignored by Git |
| `target/` | Generated dbt artifacts; ignored by Git |

The profile name in `.dbt/profiles.yml` matches `profile: bike_share_ops` in `dbt_project.yml`. DuckDB creates the database file when it connects.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `dbt` command unavailable | The current `.venv` is activated. |
| Profile not found | `DBT_PROFILES_DIR` points to this checkout's `.dbt` directory. |
| Connection failure | `dbt debug` output and access to the local `data/` directory. |
| Old folder path in a terminal | A new terminal is opened in the current checkout. |
