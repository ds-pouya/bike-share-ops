# Initial trip dataset

I selected the January 2025 NYC Citi Bike archive as the initial development dataset. It is a complete monthly archive with enough records to explore station demand and data quality. One winter month does not support seasonal conclusions; additional months will be added later.

## Provenance

- Provider: Lyft Bikes and Scooters, LLC, through the [Citi Bike system-data page](https://citibikenyc.com/system-data).
- Download: [202501-citibike-tripdata.zip](https://s3.amazonaws.com/tripdata/202501-citibike-tripdata.zip).
- Downloaded: 2026-10-05.
- Provider last-modified header: 2025-07-03 15:41:08 UTC. This is the archive modification time, not the trip period.
- Archive size: 414,213,312 bytes (about 395 MiB).
- SHA-256: `ed3b0138903960afe50386ab44fec8bf52d69474b26f5c0af83e648094aea096`.
- Local location: `data/raw/citibike/2025-01/`; raw files and the download manifest are ignored by Git.

The downloader validates the expected byte count and ZIP CRC checks before recording a local SHA-256 fingerprint. The fingerprint identifies the downloaded version; it is not a provider-supplied authenticity signature. Existing archives are checked against their recorded fingerprint rather than downloaded again.

The [data-sharing policy](https://citibikenyc.com/data-sharing-policy) permits analysis subject to its terms and restricts distribution as a standalone dataset. I am keeping the source files local and publishing code and aggregate analysis. Offline test fixtures will use synthetic records. This project is independent of the provider.

## File coverage and grain

| File | Rows |
| --- | ---: |
| `202501-citibike-tripdata_1.csv` | 1,000,000 |
| `202501-citibike-tripdata_2.csv` | 1,000,000 |
| `202501-citibike-tripdata_3.csv` | 124,475 |
| **Total** | **2,124,475** |

All three files have the same 13 columns. One row represents one recorded trip; `ride_id` is the candidate key. The complete archive has 2,124,475 distinct ride IDs, with no missing IDs. The profiler uses all rows without sampling or filtering and reads source fields as text before explicit timestamp checks.

| Columns | Meaning and modeling considerations |
| --- | --- |
| `ride_id` | Trip identifier; preserve as text |
| `rideable_type` | Recorded bike type: classic or electric |
| `started_at`, `ended_at` | Source timestamps without explicit time-zone offsets; time-zone handling remains to be documented |
| `start_station_id`, `end_station_id` | Station identifiers; preserve as text rather than treating them as numbers |
| `start_station_name`, `end_station_name` | Recorded station labels; station ID is preferable to name for joins |
| `start_lat`, `start_lng`, `end_lat`, `end_lng` | Recorded coordinates; missingness and geographic suitability need consideration |
| `member_casual` | Recorded rider category: member or casual |

## Initial observations

- All start/end timestamps parse, and all recorded durations are positive.
- 564 records have no start station ID; 4,322 have no end station ID.
- 288 trips last more than 24 hours. They are flagged for investigation rather than automatically removed.
- No recorded trips last less than 60 seconds.
- 207 trips started before January. The earliest start is 2024-12-30 23:41:25.635; all end timestamps fall within January 2025. The archive label alone is therefore insufficient to define a departure-date filter.
- Bike types: 1,493,551 electric-bike trips and 630,924 classic-bike trips.
- Rider categories: 1,922,616 member trips and 201,859 casual trips.

These are source observations, not conclusions about unmet demand or station placement. Missing station IDs do not establish off-station drop-offs. Raw records remain unchanged; inclusion rules and their effect on counts will be explicit in later models.

The complete machine-readable profile is in [data_profile_2025_01.json](data_profile_2025_01.json). It records the profiling timestamp, DuckDB version, file counts, column missingness, and category counts.

## Reproducing the inspection

With the project environment activated, from the repository root:

```sh
python scripts/download_trips.py
python scripts/profile_trips.py
```

The downloader is deliberately limited to the selected initial archive. It uses the expected size checked on 2026-10-05 and stops if that changes. Failed downloads remain as `.part` files; another run restarts the download. The profiler extracts CSVs from the preserved ZIP, checks column names, and uses an in-memory DuckDB connection. It does not load or modify the project database.
