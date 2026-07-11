"""Build dist/singapore-gtfs.zip from data/raw. Fully offline.

Usage: uv run python -m sg_gtfs.build

Assembles rail + bus tables, runs the structural gates (checks.py), and only
writes the zip if every gate passes. Coverage warnings (interchange pairs
without a measured walk) are printed but non-fatal — routers street-route
those.
"""

import csv
import io
import sys
import zipfile
from pathlib import Path

from sg_gtfs import bus, checks, rail, service

# src/sg_gtfs/build.py -> parents[2] is the repo root
OUTPUT = Path(__file__).parents[2] / "dist" / "singapore-gtfs.zip"

AGENCY = [
    {
        "agency_id": "LTA",
        "agency_name": "Land Transport Authority (unofficial feed)",
        "agency_url": "https://www.lta.gov.sg",
        "agency_timezone": "Asia/Singapore",
    }
]
CALENDAR = [
    {
        "service_id": service.SERVICE_ID,
        "monday": 1,
        "tuesday": 1,
        "wednesday": 1,
        "thursday": 1,
        "friday": 1,
        "saturday": 0,
        "sunday": 0,
        "start_date": "20260101",
        "end_date": "20301231",
    }
]
FEED_INFO = [
    {
        "feed_publisher_name": "singapore-gtfs (built from primary data)",
        "feed_publisher_url": "https://github.com/Vorld/singapore-gtfs",
        "feed_lang": "en",
        "feed_version": "2026-07-12",
    }
]


def assemble() -> dict[str, list[dict]]:
    rail_trips, rail_times, rail_freq = rail.trips_and_times()
    bus_trips, bus_times, bus_freq = bus.trips_and_times()
    return {
        "agency": AGENCY,
        "calendar": CALENDAR,
        "feed_info": FEED_INFO,
        "stops": rail.stops() + bus.stops(),
        "routes": rail.routes() + bus.routes(),
        "trips": rail_trips + bus_trips,
        "stop_times": rail_times + bus_times,
        "frequencies": rail_freq + bus_freq,
        "transfers": rail.transfers(),
    }


def write_zip(tables: dict[str, list[dict]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, rows in tables.items():
            buffer = io.StringIO()
            writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
            zf.writestr(f"{name}.txt", buffer.getvalue())


def main() -> int:
    tables = assemble()

    failures = checks.run(tables)
    if failures:
        print(f"BUILD FAILED — {len(failures)} structural failures:")
        for f in failures:
            print(f"  {f}")
        return 1

    warnings = checks.coverage_warnings(tables)
    for w in warnings:
        print(f"warning: {w}")

    write_zip(tables, OUTPUT)
    sizes = {name: len(rows) for name, rows in tables.items()}
    print(f"\nwrote {OUTPUT} ({OUTPUT.stat().st_size / 1e6:.1f} MB)")
    print(", ".join(f"{k}={v}" for k, v in sizes.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
