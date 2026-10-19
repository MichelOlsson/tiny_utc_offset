# tiny_utc_offset

Parses human-written UTC offset strings like `GMT-5`, `+0530`, and `UTC+02:00` into `datetime.timezone` objects.

```python
from tiny_utc_offset import parse_utc_offset

tz = parse_utc_offset("GMT-5")
# tz is a datetime.timezone with offset -05:00

print(tz.utcoffset(None))   # -1 day, 19:00:00  (i.e. -5 hours)
print(tz.tzname(None))     # 'GMT-5'
```

## Why this exists

Configuration files, logs, and user input often carry UTC offsets in inconsistent formats: `Z`, `UTC+02:00`, `GMT-5`, `+0530`, `+05:30`. The standard library does not parse these — it only formats and applies `timezone` objects once you have one. This library fills that gap with a single function returning a ready-to-use `datetime.timezone`, with no third-party dependencies.

The trade-off: this is a parser, not a full timezone database. It produces fixed-offset zones only. `UTC+02:00` means exactly +02:00 forever, with no daylight saving rules. That is the correct behaviour for the inputs it accepts — if you need IANA rules, use `zoneinfo`.

## Edge cases

- Minutes must be 0–59. An offset like `+05:75` raises `ParseError`.
- `Z` and bare `UTC`/`GMT` produce the zero-offset timezone.
- A trailing `Z` (as in `+0530Z`) is accepted and ignored; only the numeric offset matters.
- `-00:00` is treated as zero offset, matching ISO 8601 semantics.
- Hours above 23 are not separately rejected — Python's `datetime.timezone` itself rejects offsets outside ±24 hours, so such inputs surface as a `ValueError` from the standard library.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

