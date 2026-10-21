# Time Is Money visitor verification — 2026-10-20

This is evidence for the [CLI verification skill](../../../../.agents/skills/verify-timeismoneycc/SKILL.md).
Runs occurred on October 20 in America/Chicago (October 21 UTC), using synthetic
static examples and anonymous disposable Chromium contexts. No production data,
form submissions, Google sign-in, extension installation, purchases, or receiver
inboxes were used. Owner sign-in and form delivery are **n/a: this public static
site has no authentication or forms**.

## Deployment discovery

The live product is [the Cloudflare promotional page](https://timeismoneycc-site.mistystep.io/timeismoneycc/).
[GitHub repository metadata](deployment/repository.json) still advertises an old
Pages URL. Both legacy Pages URLs returned 404; that is not evidence of an
undeployed product. [Promotion is enabled](deployment/promotion.json), and the
[native deployment run](deployment/run.json) succeeded at base commit
`4e1d23ffc8253bd1c662de5d63429ced7fb3ae95`. Its
[Actions log](https://github.com/moomooskycow/timeismoneycc/actions/runs/38841718009)
records Cloudflare production deployment and seven real HTTP/parity checks.

The published source is pinned to
`3aa1acb09ee26fda6180efd58b4653d02a99bf30` in `cloudflare/site.json`.
Local mode stages those exact allowlisted bytes through Git, rather than claiming
that today's TypeScript build is deployed. The local server reproduces the
project prefix, root redirect and missing-path behavior used by these journeys;
Cloudflare-specific HTML canonicalization is exercised by the production doctor.

The [standard-library doctor](doctor/results.json) passed all seven checks:
five objects, root/homepage identity and missing-path 404. A separate
[default urllib probe](deployment/urls.json) received 403 at Cloudflare; the
named CLI user agent and anonymous Chromium can read the public site. No owner
authorization was required. This client-dependent response is retained rather
than confused with authentication or absence of a deployment.

## Browser proof

- [Local results](local/results.json): **15 pass, 4 fail; exit 1**. Every mapped feature plus delayed CSS,
  offline rejection/recovery and JavaScript-disabled fallback.
- [Production results](production/results.json): **11 pass, 5 fail; exit 1**. Anonymous read-only visitor
  journeys and a separate mobile context, preceded by the real HTTP doctor.
- Desktop: [local](local/landing-desktop.jpg), [production](production/landing-desktop.jpg).
- Natural timer: [initial example](production/demo-0.jpg), [MXN example](production/demo-4.jpg), [wrap to initial](production/demo-5.jpg).
- Download receiver: [Web Store screenshot](production/download-store.jpg) and
  [rendered text](production/download-store.txt). The listing shows the exact
  extension name and `Add to Chrome`; installation is outside this repository.
- Mobile failure: [375px device screenshot](production/landing-mobile.jpg).
- Local resilience: [delayed CSS](local/delayed-stylesheet.jpg),
  [online recovery](local/network-recovered.jpg),
  [JavaScript disabled](local/javascript-disabled.jpg).

Results pair each action with fields, clicked and final URLs, receiver GET
status, and exact errors. Third-party browser pages can change their URL through
the History API; the helper separately reads back the URL actually shown, then
checks rendered destination content. Screenshots use browser JPEG encoding to
keep each artifact below the repository's 500 KB limit. Page text is bounded;
cookies, headers, browser storage, and private records are omitted.

## Retained failures and limitations

- **Mobile layout fails:** accepted HTML lacks `meta[name=viewport]`; a 375px
  device lays out at 981px. Text and the download action appear scaled down.
  The helper records this as failure rather than accepting a desktop layout on
  a phone. See the [mobile screenshot](production/landing-mobile.jpg).
- **Bulk crisps points to a parked domain:** the destination says it may be
  for sale instead of displaying McCoy's crisps. See the
  [destination text](production/outbound-GBP.txt) and [screenshot](production/outbound-GBP.jpg).
- **Taurinus X200 cannot load from this host:**
  `https://shop.libiquity.com/product/taurinus-x200` reaches Chromium's error
  document. The receiving product page remains unproven; a separate curl probe
  also failed to connect. This is an observed host result, not a claim about
  every visitor's network.
- **Licuadora Oster cannot load from this host:**
  `http://bit.ly/2ldKpPN` reaches Chromium's error document. Destination usability
  remains unproven. The exact attempted link and error are in each result file.
- **Kindle is an external dependency:** the link redirects to Amazon France.
  The final local run displayed a real Kindle page (PASS); the final
  production run displayed an Amazon “continue shopping” interstitial (FAIL).
  The committed results and destination text establish each run's outcome;
  an interstitial fails product-content proof. No external form was submitted
  to bypass it. A normal anonymous session that reaches the product is required
  to prove an interstitial-blocked attempt; owner credentials are irrelevant.
- **Separate product scope:** this proves the promotional site's store handoff,
  not extension installation, extension runtime conversions, or Google account
  authentication. The install control can be disabled in headless Chromium.
- **Published bytes remain immutable:** these are retained defects and
  dependencies of the accepted snapshot. Repair requires an intentional
  reviewed source/pin/hash update under `cloudflare/ADR.md`. This PR changes
  verification and documentation only.

The helper returns exit 1 for any failure and keeps running unrelated checks.
It does not replace failed destinations with mocks, reinterpret failures as
passes, or claim the whole product is verified.

## Checks and cleanup

See [checks.txt](checks.txt) for exact commands and outcomes. Before this change,
base had no `.agents`/`.claude` visitor verification skill; native static parity
was green while these visitor defects remained. After this change, a shell
command proves working paths and reports broken ones with durable artifacts.

The local owned port was checked closed after cleanup, and evidence remained.
Each run removes its own staging and browser contexts. No shared server,
database, global browser profile, Cloudflare configuration, or deployment was
changed. No QA/review/judge or merge is claimed by this builder report.
