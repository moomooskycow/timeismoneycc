# Download the extension

A visitor follows `Download Now` to the real Time Is Money Chrome Web Store
listing and sees the extension name and install control.

## Sub-features

- `handoff`: click the site's anchor and follow the legacy store URL redirect.
- `listing`: confirm a rendered listing rather than a removed-item/error page.

## How to get to it (user POV)

Open the homepage and choose `Download Now` below the rotating examples.

## Driving it with verify.py

Preconditions: healthy page; anonymous GET access to Google's store.

- **Click.** Run `verify.py production --evidence ~/.cache/tmp/timeismoneycc-download-proof` using the tools Python. The helper clicks the actual `Download Now` link and observes its popup.
- **Prove.** `download-store-listing` requires HTTP 200 on `chromewebstore.google.com/detail/`, heading `Time Is Money`, and `Add to Chrome`. `download-store.jpg` and `.txt` show receiver content; the result names the clicked and final URL.

## Gotchas

- Google may show a “Switch to Chrome” notice in headless Chromium. The exact listing and install control must still render.
- The extension ID is `ooppbnomdcjmoepangldchpmjhkeendl`; a redirect to a generic store landing page fails proof.
- This site has no Google authentication. Extension installation and runtime conversion inside Chrome are separate product scope and remain untested here.
- Stop at the listing: do not install, sign in, submit reviews, or write external data.
