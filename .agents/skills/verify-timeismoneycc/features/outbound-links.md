# Follow examples and author

A visitor follows a rotating product example to its product page, or follows
the footer's `Phaedrus` link to the creator's public site.

## Sub-features

- `products`: Taurinus X200, Bulk crisps, Kindle Paperwhite and Licuadora Oster.
- `creator`: the footer's author destination.

## How to get to it (user POV)

- Wait until the chosen product appears beside its example price, then click its name.
- Choose `Phaedrus` in the footer after page initialization.

## Driving it with verify.py

Preconditions: healthy page, working natural example cycle and public GET access
to each destination. No third-party account is required or used.

- **Click products.** Run `verify.py production --evidence ~/.cache/tmp/timeismoneycc-links-proof` using the tools Python. The helper waits on each `#example-product a` name, clicks the real anchor and captures the destination.
- **Prove products.** `outbound:*` requires a real HTTP 200 and recognizable product content (`taurinus`, `mccoy`, `kindle`, or `oster`). Read the clicked/final URLs in results and the `outbound-*.jpg`/`.txt` artifacts. A parked-domain page or generic shop homepage fails.
- **Click creator.** The same command clicks the exact `Phaedrus` link, requires HTTP 200 and recognizable author content, and saves `creator.jpg`/`.txt`.

## Gotchas

- These are old external links. Connection errors, short-link failures, parked domains, CAPTCHA, or denied requests leave destination usability unproven; report the attempted URL and exact observed error.
- A dead external destination is not repaired by intercepting it with a fixture or accepting its anchor alone. Production content is an immutable accepted snapshot; replacing links needs a separately reviewed snapshot/source/hash update.
- USD hourly and yearly share the Taurinus anchor; drive that destination once, while the demo checks both display states.
- Some links start with HTTP and redirect to HTTPS. Preserve and observe the real chain; no purchases or form submissions are part of this recipe.
