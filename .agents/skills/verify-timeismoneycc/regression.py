#!/usr/bin/env python3
"""Exercise product receiver rejection and Ctrl-C cleanup on disposable local servers."""
import argparse
import ast
import hashlib
import http.server
import importlib.util
import json
from pathlib import Path
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.parse

from playwright.sync_api import sync_playwright

SOURCE = Path(__file__).with_name('verify.py')
ROOT = SOURCE.resolve().parents[3]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', required=True, type=Path)
    parser.add_argument('--source-ref', help='optional Git ref for reproducing pre-fix failures')
    args = parser.parse_args()
    args.evidence.mkdir(parents=True, exist_ok=False)
    source = (subprocess.check_output(['git', 'show', args.source_ref + ':' + str(SOURCE.relative_to(ROOT))],
                                      cwd=ROOT, text=True) if args.source_ref else SOURCE.read_text())
    spec = importlib.util.spec_from_file_location('verifier', SOURCE)
    verifier = importlib.util.module_from_spec(spec)
    exec(compile(source, str(SOURCE), 'exec'), verifier.__dict__)
    follow_node = next(node for node in ast.walk(ast.parse(source))
                       if isinstance(node, ast.FunctionDef) and node.name == 'follow')
    follow_code = compile(ast.Module(body=[follow_node], type_ignores=[]), str(SOURCE), 'exec')
    checks = []

    def record(name, passed, detail):
        checks.append({'name': name, 'status': 'PASS' if passed else 'FAIL', 'detail': detail})
        print(checks[-1], flush=True)

    bodies = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(bodies[self.path].encode())

        def log_message(self, *_):
            pass

    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f'http://127.0.0.1:{server.server_port}'
    products = [
        ('Taurinus X200', '/product/taurinus-x200', 'Taurinus X200', 'taurinus'),
        ('Bulk crisps', "/products/McCoy%27s-Salted-Ridge-Cut-Potato-Crisps-30-x-50G.html",
         "McCoy's Salted Ridge Cut Potato Crisps 30 x 50G", 'mccoy'),
        ('Kindle Paperwhite', '/dp/B00QJDO0QC', 'Kindle Paperwhite (7ème génération)', 'kindle'),
        ('Licuadora Oster', '/p/licuadora-oster-brly07-r00-013-con-motor-reversible-vino-vdataf',
         'Licuadora Oster BRLY07-R00-013 con motor reversible', 'oster'),
    ]
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            namespace = {**verifier.__dict__, 'page': page, 'capture': lambda *_: None}
            if 'PRODUCT_RECEIVERS' in namespace:
                # Change only the receiver host for isolated fixtures, retaining product paths/headings.
                namespace['PRODUCT_RECEIVERS'] = {
                    name: (urllib.parse.urlsplit(base).netloc, path, heading)
                    for name, (_, path, heading) in namespace['PRODUCT_RECEIVERS'].items()
                }
            exec(follow_code, namespace)
            for product, path, heading, token in products:
                for variant in ['product', 'navigation-only', 'navigation-heading', 'title-only', 'hidden-heading', 'wrong-host', 'wrong-path']:
                    target = base + path
                    body = '<h1>' + heading + '</h1><p>Product specifications</p>'
                    if variant in ('navigation-only', 'navigation-heading', 'title-only', 'hidden-heading'):
                        body = '<title>' + (heading if variant == 'title-only' else 'Generic shop') + '</title>'
                        body += '<nav>' + heading + '</nav><h1>Welcome to our shop</h1>'
                        if variant == 'navigation-heading':
                            body += '<nav><h2>' + heading + '</h2></nav>'
                        if variant == 'hidden-heading':
                            body += '<h2 hidden>' + heading + '</h2>'
                    if variant == 'wrong-host':
                        target = target.replace('127.0.0.1', 'localhost')
                    if variant == 'wrong-path':
                        target = base + '/shop'
                    bodies[urllib.parse.urlsplit(target).path] = body
                    bodies['/'] = '<a target="_blank" href="' + target + '">' + product + '</a>'
                    page.goto(base + '/')
                    kwargs = ({'product_name': product} if 'PRODUCT_RECEIVERS' in namespace else {'expected_text': token})
                    try:
                        result = namespace['follow']('fixture', page.get_by_role('link', name=product), **kwargs)
                        accepted, detail = True, result
                    except RuntimeError as error:
                        accepted, detail = False, str(error)
                    record(product + ':' + variant, accepted == (variant == 'product'), detail)
                    assert len(context.pages) == 1, 'follow left a popup open'
            context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()

    evidence = args.evidence.resolve() / 'interrupted'
    cache = Path.home() / '.cache/tmp'
    before = set(cache.glob('timeismoneycc-*'))
    code = '__file__ = ' + repr(str(SOURCE)) + '\n' + source
    command = [sys.executable, '-c', code, 'local', '--evidence', str(evidence)]
    with (args.evidence / 'interrupted-transcript.txt').open('w') as transcript:
        child = subprocess.Popen(command, cwd=ROOT, stdout=transcript, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + 35
            while time.monotonic() < deadline:
                try:
                    partial = json.loads((evidence / 'results.json').read_text())
                    if any(c['name'] == 'landing' and c['status'] == 'PASS' for c in partial['checks']):
                        break
                except (FileNotFoundError, json.JSONDecodeError):
                    pass
                if child.poll() is not None:
                    raise RuntimeError('child exited before landing; see interrupted transcript')
                time.sleep(0.1)
            else:
                raise RuntimeError('child did not reach landing within 35 seconds')
            staging = [p for p in set(cache.glob('timeismoneycc-*')) - before
                       if (p / 'timeismoneycc/index.html').is_file()]
            child.send_signal(signal.SIGINT)
            exit_code = child.wait(timeout=30)
        finally:
            if child.poll() is None:
                child.kill()
                child.wait()
    result = json.loads((evidence / 'results.json').read_text())
    record('interrupt:exit', exit_code != 0, {'exit_code': exit_code})
    record('interrupt:incomplete', result.get('completed') is False, {'completed': result.get('completed')})
    record('interrupt:outcome', result.get('outcome') == 'INTERRUPTED', {'outcome': result.get('outcome')})
    record('interrupt:failure-recorded', any(c['status'] == 'FAIL' and 'KeyboardInterrupt' in str(c['detail'])
                                          for c in result['checks']), result['checks'][-1])
    record('interrupt:no-finished-marker', 'finished_utc' not in result, {'finished_utc': result.get('finished_utc')})
    address = urllib.parse.urlsplit(result['base'])
    with socket.socket() as probe:
        closed = probe.connect_ex((address.hostname, address.port)) != 0
    record('interrupt:server-closed', closed, {'base': result['base']})
    record('interrupt:staging-removed', bool(staging) and all(not p.exists() for p in staging),
           {'observed_staging_count': len(staging), 'remaining_count': sum(p.exists() for p in staging)})
    record('interrupt:evidence-retained', (evidence / 'landing-desktop.jpg').is_file(), 'landing screenshot and results survive cleanup')
    output = {'source_ref': args.source_ref or 'working-tree', 'verifier_sha256': hashlib.sha256(source.encode()).hexdigest(),
              'scope': 'synthetic loopback receiver fixtures; actual CLI local run interrupted with SIGINT', 'checks': checks}
    (args.evidence / 'results.json').write_text(json.dumps(output, indent=2) + '\n')
    return int(any(check['status'] == 'FAIL' for check in checks))


if __name__ == '__main__':
    raise SystemExit(main())
