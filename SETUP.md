# Bike Share Ops setup guide

This local project uses dbt for SQL transformations, DuckDB as its database, a Python virtual environment for isolation, and direnv to prepare your terminal automatically.

## Daily use

```sh
cd ~/dev/github/bike-share-ops
dbt debug
dbt build
```

Entering the folder activates `.venv` and sets `DBT_PROFILES_DIR` automatically. Leaving it unloads those settings. You do not need to run `source`, `export`, or `deactivate` in daily work.

`dbt debug` checks that dbt and DuckDB can connect. Its final line should be `All checks passed!`. `dbt build` runs models, seeds, snapshots, and tests in dependency order.

## Project map

```text
bike-share-ops/
├── .venv/                Project-only Python packages; not committed
├── .envrc                Automatic terminal setup for direnv
├── .dbt/profiles.yml     DuckDB connection configuration
├── data/analytics.duckdb Local database file; not committed
├── dbt_project.yml       dbt project configuration
├── models/               SQL models
│   ├── staging/          Clean, source-aligned models
│   └── marts/            Business-facing tables and views
├── seeds/                Small version-controlled CSV reference data
├── tests/                Custom data tests
└── target/               Generated dbt files; not committed
```

The `dbt-duckdb` software package lives inside `.venv`. The separate `data/analytics.duckdb` file is the actual database that stores your tables and views. The profile tells dbt where that file lives.

## VS Code

Open the project folder with **File → Open Folder**, selecting `~/dev/github/bike-share-ops`. After a rename, close terminals belonging to the old folder and create a new integrated terminal. Existing interpreter selections can also retain the old path: run **Python: Select Interpreter** and choose `.venv/bin/python` in the renamed folder.

Workspace settings select the local Python interpreter by default and point new integrated terminals at `.dbt` for the dbt profile. Python environments contain absolute paths, so moving a folder requires repairing or recreating the environment before using it.

Recommended extensions (also listed in `.vscode/extensions.json`):

- [Python by Microsoft](https://marketplace.visualstudio.com/items?itemName=ms-python.python) for interpreter selection and Python tooling.
- [YAML by Red Hat](https://marketplace.visualstudio.com/itemdetails?itemName=redhat.vscode-yaml) for configuration editing.

No dbt extension or account is required for the first lessons; dbt runs from the integrated terminal.

If you do not use direnv, activate explicitly:

```sh
source .venv/bin/activate
export DBT_PROFILES_DIR="$PWD/.dbt"
dbt debug
dbt parse
```

## Create a new project from scratch

Replace `my_dbt_project` with your project name.

### 1. Create the standard dbt project structure

```sh
cd ~/dev/github
dbt init my_dbt_project
```

`dbt init` creates dbt's starter project folders: `models`, `seeds`, `tests`, `macros`, `analyses`, and `snapshots`, plus starter config files. It asks questions about the adapter and connection. Choose DuckDB for a local database.

Do this from the parent directory. Running `dbt init my_dbt_project` while already inside that folder would create an unwanted nested project.

### 2. Create the Python environment and install dbt

```sh
cd ~/dev/github/my_dbt_project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install dbt-duckdb
dbt --version
```

`python3 -m venv .venv` makes a project-only Python installation. `source .venv/bin/activate` activates it in the current terminal. `pip install dbt-duckdb` installs dbt, its DuckDB adapter, and the DuckDB Python package.

Expected `dbt --version` shape:

```text
Core:
  - installed: 1.x.x
Plugins:
  - duckdb: 1.x.x
```

### 3. Create a project-local database profile

Create `.dbt/profiles.yml`:

```yaml
my_dbt_project:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "{{ env_var('DBT_DUCKDB_PATH', 'data/analytics.duckdb') }}"
      schema: main
      threads: 4
```

The top name must match `profile:` in `dbt_project.yml`. The database file does not need to exist yet; dbt creates it when it connects.

### 4. Automate activation with direnv

Install direnv once if necessary:

```sh
brew install direnv
```

Add this line once to `~/.zshrc` if it is not already present, then restart your terminal:

```sh
eval "$(direnv hook zsh)"
```

Create `.envrc` in the project:

```sh
source .venv/bin/activate
export DBT_PROFILES_DIR="$PWD/.dbt"
```

Authorize it once:

```sh
direnv allow
```

Expected output includes `direnv: loading .../.envrc` and an exported `DBT_PROFILES_DIR`. Any later change to `.envrc` requires another `direnv allow`, which is a safety check.

### 5. Ignore generated files and start Git

Create `.gitignore`:

```gitignore
.venv/
*.egg-info/
target/
dbt_packages/
logs/
data/*.duckdb
.DS_Store
```

Then run:

```sh
git init
git add .
git commit -m "Initialize dbt project"
```

`git init` enables version control. `git add .` stages your project files except ignored generated files. `git commit` records the initial version.

### 6. Verify the project

```sh
dbt debug
dbt parse
```

`dbt debug` checks the configuration and DuckDB connection. `dbt parse` validates project files without running your models. Both should complete successfully.

## First model

Create `models/staging/stg_example.sql`:

```sql
select
    1 as example_id,
    'Hello dbt' as example_name
```

Run it:

```sh
dbt run
```

Expected shape:

```text
1 of 1 OK created sql view model main.stg_example
Completed successfully
```

Use `dbt test` to run tests. Use `dbt build` for the normal full project run.

## Useful fixes

| Problem | Command | Result |
| --- | --- | --- |
| dbt command missing | `cd ~/dev/github/bike-share-ops` | direnv activates the project. |
| Profile not found | `direnv allow` | Re-authorizes and reloads `.envrc`. |
| Check setup | `dbt debug` | Tests dbt and DuckDB connection. |
| Remove dbt generated files | `dbt clean` | Deletes `target/` and `dbt_packages/`. |
| Reset local database | `rm data/analytics.duckdb` | Permanently removes local tables and views. |
