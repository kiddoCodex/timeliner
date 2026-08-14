#!/usr/bin/env python3
"""
timeliner - builds a chronological "super timeline" from filesystem metadata.

This is the same idea behind mactime / log2timeline's simplest mode: walk a
directory, pull the modified/accessed/changed times off every file, and
lay every one of those events out on a single sorted timeline. Useful for
getting a quick feel for "what happened, and when" during an investigation
without reaching for a full forensics suite.

Usage:
    python3 timeliner.py /path/to/case
    python3 timeliner.py /path/to/case --since 2026-08-01 --until 2026-08-13
    python3 timeliner.py /path/to/case --csv timeline.csv
"""

import argparse
import csv
import os
import sys
from datetime import datetime

EVENT_LABELS = {"m": "MODIFIED", "a": "ACCESSED", "c": "CHANGED"}


def parse_date(s):
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError(f"couldn't parse date: {s!r} (try YYYY-MM-DD)")


def collect_events(root, since, until):
    events = []
    skipped = 0
    for dirpath, dirnames, filenames in os.walk(root):
        for name in filenames:
            path = os.path.join(dirpath, name)
            try:
                st = os.lstat(path)
            except OSError:
                skipped += 1
                continue
            for kind, ts in (("m", st.st_mtime), ("a", st.st_atime), ("c", st.st_ctime)):
                dt = datetime.fromtimestamp(ts)
                if since and dt < since:
                    continue
                if until and dt > until:
                    continue
                events.append((dt, kind, path, st.st_size))
    events.sort(key=lambda e: e[0])
    return events, skipped


def main():
    ap = argparse.ArgumentParser(description="Build a sorted filesystem timeline from mtime/atime/ctime.")
    ap.add_argument("directory")
    ap.add_argument("--since", type=parse_date, help="only include events on/after this date (YYYY-MM-DD)")
    ap.add_argument("--until", type=parse_date, help="only include events on/before this date (YYYY-MM-DD)")
    ap.add_argument("--csv", metavar="FILE", help="write the full timeline to a CSV (bodyfile-lite) file")
    ap.add_argument("--top", type=int, default=200, help="only print the first N events to console (default: 200)")
    ap.add_argument("--type", choices=["m", "a", "c"], action="append", dest="types",
                     help="only include this event type (repeatable); default is all three")
    args = ap.parse_args()

    if not os.path.isdir(args.directory):
        print(f"[!] Not a directory: {args.directory}", file=sys.stderr)
        sys.exit(1)

    events, skipped = collect_events(args.directory, args.since, args.until)

    if args.types:
        wanted = set(args.types)
        events = [e for e in events if e[1] in wanted]

    print(f"[*] {len(events)} timeline event(s) from {args.directory} ({skipped} path(s) unreadable)\n")

    for dt, kind, path, size in events[:args.top]:
        print(f"{dt.strftime('%Y-%m-%d %H:%M:%S')}  {EVENT_LABELS[kind]:<9}  {size:>10}  {path}")

    if len(events) > args.top:
        print(f"\n... and {len(events) - args.top} more event(s). Use --csv for the full timeline.")

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "event_type", "size", "path"])
            for dt, kind, path, size in events:
                writer.writerow([dt.strftime("%Y-%m-%d %H:%M:%S"), EVENT_LABELS[kind], size, path])
        print(f"[*] Full timeline written to {args.csv}")


if __name__ == "__main__":
    main()
