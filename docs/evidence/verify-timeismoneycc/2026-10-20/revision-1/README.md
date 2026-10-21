# Revision 1: receiver identity and interrupted runs

Fixes for PR #15's independent review and CodeRabbit findings. Original
commissioning evidence outside `revision-1/` is unchanged. These runs occurred
October 20 America/Chicago (October 21 UTC), with the verifier delta uncommitted
on `1b7a5d7afb9331b7fb1f17346f9f002aabba0eb7`.
[manifest.json](manifest.json) identifies the exact tested verifier digest;
`checkout_sha` in the browser results denotes that parent checkout, rather than
claiming the patched verifier was already committed. Published assets, pin,
hashes, deployments, and product code remain unchanged.

## Product identity: before and after

- [Original reviewer reproducer](before-generic.txt), adapted only to the prepared
  worktree/evidence directory: a generic shop with `Kindle` in navigation passed
  the original `follow()` check. Its [result](before-generic/result.json) and
  [screenshot](before-generic/generic-homepage.jpg) preserve the false pass.
- [Pre-fix regression results](before-regression/results.json): **8 pass / 24 fail,
  exit 1**. The 24 receiver cases accept the four real-shaped product fixtures
  but expose 20 false acceptances; eight interruption assertions expose four
  missing completion/failure semantics. These are harness regressions, not
  production product outcomes.
- [Patched regression results](after-regression/results.json): **36 pass / 0 fail,
  exit 0**. Four isolated product-shaped receivers pass; navigation-only,
  navigation-heading, title-only, hidden-heading, wrong-host, and wrong-path
  receivers fail for every product. The four navigation-heading cases were
  added after the initial baseline capture. The actual `follow()` function is
  extracted from the selected verifier source; only its receiver hosts are
  changed to the disposable loopback server. Product paths and heading patterns
  retain the real contracts. This proves the harness, not external availability.
- [Local real receiver result](local/results.json): Kindle passes on
  `www.amazon.fr/dp/B00QJDO0QC/...`, with the matched visible product heading
  recorded. [Screenshot](local/outbound-EUR.jpg) and [text](local/outbound-EUR.txt)
  show the actual anonymous product page. No Amazon form was submitted.
- The [Oster short-link observation](oster-redirect.json) identifies the specific
  Linio product path for model `BRLY07-R00-013`. This HEAD redirect observation
  supplies receiver identity; it does not prove Linio product content.

## Interruption: before and after

The regression helper launches the real local CLI, waits for its landing check,
then sends SIGINT during the natural demo cycle.

- [Before](before-regression/interrupted/results.json): exit -2; only passing
  checks and `finished_utc`, with no completion or interruption status.
- [After](after-regression/interrupted/results.json): exit 1,
  `completed: false`, `outcome: INTERRUPTED`, an explicit failed harness check,
  and `ended_utc`, with no `finished_utc`. The owned local port is closed and
  observed temporary staging is removed. [Landing evidence](after-regression/interrupted/landing-desktop.jpg)
  and results survive cleanup. The [transcript](after-regression/interrupted-transcript.txt)
  records the interruption failure.

Fully attempted runs now have `completed: true` and `finished_utc`; their
`outcome` can still be `FAIL`. Completion and success are separate facts.
Doctor failure or a harness exception leaves the run incomplete. Exit 0
requires completion and a passing outcome.

## Real journeys and retained blockers

- [Local](local/results.json): **14 pass / 5 fail, exit 1; completed**. Includes
  real external destinations plus local delayed CSS, offline recovery and
  JavaScript-disabled fallback. The owned local server port was checked closed
  after completion; screenshots/results remain.
- [Production](production/results.json): **11 pass / 5 fail, exit 1; completed**.
  All four visitor journeys were attempted read-only. All seven doctor checks
  pass, proving the immutable public snapshot is still served.
- The real Web Store listing and `Add to Chrome` render in both runs:
  [local](local/download-store.jpg), [production](production/download-store.jpg).
- Mobile still fails: no viewport meta tag, 375px device lays out at 981px.
- Taurinus, Bulk crisps, and Oster reached browser error documents from this
  host in both reruns. The original Bulk crisps parked-domain observation is
  retained in the commissioning evidence; this rerun establishes connection
  failure, not recovery of that destination.
- Kindle passes locally but production renders an Amazon interstitial, which
  fails the visible product-heading requirement. A normal anonymous GET session
  reaching the product is needed to prove that production attempt; owner
  credentials are irrelevant.
- Creator fails to load locally in this rerun but passes in production. This
  variability remains visible; neither result substitutes for the other.
- Receiver positives for Taurinus, crisps, and Oster are isolated harness
  fixtures only. Actual receiver content remains **UNPROVEN** pending public
  read-only browser access to their specified product pages. No sign-in,
  purchase, CAPTCHA submission, form delivery, or production write was tried.

Owner sign-in and receiver-side form delivery are **n/a**: the promotional site
has no authentication or forms. Extension installation/runtime remain outside
this site's scope. Snapshot defects need a separate reviewed asset/pin change;
this fix preserves the accepted bytes.

## Repeatable checks

See [checks.txt](checks.txt) for exact commands and outcomes, plus
[before](before-regression.txt) / [after](after-regression.txt) regression and
[local](local-transcript.txt) / [production](production-transcript.txt) transcripts.
The executable [regression helper](../../../../../.agents/skills/verify-timeismoneycc/regression.py)
and its invocation are documented in the skill. New JSON uses repository
formatting; trailing whitespace in captured public text is normalized. Original
evidence is preserved byte for byte.
