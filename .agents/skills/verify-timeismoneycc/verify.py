#!/usr/bin/env python3
"""Drive the public Time Is Money snapshot; keep failures and proof on disk."""
import argparse
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
CONFIG = json.loads((ROOT / 'cloudflare/site.json').read_text())
HOST = json.loads((ROOT / 'cloudflare/wrangler.json').read_text())['env']['production']['routes'][0]['pattern']
PREFIX = '/' + CONFIG['project_prefix'] + '/'
PRODUCTION = 'https://' + HOST
ASSETS = [line.split('  ', 1) for line in (ROOT / 'cloudflare/files.sha256').read_text().splitlines()]
STATES = [
    ('USD', '$', '7.25', 'hourly', 'Taurinus X200', '$445.00 (61h 23m)'),
    ('USD', '$', '50,756.00', 'yearly', 'Taurinus X200', '$445.00 (18h 15m)'),
    ('GBP', '£', '26,500.00', 'yearly', 'Bulk crisps', '£24.99 (1h 58m)'),
    ('EUR', '€', '9,61', 'hourly', 'Kindle Paperwhite', '99,99 EUR (10h 25m)'),
    ('MXN', '$', '31.30', 'hourly', 'Licuadora Oster', '$1,149.00 (36h 43m)'),
]


def public_url(url):
    parsed = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, '', ''))


def fetch(url):
    try:
        response = urllib.request.urlopen(urllib.request.Request(url, headers={
            'User-Agent': 'TimeIsMoney-verification/1.0', 'Accept-Encoding': 'identity',
        }), timeout=20)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        body = response.read(5_000_001)
        assert len(body) <= 5_000_000, 'response exceeded 5 MB'
        return response.status, public_url(response.url), hashlib.sha256(body).hexdigest()


class Proof:
    def __init__(self, directory, mode):
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=False)
        self.results = {
            'mode': mode, 'started_utc': datetime.now(timezone.utc).isoformat(),
            'checkout_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'serving_source': CONFIG['source_commit'], 'owner_sign_in': 'n/a: public static site; no authentication',
            'checks': [],
        }

    def record(self, name, passed, detail):
        self.results['checks'].append({'name': name, 'status': 'PASS' if passed else 'FAIL', 'detail': detail})
        self.save()
        print(f'{"PASS" if passed else "FAIL"} {name}: {detail}', flush=True)

    def check(self, name, action):
        try:
            detail = action()
            self.record(name, True, detail)
        except Exception as error:
            self.record(name, False, f'{type(error).__name__}: {str(error)[:1000]}')

    def save(self):
        (self.directory / 'results.json').write_text(json.dumps(self.results, indent=2, ensure_ascii=False) + '\n')


def doctor(base, proof):
    for digest, name in ASSETS:
        path = '/' + name.removeprefix('_site/')

        def asset(path=path, digest=digest):
            status, final, actual = fetch(base + path)
            assert status == 200 and actual == digest, f'{path}: HTTP {status}, sha256={actual}'
            assert urllib.parse.urlsplit(final).netloc == urllib.parse.urlsplit(base).netloc, final
            return {'url': final, 'status': status, 'sha256': actual}
        proof.check('doctor-asset:' + path, asset)

    def home():
        status, final, actual = fetch(base + '/')
        expected = next(digest for digest, name in ASSETS if name.endswith('/index.html'))
        assert status == 200 and final == base + PREFIX and actual == expected, (status, final, actual)
        return {'root_redirect_to': final, 'status': status, 'sha256': actual}
    proof.check('doctor-root-and-homepage', home)

    def missing():
        status, final, _ = fetch(base + PREFIX + '__verify_missing__')
        assert status == 404, f'{final}: HTTP {status}; expected 404'
        return {'url': final, 'status': status}
    proof.check('doctor-missing-path', missing)
    return all(item['status'] == 'PASS' for item in proof.results['checks'])


def stage(directory):
    for digest, name in ASSETS:
        local = name.removeprefix('_site' + PREFIX)
        body = subprocess.check_output(['git', 'show', CONFIG['source_commit'] + ':' + local], cwd=ROOT)
        assert hashlib.sha256(body).hexdigest() == digest, 'pinned source/hash drift: ' + local
        target = directory / name.removeprefix('_site/')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)


class LocalHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(302)
            self.send_header('Location', PREFIX)
            self.end_headers()
        else:
            super().do_GET()

    def log_message(self, *_args):
        pass


def drive(base, proof, local):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800}, service_workers='block')
        blocked_writes = []

        def read_only(route):
            if route.request.method not in ('GET', 'HEAD'):
                blocked_writes.append({'method': route.request.method, 'url': public_url(route.request.url)})
                route.abort()
            else:
                route.continue_()
        context.route('**/*', read_only)
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)[:500]))

        def capture(name, target=page):
            target.screenshot(path=str(proof.directory / (name + '.jpg')), type='jpeg', quality=75, full_page=target == page)
            (proof.directory / (name + '.txt')).write_text(target.locator('body').inner_text()[:10000] + '\n')

        def navigate():
            response = page.goto(base + PREFIX, wait_until='load', timeout=25000)
            assert response.status == 200, f'HTTP {response.status}'
            assert page.get_by_role('heading', name='Time Is Money', exact=True).is_visible()
            assert page.locator('#brand-image').evaluate('(image) => image.complete && image.naturalWidth > 0')
            assert page.get_by_role('link', name='Download Now').is_visible()
            assert not page.locator('form, input, [type="password"]').count(), 'new input/auth surface; update map'
            assert page.locator('body').evaluate('(body) => getComputedStyle(body).fontFamily').find('Helvetica') >= 0, 'Bootstrap stylesheet unavailable'
            capture('landing-desktop')
            return {'url': page.url, 'title': page.title(), 'logo_loaded': True, 'bootstrap_loaded': True}
        proof.check('landing', navigate)

        def snapshot():
            selectors = ['#currency-code', '#currency-symbol', '#income-amount', '#pay-frequency', '#example-product a', '#example-price']
            return tuple(page.locator(selector).inner_text().strip() for selector in selectors)

        def demo():
            observations = []
            for index, expected in enumerate(STATES + [STATES[0]]):
                page.wait_for_function('expected => document.querySelector("#income-amount").textContent === expected', arg=expected[2], timeout=6500)
                actual = snapshot()
                assert actual == expected, f'expected {expected}; rendered {actual}'
                link = page.locator('#example-product a')
                observations.append({'step': index, 'rendered': actual, 'href': link.get_attribute('href')})
                capture('demo-' + str(index))
            assert not errors, errors
            return {'natural_4_second_cycle': observations, 'uncaught_errors': errors}
        proof.check('demo-cycle-and-wrap', demo)

        def follow(name, locator, store=False, expected_text=None):
            href = locator.get_attribute('href')
            popup = None
            captured = False
            try:
                with page.expect_popup(timeout=15000) as event:
                    locator.click()
                popup = event.value
                popup.wait_for_load_state('domcontentloaded', timeout=25000)
                if store:
                    popup.get_by_role('heading', name='Time Is Money', exact=True).wait_for(timeout=15000)
                capture(name, popup)
                captured = True
                text = popup.locator('body').inner_text()
                assert popup.url.startswith(('https://', 'http://')), 'destination failed to load: ' + popup.url
                # A destination can replace its URL with History API after loading.
                # Read back that visible receiver URL instead of guessing its original response.
                receiver = popup.request.get(popup.url, timeout=20000)
                document = {'url': public_url(receiver.url), 'status': receiver.status}
                receiver.dispose()
                status = document['status']
                assert status == 200, f'{public_url(popup.url)}: last document {document}'
                assert urllib.parse.urlsplit(document['url']).netloc == urllib.parse.urlsplit(popup.url).netloc, document
                if store:
                    assert 'chromewebstore.google.com/detail/' in popup.url, popup.url
                    assert popup.get_by_role('heading', name='Time Is Money', exact=True).count(), text[:500]
                    assert popup.get_by_role('button', name='Add to Chrome', exact=True).count(), text[:500]
                    assert 'no longer available' not in text.lower(), text[:500]
                else:
                    assert text.strip(), 'empty destination body'
                    assert not any(term in text.lower() for term in ['this site can’t be reached', '404 not found', 'access denied']), text[:500]
                    assert expected_text in (popup.title() + ' ' + text).lower(), 'destination did not show expected content: ' + str(expected_text)
                return {'clicked': href, 'final_url': public_url(popup.url), 'document_response': document, 'title': popup.title()}
            except Exception as error:
                if popup and not captured:
                    try:
                        capture(name + '-failed', popup)
                    except Exception:
                        pass
                raise RuntimeError(f'clicked {href}; {type(error).__name__}: {str(error)[:700]}') from error
            finally:
                if popup:
                    popup.close()

        proof.check('download-store-listing', lambda: follow('download-store', page.get_by_role('link', name='Download Now'), store=True))
        # Drive each rotating link through the real anchor, waiting for the visible state.
        seen = set()
        for expected in STATES:
            name = expected[4]
            if name in seen:
                continue
            seen.add(name)

            def product(expected=expected):
                page.wait_for_function('name => document.querySelector("#example-product a").textContent === name', arg=expected[4], timeout=22000)
                token = {'Taurinus X200': 'taurinus', 'Bulk crisps': 'mccoy', 'Kindle Paperwhite': 'kindle', 'Licuadora Oster': 'oster'}[expected[4]]
                return follow('outbound-' + expected[0], page.locator('#example-product a'), expected_text=token)
            proof.check('outbound:' + name, product)
        proof.check('outbound:creator', lambda: follow('creator', page.get_by_role('link', name='Phaedrus', exact=True), expected_text='phaedrus'))

        def mobile():
            mobile_context = browser.new_context(viewport={'width': 375, 'height': 812}, is_mobile=True, device_scale_factor=1, service_workers='block')
            mobile_context.route('**/*', read_only)
            try:
                phone = mobile_context.new_page()
                phone.goto(base + PREFIX, wait_until='load', timeout=25000)
                capture('landing-mobile', phone)
                dimensions = phone.evaluate('({viewport: innerWidth, device: screen.width, content: document.documentElement.scrollWidth, meta: !!document.querySelector("meta[name=viewport]")})')
                button = phone.get_by_role('link', name='Download Now').bounding_box()
                assert dimensions['meta'] and dimensions['viewport'] == 375, f'mobile viewport scales desktop layout: {dimensions}'
                assert dimensions['content'] <= 375, f'horizontal overflow: {dimensions}'
                assert button and button['width'] >= 44 and button['height'] >= 44, button
                return {'dimensions': dimensions, 'download_bounds': button}
            finally:
                mobile_context.close()
        proof.check('mobile-375', mobile)

        if local:
            def delayed_style():
                delayed = []

                def delay(route):
                    delayed.append(public_url(route.request.url))
                    time.sleep(0.75)
                    route.continue_()
                page.route('**/bootstrap.min.css', delay)
                try:
                    page.goto(base + PREFIX, wait_until='load', timeout=25000)
                    assert delayed, 'stylesheet delay did not run'
                    assert page.get_by_role('link', name='Download Now').is_visible()
                    assert 'Helvetica' in page.locator('body').evaluate('(body) => getComputedStyle(body).fontFamily')
                    capture('delayed-stylesheet')
                    return {'delayed_stylesheet': delayed, 'result': 'styled page and download visible after delayed response'}
                finally:
                    page.unroute('**/bootstrap.min.css', delay)
            proof.check('slow-stylesheet-local', delayed_style)

            def recovery():
                context.set_offline(True)
                rejected = False
                try:
                    try:
                        page.reload(timeout=10000)
                    except Exception:
                        rejected = True
                finally:
                    context.set_offline(False)
                assert rejected, 'offline reload unexpectedly succeeded; offline refusal not proven'
                page.goto(base + PREFIX, wait_until='load', timeout=25000)
                assert page.get_by_role('link', name='Download Now').is_visible()
                page.wait_for_function('document.querySelector("#income-amount").textContent === "50,756.00"', timeout=6500)
                capture('network-recovered')
                return 'offline navigation rejected; fresh online navigation restored page and natural example cycle'
            proof.check('offline-recovery-local', recovery)

            def no_script():
                disabled = browser.new_context(java_script_enabled=False, service_workers='block')
                disabled.route('**/*', read_only)
                try:
                    fallback = disabled.new_page()
                    fallback.goto(base + PREFIX, wait_until='load', timeout=25000)
                    capture('javascript-disabled', fallback)
                    assert fallback.get_by_role('link', name='Download Now').is_visible()
                    assert fallback.locator('#example-price').inner_text().strip() == STATES[0][-1]
                    return 'initial USD example and download anchor remain usable with JavaScript disabled'
                finally:
                    disabled.close()
            proof.check('javascript-disabled-local', no_script)
        proof.results['blocked_non_read_requests'] = blocked_writes
        proof.results['browser_version'] = browser.version
        context.close()
        browser.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['doctor', 'local', 'production'])
    parser.add_argument('--evidence', required=True, type=Path, help='new evidence directory; existing paths are refused')
    args = parser.parse_args()
    proof = Proof(args.evidence.resolve(), args.mode)
    server = None
    thread = None
    os.makedirs(Path.home() / '.cache/tmp', exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix='timeismoneycc-', dir=Path.home() / '.cache/tmp') as scratch:
            base = PRODUCTION
            if args.mode == 'local':
                stage(Path(scratch))
                server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(LocalHandler, directory=scratch))
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                base = f'http://127.0.0.1:{server.server_port}'
            proof.results['base'] = base
            healthy = doctor(base, proof)
            if healthy and args.mode != 'doctor':
                drive(base, proof, local=args.mode == 'local')
            elif not healthy:
                proof.record('drive-precondition', False, 'doctor failed; instance not driven')
    except Exception as error:
        proof.record('harness', False, f'{type(error).__name__}: {str(error)[:1000]}')
    finally:
        if server:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        proof.results['cleanup'] = 'owned HTTP server stopped; temporary staging removed; browser contexts disposable'
        proof.results['finished_utc'] = datetime.now(timezone.utc).isoformat()
        proof.save()
    return int(any(item['status'] == 'FAIL' for item in proof.results['checks']))


if __name__ == '__main__':
    raise SystemExit(main())
