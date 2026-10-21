# Landing and currency examples

A visitor learns that the Chrome extension converts prices into hours of work,
then sees five income/currency examples rotate and return to the first example.

## Sub-features

- `landing`: branded page, explanation, logo, stylesheet and visible download.
- `demo`: USD hourly/yearly, GBP, EUR and MXN examples with matching prices.
- `wrap`: the initial USD example returns after the full natural timer cycle.

## How to get to it (user POV)

- Open `https://timeismoneycc-site.mistystep.io/`; it redirects to `/timeismoneycc/`.
- Open the project prefix directly, then wait for the examples to change.

## Driving it with verify.py

Preconditions: doctor passes and Playwright Chromium is installed.

- **Open.** Run `verify.py production --evidence ~/.cache/tmp/timeismoneycc-landing-proof` using the tools Python from SKILL.md. `landing` requires heading `Time Is Money`, loaded logo and Bootstrap styles, and visible `Download Now`.
- **Observe.** `demo-cycle-and-wrap` waits on `#income-amount`, then compares all six visible fields: currency code/symbol, income, frequency, product and price/time. It captures six screenshots, from initial USD through the wrap.
- **Prove.** Read `results.json`, `landing-desktop.jpg`, and `demo-0.jpg` through `demo-5.jpg`. Expected income sequence is `7.25`, `50,756.00`, `26,500.00`, `9,61`, `31.30`, `7.25`; matching text and actual product hrefs appear in the result.

## Gotchas

- Allow the real 20-second cycle. Do not call `shiftExample`, set state or accelerate the timer to make this pass.
- The prices and time values are predefined promotional examples, not a visitor-editable calculator or live exchange rates.
- `cloudflare/site.json` pins the served commit. Editing current TypeScript or building `dist/` does not update production.
- A valid document response does not prove successful JavaScript startup or loaded external CSS; the browser checks both.
