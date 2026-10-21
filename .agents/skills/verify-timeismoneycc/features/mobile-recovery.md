# Mobile and failure recovery

A visitor reads the page and reaches its download action on a phone, and can
reload after a connection failure. Static essential content remains available
when JavaScript is disabled.

## Sub-features

- `mobile`: a true 375px device viewport, no horizontal overflow, usable download target.
- `slow`: a delayed real Bootstrap response still leads to the styled page.
- `offline-recovery`: offline navigation rejects, then online navigation restores the page and cycling examples.
- `no-script`: initial example and download survive without JavaScript.
- `missing`: unknown paths return 404 rather than a misleading success page.

## How to get to it (user POV)

- Open the homepage on a narrow mobile browser.
- Reload while offline, reconnect and reopen the homepage.
- Disable JavaScript and load the page, or visit an unknown path.

## Driving it with verify.py

Preconditions: healthy first-party assets. Fault injection runs against the
owned local server only; the mobile check also runs read-only in production.

- **Phone.** Run `verify.py production --evidence ~/.cache/tmp/timeismoneycc-mobile-proof` using the tools Python. `mobile-375` checks the mobile viewport declaration, actual layout width, document overflow and a minimum 44px download target; retain `landing-mobile.jpg`.
- **Recovery.** Run `verify.py local --evidence ~/.cache/tmp/timeismoneycc-recovery-proof`. `slow-stylesheet-local` delays the real CSS response by 750ms and requires applied styles; `offline-recovery-local` requires rejected navigation, then fresh page load and the next natural example.
- **Fallback.** The local command loads a new JavaScript-disabled context; `javascript-disabled-local` requires the initial USD price/time and visible download anchor. It captures `javascript-disabled.jpg`.
- **Missing.** Every mode's doctor requests `/timeismoneycc/__verify_missing__` and requires HTTP 404. Local staging has no backend or data store to seed or simulate.

## Gotchas

- The accepted HTML currently lacks a viewport meta tag. A desktop page squeezed onto a phone is a failed mobile journey even when no horizontal scrollbar appears.
- Offline refusal is a browser/network state, not an app-specific error screen. Recovery must resume the real animation after a fresh navigation.
- This is a network-delayed response check, not a performance benchmark or proof of offline caching.
- JavaScript-disabled mode has static content but no rotating examples or generated author footer. Those interactive features remain covered by the normal browser drive.
