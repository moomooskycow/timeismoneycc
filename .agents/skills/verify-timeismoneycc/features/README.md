# Time Is Money visitor verification map

The published artifact is a public promotional page. It has no sign-in,
interactive calculator, saved data, form submission, or payment flow. The
extension itself lives elsewhere; this map proves its download handoff only.

Run `verify.py local` and `verify.py production` as documented in
[SKILL.md](../SKILL.md). Each runs doctor first, uses disposable browser contexts,
and writes proof to a fresh `--evidence` directory. Production browsing is
read-only; synthetic network faults run locally. No owner's credentials are
needed. A failed or skipped destination remains unproven, even if its anchor is
correct. Each check in `results.json` records its own pass/fail outcome.

| Feature                                           | Entry points                                                                    | Result checks                                                                                |
| ------------------------------------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| [Landing and currency examples](landing-demo.md)  | Canonical root and project prefix; timed examples                               | `doctor-*`, `landing`, `demo-cycle-and-wrap`                                                 |
| [Download the extension](download.md)             | `Download Now`                                                                  | `download-store-listing`                                                                     |
| [Follow examples and author](outbound-links.md)   | Four rotating product anchors; footer `Phaedrus`                                | `outbound:*`                                                                                 |
| [Mobile and failure recovery](mobile-recovery.md) | Mobile page; delayed network, offline/reload and JavaScript-disabled local page | `mobile-375`, `slow-stylesheet-local`, `offline-recovery-local`, `javascript-disabled-local` |

The four feature entries use the same four H2s: sub-features, user entry points,
drive recipe, and gotchas. Keep this index and the entries aligned when visitor
behavior changes. The commissioning evidence records current broken journeys;
these failures are not converted to expected passes.
