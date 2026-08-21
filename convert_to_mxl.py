#!/usr/bin/env python3
"""Convert this corpus's MuseScore files to compressed MusicXML (.mxl).

MuseScore is the only thing that reads .mscx, which makes the corpus hard
to use from anything else — notation libraries, renderers and analysis
tools generally speak MusicXML. Committing a .mxl beside each .mscx costs
little (they compress to roughly 5% of the .mscx) and makes the scores
readable without MuseScore installed. The DCML harmony annotations survive
the conversion as <harmony> elements, so the analytic content travels with
the notes.

Usage:
    python convert_to_mxl.py                 # MS3/*.mscx -> mxl/*.mxl
    python convert_to_mxl.py --check         # report what would change
    python convert_to_mxl.py --force         # reconvert everything

Requires MuseScore. It looks for a MuseScore **3** first, because this
corpus was authored in 3.6.2 and MuseScore 4 writes MusicXML 4.0 where 3
writes 3.1 — the music and the harmony annotations are identical either
way, but 3.1 is the more widely readable of the two. Set $MSCORE or pass
--mscore to choose explicitly. Nothing else: standard library only.

Notes for anyone adapting this:

- It uses MuseScore's batch job mode (``mscore -j jobs.json``), which
  converts every file in one process and is far faster than one process
  per file. MuseScore frequently exits 134 (SIGABRT) on teardown even when
  every file converted, so the exit code is reported but not trusted: each
  output is opened and checked instead.
- **Convert with the version the corpus was authored in.** This one says
  so in its README — "edited, annotated and tested with MuseScore 3.6.2".
  Converting all 66 scores with both 3.6.2 and 4.7.4, every file differs,
  but only in the wrapper: MuseScore 4 declares MusicXML 4.0 and names
  itself in <software>, where 3.6.2 declares 3.1. All 8236 <harmony>
  annotations survive either way and Verovio reads both. MusicXML 3.1 has
  the broader tool support, so 3.6.2 is the default here.
- Only the canonical scores are converted. This corpus also has
  ``reviewed/*_reviewed.mscx``, which are annotation-review copies rather
  than the scores themselves.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


# Preferring 3 over 4 for the MusicXML version it writes, not because 4 is
# wrong. Standard install locations only — pass --mscore or set $MSCORE for
# a build kept elsewhere.
MUSESCORE_CANDIDATES = (
    "/Applications/MuseScore 3.app/Contents/MacOS/mscore",
    "/usr/local/bin/mscore3",
    "mscore3",
    "mscore",
)


def find_musescore(explicit: str | None) -> str:
    if explicit:
        return explicit
    if os.environ.get("MSCORE"):
        return os.environ["MSCORE"]
    for candidate in MUSESCORE_CANDIDATES:
        if Path(candidate).exists() or shutil.which(candidate):
            return candidate
    sys.exit("error: no MuseScore found. Install MuseScore 3, or set $MSCORE "
             "/ pass --mscore to point at one.")


def musescore_version(mscore: str) -> str:
    try:
        out = subprocess.run([mscore, "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        sys.exit(f"error: {mscore!r} not found on PATH — install MuseScore "
                 f"or pass --mscore /path/to/mscore")
    return (out.stdout or out.stderr).strip().splitlines()[0]


def is_readable_mxl(path: Path) -> str | None:
    """None if the file is a usable .mxl, else why it is not.

    A .mxl is a zip whose META-INF/container.xml names the score inside.
    Checking that is cheap and catches a truncated or empty conversion,
    which is the failure worth catching — MuseScore can exit cleanly and
    still leave a file nothing can open.
    """
    try:
        with zipfile.ZipFile(path) as archive:
            container = ET.fromstring(archive.read("META-INF/container.xml"))
            rootfile = container.find(".//{*}rootfile")
            if rootfile is None or not rootfile.get("full-path"):
                return "container names no rootfile"
            score = archive.read(rootfile.get("full-path"))
        if b"<score-partwise" not in score and b"<score-timewise" not in score:
            return "no score element"
    except (zipfile.BadZipFile, KeyError, ET.ParseError, OSError) as e:
        return f"{type(e).__name__}: {e}"
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", default="MS3", type=Path,
                    help="directory of .mscx files (default: MS3)")
    ap.add_argument("--out", default="mxl", type=Path,
                    help="directory to write .mxl into (default: mxl)")
    ap.add_argument("--mscore", default=None,
                    help="MuseScore executable (default: $MSCORE, then a "
                         "MuseScore 3 install, then mscore on PATH)")
    ap.add_argument("--force", action="store_true",
                    help="reconvert files that already have a .mxl")
    ap.add_argument("--check", action="store_true",
                    help="report what would be converted, write nothing")
    args = ap.parse_args()

    if not args.source.is_dir():
        sys.exit(f"error: no such directory {args.source}/ — run this from the "
                 f"corpus root, or pass --source")
    scores = sorted(args.source.glob("*.mscx"))
    if not scores:
        sys.exit(f"error: no .mscx files in {args.source}/")

    pending = [p for p in scores
               if args.force or not (args.out / f"{p.stem}.mxl").exists()]
    print(f"{len(scores)} .mscx in {args.source}/, {len(pending)} to convert")
    if args.check:
        for p in pending[:20]:
            print(f"  would convert {p.name}")
        if len(pending) > 20:
            print(f"  ... and {len(pending) - 20} more")
        return 0
    if not pending:
        print("nothing to do (use --force to reconvert)")
        return 0

    mscore = find_musescore(args.mscore)
    version = musescore_version(mscore)
    print(f"using {version}  ({mscore})")
    if not version.split()[-1].startswith("3."):
        print(f"note: this corpus was authored in MuseScore 3.6.2; {version} "
              f"will write MusicXML 4.0 rather than 3.1", file=sys.stderr)
    args.out.mkdir(parents=True, exist_ok=True)

    # One batch job for the lot, so MuseScore starts once rather than 66
    # times. Its exit code is not a verdict — it often exits 134 (SIGABRT)
    # on teardown having converted everything — so the outputs are checked
    # individually below and the exit code only tempers the report.
    jobs = [{"in": str(p), "out": str(args.out / f"{p.stem}.mxl")} for p in pending]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(jobs, fh)
        job_file = fh.name
    try:
        result = subprocess.run([mscore, "-j", job_file], capture_output=True)
    finally:
        Path(job_file).unlink(missing_ok=True)
    if result.returncode != 0:
        print(f"warning: {mscore} exited {result.returncode}; "
              f"checking output anyway", file=sys.stderr)

    failures = []
    for job in jobs:
        path = Path(job["out"])
        if not path.exists():
            failures.append((job["in"], "no output produced"))
            continue
        problem = is_readable_mxl(path)
        if problem:
            failures.append((job["in"], problem))

    written = len(jobs) - len(failures)
    total_in = sum(Path(j["in"]).stat().st_size for j in jobs)
    total_out = sum(Path(j["out"]).stat().st_size
                    for j in jobs if Path(j["out"]).exists())
    print(f"converted {written}/{len(jobs)}  "
          f"({total_in/1e6:.1f} MB of .mscx -> {total_out/1e6:.1f} MB of .mxl)")
    for name, why in failures:
        print(f"  FAILED {name}: {why}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
