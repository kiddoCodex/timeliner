# timeliner

Builds a chronological "super timeline" from filesystem metadata - the
same basic idea as `mactime` or the simplest mode of `log2timeline`. Walk
a directory, pull the mtime/atime/ctime off every file, and lay all of it
out on one sorted timeline. Good for getting a quick read on "what
happened, and when" during an investigation before reaching for something
heavier.

No external dependencies.

## Usage

```
python3 timeliner.py /path/to/case
python3 timeliner.py /path/to/case --since 2026-08-01 --until 2026-08-13
python3 timeliner.py /path/to/case --csv timeline.csv
python3 timeliner.py /path/to/case --type m --type c
```

```
[*] 6 timeline event(s) from /tmp/fimtest (0 path(s) unreadable)

2026-08-14 01:21:06  MODIFIED            9  /tmp/fimtest/c.txt
2026-08-14 01:21:06  CHANGED             9  /tmp/fimtest/c.txt
2026-08-14 01:21:06  MODIFIED           14  /tmp/fimtest/a.txt
```

## Options

| flag | meaning |
|------|---------|
| `--since DATE` / `--until DATE` | only include events in this window (`YYYY-MM-DD`) |
| `--type {m,a,c}` | only include modified/accessed/changed events (repeatable) |
| `--csv FILE` | write the full timeline to CSV instead of truncating at `--top` |
| `--top N` | how many events to print to console (default 200) |

## Why three timestamps

Each file contributes up to three events - mtime (content modified), atime
(last accessed), and ctime (metadata/inode changed, or creation time on
some platforms). Looking at all three together is what makes this useful
for investigations: a file whose ctime changed but mtime didn't often
means permissions or ownership were touched without the content being
edited, for example.

## Limitations

This reads whatever timestamps the OS and filesystem expose - it doesn't
recover deleted files, doesn't parse filesystem journals, and `atime` may
be unreliable if the filesystem was mounted with `noatime`. For real
forensic work on a disk image, use something like Plaso/log2timeline or
The Sleuth Kit instead; this is meant for a fast first pass on a live
directory you already have access to.

## License

MIT, see LICENSE.
