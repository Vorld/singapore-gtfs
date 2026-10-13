# singapore-gtfs

An unofficial GTFS feed for Singapore's public transport network: every MRT
and LRT line (184 stations, including the CCL6 stations that opened in July
2026) and every bus service (about 5,200 stops and 601 services).

I built this feed because I couldn't find any others of high enough quality.
Issues with other Singapore GTFS sources included missing stations, missing transfer times, 
opaque methodologies, and even at times incorrect information.

So I went to the primary sources — LTA, operators, government data — and built this feed from the roots, where every piece of information is traceable and every assumption is explained.

This GTFS feed models a typical weekday (05:30–23:30) rather than a full
calendar. It powers [a travel-time map of Singapore](https://traveltime.venugopal.net).

## What this repo is about

**First, transparency.** Every number in this feed can be traced back to a
source, a method, and a documented decision.
[docs/SOURCES.md](docs/SOURCES.md) explains where each piece of data came
from and how it was collected. Whether it's scraping SimplyGo for
station-to-station travel times or getting community-measured interchange transfer timings from Reddit.
[docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md) lists every modeling
decision and the reasoning behind it. If a number in the feed looks wrong to
you, you can find out exactly how it was produced — and challenge it.

**Second, a direction.** Today the data here is a set of snapshots I
collected by hand and by running one-off script. The only automated part is turning this data into a valid GTFS.
The goal is for this to become the reliable, up-to-date open feed for
Singapore. This means data collection that can be rerun at intervals, a build that follows automatically, and releases
that keep up as the transport network changes. [CONTRIBUTING.md](CONTRIBUTING.md)
explains the plan and how you can help!

## Quickstart

Just want the feed? Grab `singapore-gtfs.zip` from the
[Releases](../../releases) page.

To build it yourself, you need [uv](https://docs.astral.sh/uv/):

```bash
uv sync
uv run python -m sg_gtfs.build     # → dist/singapore-gtfs.zip
uv run pytest -q                   # model and structure tests
```

## Validation

Every CI run builds the zip and checks it with the official
[MobilityData gtfs-validator](https://github.com/MobilityData/gtfs-validator)
(pinned v8.0.1), failing on any error-severity notice. The current feed
validates with **zero errors**. A handful of non-error notices are accepted
(reviewed 2026-07-10): missing feed contact email (optional; the publisher
URL is set), missing `feed_info` start/end dates (validity lives in
`calendar.txt`), six mixed-case stop names that are genuinely spelled that
way (**one-north** is officially lowercase), one fast-travel warning on
service 187 where DataMall's cumulative distance jumps (the run time itself
is measured), and an info notice that the service extends to 2030
(deliberate — see [docs/ASSUMPTIONS.md](docs/ASSUMPTIONS.md)).

To run the validator yourself (needs Java 17+):

```bash
java -jar gtfs-validator-8.0.1-cli.jar -i dist/singapore-gtfs.zip -o validator-report
```

## What's in the feed

| File | Contents |
|---|---|
| `stops.txt` | 184 rail stations (interchanges as `parent_station` + one child per line) + ~5,200 bus stops |
| `routes.txt` | 14 rail patterns (MRT/LRT incl. loops and branches) + 601 bus services |
| `trips.txt`, `frequencies.txt` | One frequency-based trip per route/direction; headways averaged from published peak/off-peak figures |
| `stop_times.txt` | Rail: SimplyGo-calibrated inter-station run times + published SBS LRT chart times. Bus: measured first-bus differencing (95.9% of hops) with a fitted distance-speed fallback |
| `transfers.txt` | 70 measured interchange walk times (`transfer_type=2`) |
| `calendar.txt` | Single weekday service (see scope below) |

The feed is weekday-only, with a fixed 05:30–23:30 span and no `shapes.txt`
or `pathways.txt`. 

If you need a timetable-accurate feed with weekend calendars, this is not it — yet.

## Repository layout

```
data/raw/          dated snapshots of every primary source
scripts/extract/   the scripts I used to populate data/raw/
src/sg_gtfs/       building the GTFS from the data
tests/             model and structure tests
dist/              build output (gitignored)
```

More detail: [data/raw/README.md](data/raw/README.md) describes each
snapshot, and [scripts/extract/README.md](scripts/extract/README.md)
describes each collection script.

## Feedback

Found a wrong run time, a missing transfer, or a station quirk? Please [open
an issue](../../issues/new/choose). [CONTRIBUTING.md](CONTRIBUTING.md) covers
everything else, from challenging an assumption to helping build the
self-updating version of this feed.

## Licence

The code is [MIT](LICENSE). The data is built from third-party sources with
their own terms — [NOTICE.md](NOTICE.md) lists every attribution, including
data from the Land Transport Authority under the Singapore Open Data Licence.
This project is unofficial and is not endorsed by LTA, SMRT, SBS Transit,
SimplyGo, or any operator.
