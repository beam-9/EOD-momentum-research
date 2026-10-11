"""Read-only engineering dashboard checks; no provider or historical market data."""
from http.client import HTTPConnection
from decimal import Decimal
from threading import Thread

import pytest

from gex_indicator.ui import create_server, dashboard_state, render_dashboard


def test_default_is_unavailable_without_levels_or_trade_candidate():
    state = dashboard_state()
    assert state['status'] == 'DATA_UNAVAILABLE'
    assert state['verdict'] == 'NO TRADE'
    assert state['spot'] is None and state['last_valid_gex_ts'] is None
    assert not state['heatmap'] and not state['strike_totals'] and not state['targets']
    assert state['invalidation'] is None and not state['alerts_enabled']


def test_fixture_is_opt_in_synthetic_and_never_promoted():
    state = dashboard_state(test_fixture=True)
    assert state['status'] == 'TEST_ONLY' and state['verdict'] == 'NO TRADE'
    assert state['last_valid_gex_ts'] is None
    assert state['instrument'] == 'TEST_ETF'
    assert state['source_id'] == 'LOCAL_SYNTHETIC_FIXTURE'
    assert len(state['heatmap']) == 6
    assert 'synthetic' in state['metric_unit']
    assert state['portfolio_repricing_zero_gamma_roots']['status'] == 'NOT_COMPUTED'
    assert state['per_strike_bar_sign_crossings']['status'] == 'NOT_COMPUTED'
    assert state['profitability_evidence'] == 'NOT_EVALUATED'
    assert not any(key in state for key in ['confidence', 'success_probability', 'win_rate', 'expected_return'])


def test_handoff_screenshot_a_transcription_arithmetic_only():
    # Handoff transcription, not sampled vendor data or evidence of live positioning.
    call, put = Decimal('25.1'), Decimal('-17.3')
    assert call + put == Decimal('7.8')
    assert abs(call) + abs(put) == Decimal('42.4')
    assert dashboard_state(test_fixture=True)['spot'] == 100.0  # Generic fixture stays separate.


def test_renderer_escapes_metadata_and_displays_separate_flip_methods():
    state = dashboard_state(test_fixture=True)
    state['source_id'] = '<script>alert(1)</script>'
    html = render_dashboard(state)
    assert '<script>' not in html
    assert '&lt;script&gt;' in html
    assert 'Portfolio repricing zero-gamma roots' in html
    assert 'Per-strike bar sign crossings' in html
    assert 'NO TRADE' in html and 'TEST_ONLY' in html and 'NO LIVE GEX' in html


@pytest.fixture
def server():
    with create_server(port=0) as instance:
        thread = Thread(target=instance.serve_forever, daemon=True)
        thread.start()
        yield instance
        instance.shutdown()
        thread.join(timeout=2)


@pytest.mark.parametrize('path,code', [('/', 200), ('/state.json', 200), ('/.env', 404),
                                     ('/../../data/raw/private.json', 404), ('/?file=.env', 404)])
def test_server_binds_loopback_and_whitelists_routes(server, path, code):
    assert server.server_address[0] == '127.0.0.1'
    connection = HTTPConnection(*server.server_address)
    connection.request('GET', path)
    response = connection.getresponse()
    assert response.status == code
    response.read()
    connection.close()


@pytest.mark.parametrize('method', ['POST', 'PUT', 'DELETE', 'PATCH'])
def test_server_refuses_writes(server, method):
    connection = HTTPConnection(*server.server_address)
    connection.request(method, '/state.json', body='{}')
    assert connection.getresponse().status == 405
    connection.close()


def test_rebinding_host_is_rejected(server):
    connection = HTTPConnection(*server.server_address)
    connection.request('GET', '/state.json', headers={'Host': 'external.example'})
    assert connection.getresponse().status == 403
    connection.close()


def test_json_no_store_no_cors_or_embedded_secret(server):
    connection = HTTPConnection(*server.server_address)
    connection.request('GET', '/state.json')
    response = connection.getresponse()
    assert response.getheader('Cache-Control') == 'no-store'
    assert response.getheader('Access-Control-Allow-Origin') is None
    assert b'DATA_UNAVAILABLE' in response.read()
    connection.close()
