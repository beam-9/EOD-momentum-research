"""Read-only loopback dashboard. No market access, orders, credentials or signal engine."""
from __future__ import annotations

import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


def dashboard_state(*, test_fixture=False):
    """Return unavailable by default; opt-in fixtures never qualify a trade candidate."""
    state = {
        'status': 'TEST_ONLY' if test_fixture else 'DATA_UNAVAILABLE',
        'verdict': 'NO TRADE',
        'reason_codes': ['SYNTHETIC_NOT_ADMISSIBLE' if test_fixture else 'NO_ELIGIBLE_GEX_SOURCE',
                         'D0_D1_NOT_PASSED', 'PROTOCOL_DRAFT'],
        'source_id': 'LOCAL_SYNTHETIC_FIXTURE' if test_fixture else 'NONE',
        'model_id': 'ILLUSTRATION_ONLY_V1' if test_fixture else None,
        'instrument': 'TEST_ETF' if test_fixture else None,
        'price_unit': 'synthetic USD per share' if test_fixture else None,
        'metric_kind': 'ILLUSTRATIVE_SIGNED_GAMMA' if test_fixture else None,
        'metric_unit': 'synthetic USD delta-notional per 1% underlying move' if test_fixture else None,
        'dealer_sign_model': 'ILLUSTRATIVE_CALL_PLUS_PUT_MINUS; NOT OBSERVED INVENTORY' if test_fixture else None,
        'expiry_scope': 'ALL_EXPIRIES_SYNTHETIC' if test_fixture else None,
        'session': 'SYNTHETIC_RTH' if test_fixture else None,
        'timezone': 'America/New_York',
        'event_ts': '2000-01-03T10:00:00-05:00' if test_fixture else None,
        'received_ts': '2000-01-03T10:00:01-05:00' if test_fixture else None,
        'last_valid_gex_ts': None,
        'freshness': 'SIMULATED / NO LIVE GEX' if test_fixture else 'UNAVAILABLE',
        'spot': 100.0 if test_fixture else None,
        'strike_totals': [{'strike': s, 'value': g} for s, g in [(95, -3), (100, 1), (105, 4)]]
                         if test_fixture else [],
        'heatmap': [{'strike': s, 'expiry': exp, 'value': value, 'contract_type': 'SYNTHETIC_AGGREGATE'}
                    for s, values in [(95, [-2, -1]), (100, [2, -1]), (105, [1, 3])]
                    for exp, value in zip(['2000-01-07', '2000-01-21'], values)] if test_fixture else [],
        'portfolio_repricing_zero_gamma_roots': {'status': 'NOT_COMPUTED', 'roots': []},
        'per_strike_bar_sign_crossings': {'status': 'NOT_COMPUTED', 'crossings': []},
        'ema': {'status': 'SYNTHETIC_DISPLAY_ONLY' if test_fixture else 'UNAVAILABLE',
                'timeframe': '5-minute confirmed RTH; no calculation implemented',
                'values': {'8': 100.2, '21': 99.9, '50': 99.4} if test_fixture else {}},
        'profile': {'status': 'SYNTHETIC_DISPLAY_ONLY' if test_fixture else 'UNAVAILABLE',
                    'scope': 'prior completed synthetic session; no calculation implemented',
                    'zones': {'POC': 99.5, 'VAH': 101.0, 'VAL': 98.0} if test_fixture else {}},
        'targets': [], 'invalidation': None, 'alerts_enabled': False,
        'profitability_evidence': 'NOT_EVALUATED',
    }
    return state


def render_dashboard(state):
    """Render escaped state with accessible tables; illustrative charts carry explicit units."""
    def text(value):
        return escape('UNAVAILABLE' if value is None else str(value))

    rows = ''.join(f'<tr><th scope="row">{text(key)}</th><td>{text(state[key])}</td></tr>'
                   for key in ['instrument', 'spot', 'price_unit', 'session', 'timezone', 'event_ts',
                               'received_ts', 'last_valid_gex_ts', 'source_id', 'model_id',
                               'dealer_sign_model', 'expiry_scope', 'metric_kind', 'metric_unit'])
    bars = ''.join(f'<tr><th scope="row">{text(row["strike"])}</th><td>{text(row["value"])}</td>'
                   f'<td><span class="bar" style="width:{abs(row["value"]) * 25}px"></span></td></tr>'
                   for row in state['strike_totals'])
    cells = ''.join(f'<tr><th scope="row">{text(row["strike"])}</th><td>{text(row["expiry"])}</td>'
                    f'<td class="{"positive" if row["value"] >= 0 else "negative"}">'
                    f'{text(row["value"])}</td><td>{text(row["contract_type"])}</td></tr>'
                    for row in state['heatmap'])
    contexts = ''.join(f'<section><h2>{name}</h2><p>{text(state[key]["status"])}</p>'
                       f'<p>{text(state[key][scope])}</p><pre>{text(json.dumps(state[key][values], indent=2))}'
                       '</pre></section>'
                       for name, key, scope, values in [('EMA 8 / 21 / 50', 'ema', 'timeframe', 'values'),
                                                       ('Volume profile', 'profile', 'scope', 'zones')])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>GEX research prototype</title>
<style>body{{font:16px system-ui;background:#101721;color:#f1f4fa;max-width:1000px;margin:auto;padding:24px}}
h1{{font-size:28px}}h2{{font-size:20px}}section{{background:#1c2735;padding:20px;margin:18px 0;border-radius:8px}}
.status{{padding:16px;border:2px solid #f2ba55}}table{{border-collapse:collapse;width:100%}}
th,td{{text-align:left;padding:8px;border-bottom:1px solid #506075;overflow-wrap:anywhere}}
.positive{{background:#164838}}.negative{{background:#592b39}}.bar{{display:block;background:#91b7ed;height:14px}}
pre{{white-space:pre-wrap}}a{{color:#abcaff}}</style></head><body><main>
<h1>GEX confluence · research prototype</h1><div class="status" role="status">
<h2>{text(state['status'])} · {text(state['verdict'])}</h2><p>{text(state['freshness'])}</p>
<p>Engineering display only. No validated signals, market fills or options profitability evidence.</p></div>
<p>Rejection reasons: {text(', '.join(state['reason_codes']))}</p>
<section><h2>Observation and conventions</h2><table><caption>Explicit provenance and units</caption>
<thead><tr><th scope="col">Field</th><th scope="col">Value</th></tr></thead><tbody>{rows}</tbody></table></section>
<section><h2>Strike gamma illustration</h2><p>{text(state['metric_unit'])}; synthetic only when populated.</p>
<table><caption>Signed strike totals</caption><thead><tr><th scope="col">Strike</th><th scope="col">Value</th>
<th scope="col">Magnitude</th></tr></thead><tbody>{bars}</tbody></table></section>
<section><h2>Strike × expiry heatmap</h2><p>TEST_ONLY cells; signs are numbers as well as colors.
0DTE-only view unavailable. All-expiry fixture is not a live chain.</p><table><caption>Synthetic cell exposures</caption>
<thead><tr><th scope="col">Strike</th><th scope="col">Expiry</th><th scope="col">Value</th>
<th scope="col">Contract type</th></tr></thead><tbody>{cells}</tbody></table></section>
<section><h2>Two distinct flip definitions</h2><p>Portfolio repricing zero-gamma roots: NOT COMPUTED.</p>
<p>Per-strike bar sign crossings: NOT COMPUTED. These are different statistics; no substitute flip is shown.</p>
</section>{contexts}<section><h2>Candidate and risk state</h2><p>NO TRADE. No targets or invalidation.
Advisory alerts disabled. D0 / D1 not passed; protocol DRAFT.</p></section>
<p><a href="/state.json">Read-only JSON state</a> · No provider connection or broker execution.</p>
</main></body></html>'''


def create_server(*, port=8765, test_fixture=False):
    """Bind IPv4 loopback only; expose two fixed read routes and no local files."""
    state = dashboard_state(test_fixture=test_fixture)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass  # No request body, query string or client-supplied value is logged.

        def do_GET(self):
            if self.headers.get('Host') not in {f'127.0.0.1:{self.server.server_port}',
                                                 f'localhost:{self.server.server_port}'}:
                self.send_error(403)
                return
            if self.path == '/':
                body, content_type = render_dashboard(state).encode(), 'text/html; charset=utf-8'
            elif self.path == '/state.json':
                body, content_type = json.dumps(state, sort_keys=True).encode(), 'application/json'
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            self.send_error(405)

        do_PUT = do_POST
        do_DELETE = do_POST
        do_PATCH = do_POST

    return HTTPServer(('127.0.0.1', port), Handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--test-fixture', action='store_true', help='Explicit synthetic engineering display only')
    args = parser.parse_args(argv)
    with create_server(port=args.port, test_fixture=args.test_fixture) as server:
        print(f'GEX read-only UI: http://127.0.0.1:{server.server_port} '
              f'[{"TEST_ONLY / NO LIVE GEX" if args.test_fixture else "DATA_UNAVAILABLE"}]', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
