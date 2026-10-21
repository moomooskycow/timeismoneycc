# Rendered product heading fix

The [round-2 review](https://github.com/moomooskycow/timeismoneycc/pull/15#issuecomment-6305546523) reproduced hidden product text inside a visible generic heading passing all four receiver contracts. The verifier now matches each candidate heading's rendered inner text as well as checking visibility and ancestry.

- [Before](before/results.json): 36 PASS, 4 FAIL, exit 1. All four new hidden-descendant cases demonstrate false acceptance in the verifier at parent commit `cb8811682e97c1978cfc16dcf642613188b025b6`.
- [After](after/results.json): 40 PASS, 0 FAIL, exit 0. Four visible product fixtures still pass; hidden descendants, hidden headings, generic navigation, title-only, wrong-host and wrong-path cases reject. These are synthetic loopback fixtures of the checker, not live-product availability proof.
- [Real SIGINT result](after/interrupted/results.json): incomplete/interrupted, failure recorded, nonzero exit, no finished marker. Owned port closed, staging removed, evidence retained.
- [First post-fix attempt](first-attempt.log) stopped when Chromium failed to capture the local landing screenshot. No passing summary was produced. The unchanged helper succeeded on the subsequent fresh-directory run above; this host/browser failure is retained.

Both runs exercised the uncommitted delta on the parent revision; each result records the exact verifier source SHA-256. Original commissioning and revision-1 evidence remain unchanged. Published assets, pin, hashes and deployment configuration remain unchanged. The independent round-2 QA and review retain real receiver proof and known production failures; no full live pass is claimed for this single rendered-text assertion delta.

Commands from the repository root, using the existing tools environment:

```bash
~/.cache/tmp/verify-timeismoneycc-tools/bin/python .agents/skills/verify-timeismoneycc/regression.py --evidence ~/.cache/tmp/timeismoneycc-hidden-before
# Apply rendered-inner-text assertion.
~/.cache/tmp/verify-timeismoneycc-tools/bin/python .agents/skills/verify-timeismoneycc/regression.py --evidence ~/.cache/tmp/timeismoneycc-hidden-after
# Initial browser screenshot attempt failed; retry identical source with fresh evidence.
~/.cache/tmp/verify-timeismoneycc-tools/bin/python .agents/skills/verify-timeismoneycc/regression.py --evidence ~/.cache/tmp/timeismoneycc-hidden-after-retry
git diff --check
```

Both Python helpers parse. Scope is one verifier assertion and four new regression cases; unrelated npm suites retain their passing revision-1 results. Mobile and destination findings remain tracked in [issue 16](https://github.com/moomooskycow/timeismoneycc/issues/16) and [issue 17](https://github.com/moomooskycow/timeismoneycc/issues/17).
