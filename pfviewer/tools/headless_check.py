#!/usr/bin/env python3
"""
headless_check.py — load pfviewer in headless Chromium, run steps, report errors.

Run from anywhere (it serves the repo root itself):

  python3 tools/headless_check.py --date 1906-07-01 --wait 40 \
      --step "eval:window._debugRails()" \
      --step "date:1912-07-01" --step "sleep:3000" --step "eval:window._debugRails()"

Steps (run in order, after the page has loaded and --wait seconds have passed):
  eval:<js>        evaluate a JS expression in the page, print JSON of the result
  date:<YYYY-MM-DD> set the viewer date through the date picker (as a user would)
  click:<selector>  click an element via JS (works even when hidden/off-screen)
  key:<key>         press a key (e.g. key:p)
  tod:<0..1>        set the TIME slider
  sleep:<ms>        wait

Only errors, page errors and warnings are shown (GPU-driver noise and the
expected 404s for optional sound/mask/bump files are hidden; --all shows
everything). Exit code 1 if there was a page error.

GOTCHAS (learned the hard way):
  * The scene is rendered by a software GL driver here: ~1 frame/s. The app clamps
    dt to 0.1 s per frame, so the timeline runs ~10× slower than real time. To
    advance the timeline fast, call window._debugTickTimeline(0.1) in a loop
    (see eval:), don't wait.
  * Rendering a frame can take tens of seconds; prefer the window._debug* hooks
    that don't render (e.g. _debugLOD, _debugRails, _debugWx).
  * index.html is one ES module: its variables are NOT reachable from eval:. Add a
    `window._something=...` hook inside the module for anything you need.
  * Needs: pip install playwright (in a venv) and a Chromium that Playwright can
    drive — set PW_CHROMIUM=/path/to/chrome, or it uses the newest
    ~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome. If Python has no
    playwright, set PYTHONPATH to a venv's site-packages that does.
"""
import argparse, glob, json, os, re, subprocess, sys, time

NOISE = re.compile(r'GPU stall|GL Driver Message|_mask\.png|bump_.*\.png|/sounds/|ERR_NETWORK_CHANGED')

def find_chromium():
    p = os.environ.get('PW_CHROMIUM')
    if p: return p
    c = sorted(glob.glob(os.path.expanduser('~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome')))
    if not c: sys.exit('No Chromium found: set PW_CHROMIUM or run `playwright install chromium`.')
    return c[-1]

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--date', help='start date YYYY-MM-DD (overrides CONFIG.timeline.startDate for this run)')
    ap.add_argument('--query', default='', help='query string for the page, e.g. "?year=1912&month=7&day=1"')
    ap.add_argument('--wait', type=float, default=35, help='seconds to wait after load before running steps')
    ap.add_argument('--step', action='append', default=[], help='see above; repeatable')
    ap.add_argument('--port', type=int, default=8765)
    ap.add_argument('--all', action='store_true', help='show all console output, not just errors/warnings')
    ap.add_argument('--phone', action='store_true', help='emulate a phone viewport + touch (mobile profile)')
    a = ap.parse_args()

    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))   # repo root (pfviewer/ is a subfolder)
    from playwright.sync_api import sync_playwright
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(a.port), '-d', repo], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    errors = 0
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=find_chromium(), args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader'])
            ctx = b.new_context(**(p.devices['Pixel 7'] if a.phone and 'Pixel 7' in p.devices else {}))
            pg = ctx.new_page(); t0 = time.time()
            def on_console(m):
                if a.all or (m.type in ('error', 'warning') and not NOISE.search(m.text)):
                    print(f'{time.time()-t0:6.1f}s {m.type.upper():7} {m.text[:600]}')
            def on_pageerror(e):
                nonlocal errors; errors += 1; print('PAGEERROR', str(e)[:1500], (getattr(e, 'stack', '') or '')[:1200])
            pg.on('console', on_console); pg.on('pageerror', on_pageerror)
            pg.on('response', lambda r: r.status >= 400 and not NOISE.search(r.url) and print('HTTP', r.status, r.url))
            if a.date:
                def cfg(route):
                    body = open(os.path.join(repo, 'pfviewer', 'config.js'), encoding='utf-8').read()
                    body = re.sub(r"startDate: '[\d-]+'", f"startDate: '{a.date}'", body, count=1)
                    route.fulfill(body=body, content_type='text/javascript')
                pg.route('**/pfviewer/config.js*', cfg)
            pg.goto(f'http://localhost:{a.port}/pfviewer/index.html{a.query}')
            pg.wait_for_timeout(int(a.wait * 1000))
            for st in a.step:
                kind, _, arg = st.partition(':')
                if kind == 'eval':
                    try: print('EVAL', arg, '->', json.dumps(pg.evaluate('()=>(' + arg + ')'), default=str)[:3000])
                    except Exception as e: print('EVAL', arg, '-> ERROR', str(e)[:400]); errors += 1
                elif kind == 'date':
                    pg.evaluate("d=>{const p=document.getElementById('date-picker');p.value=d;p.dispatchEvent(new Event('input'))}", arg)
                elif kind == 'click': pg.evaluate("s=>document.querySelector(s).click()", arg)
                elif kind == 'key': pg.keyboard.press(arg)
                elif kind == 'tod': pg.evaluate("v=>{const t=document.getElementById('tod-slider');t.value=v;t.dispatchEvent(new Event('input'))}", arg)
                elif kind == 'sleep': pg.wait_for_timeout(int(arg))
                else: print('unknown step', st)
            b.close()
    finally:
        srv.terminate()
    sys.exit(1 if errors else 0)

if __name__ == '__main__':
    main()
