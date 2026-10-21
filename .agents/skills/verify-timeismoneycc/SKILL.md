---
name: verify-timeismoneycc
description: Verify the Time Is Money promotional website from a shell, locally and on Cloudflare, including rotating examples, download and product links, mobile layout, and recovery.
---

# Verify Time Is Money

Read [the feature map](features/README.md), then run from the repository root.
This repository publishes a static promotional page, not the Chrome extension.
There is no authentication, owner session, form, inbox, database, or delivery
receiver. Owner sign-in and receiver-side form delivery are **n/a**.

## Launch

Requirements: Git, Python 3.10+, network access, and Playwright's Chromium system
libraries. On a fresh Linux host, Playwright's `install --with-deps chromium`
can install the browser and OS libraries. Use a disposable virtual environment:

```bash
python3 -m venv ~/.cache/tmp/verify-timeismoneycc-tools
~/.cache/tmp/verify-timeismoneycc-tools/bin/pip install -r .agents/skills/verify-timeismoneycc/requirements.txt
~/.cache/tmp/verify-timeismoneycc-tools/bin/playwright install chromium
```

Use a fresh evidence path per run; helpers refuse to overwrite existing proof.
The `local` command launches its own loopback server on an OS-selected free port,
checks readiness, drives the page, and tears everything down automatically:

```bash
~/.cache/tmp/verify-timeismoneycc-tools/bin/python .agents/skills/verify-timeismoneycc/verify.py local --evidence ~/.cache/tmp/timeismoneycc-local-proof
```

The deployed source is **pinned**, as recorded in `cloudflare/site.json`, rather
than rebuilt from HEAD. Local verification reads that commit through Git and
stages only the assets in `cloudflare/files.sha256`, checking their digests.
Fetch the pinned commit if a shallow clone lacks it. The npm TypeScript output
is not the published website. Local writes are limited to temporary staging and
the requested evidence directory; no production data is written.

## Doctor

```bash
python3 .agents/skills/verify-timeismoneycc/verify.py doctor --evidence ~/.cache/tmp/timeismoneycc-doctor-proof
```

This needs only Python's standard library. It derives the canonical domain from
the production route in `cloudflare/wrangler.json`, then checks every public
asset's status and digest, root redirect to the project prefix, the homepage,
and unknown-path 404. Seven passing checks mean the served snapshot is worth
driving; they do not prove browser behavior. A failure stops the browser drive.
Rerun doctor to a fresh directory after a surprising first-party failure.

## Drive

```bash
~/.cache/tmp/verify-timeismoneycc-tools/bin/python .agents/skills/verify-timeismoneycc/verify.py production --evidence ~/.cache/tmp/timeismoneycc-production-proof
```

Both drives cover all four mapped journeys. The helper observes the real
four-second example timer through its full cycle and wrap; it never invokes
internal setters. It clicks the actual download, product, and creator anchors
and checks the rendered destinations. It checks a separate 375px mobile browser
context. Local mode additionally delays the real stylesheet response, rejects
an offline navigation and verifies online recovery, and loads with JavaScript
disabled. No backend exists to test for an outage.

Production and external destinations use disposable anonymous browser contexts.
Browser requests are restricted to GET/HEAD; attempted writes are blocked and
listed in `results.json`. Read-only inspection ends at the Chrome Web Store
listing and its `Add to Chrome` control. Installing the extension or signing
into Google is outside this repository's visitor journey.

Exit **0** means every requested check passed. Exit **1** means at least one
failure or unmet prerequisite; inspect `results.json` rather than treating the
transcript's final passing line as success. Outbound failures do not suppress
later checks. Keep broken journeys in the map and report their exact results.

## Evidence

Each run writes `results.json`, screenshots (full-page for the primary page,
viewport-sized for external destinations and mobile), and bounded public page
text. Results pair actions with rendered fields, clicked destinations, HTTP
statuses, snapshot identity, and errors. Screenshots show desktop, each demo
state, outbound destinations where loadable, and mobile layout. Failed browser
navigations can produce browser error screenshots instead of destination proof.
No cookies, storage, credentials, response headers, or private user data are
saved. Evidence from the commissioning run lives under
`docs/evidence/verify-timeismoneycc/2026-10-20/`.

The [commissioning report](../../../docs/evidence/verify-timeismoneycc/2026-10-20/README.md)
distinguishes passing first-party behavior from retained product defects and
external destinations unproven from this host. A 200 alone is not receiver proof:
the Web Store must render the exact extension name and install control; product
destinations must render recognizable product content.

## Cleanup

Normal completion and failed checks close the owned browser/contexts, stop and
close the owned HTTP server, and remove temporary staging under `~/.cache/tmp`.
Evidence and the reusable tools virtual environment remain. An interrupted
foreground run can be stopped with Ctrl-C; the helper's `finally` path retains
results and stops its server. Never kill an unrelated server or browser.
Confirm `results.json` and screenshots still exist after the command exits.

## Helpers

`verify.py` is executable (`chmod +x` is preserved in Git); the Python-prefixed
invocations above select the environment with Playwright. `doctor` works with
system Python. `verify.py --help` lists the three modes and evidence argument.
For future map upkeep, use `/maintain-verification-skill`; inspect the source
and drive every mapped feature before changing its expected outcomes.
