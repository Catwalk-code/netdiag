from netdiag.checks.traceroute import _compact_tracert_output


def test_compact_tracert_output_returns_hops():
    raw = """
Tracing route to 8.8.8.8 over a maximum of 30 hops
  1     1 ms     1 ms     1 ms  192.168.1.1
  2    10 ms    12 ms    11 ms  10.0.0.1
  3     *        *        *     Request timed out.
Trace complete.
"""
    summary = _compact_tracert_output(raw)
    assert "192.168.1.1" in summary
    assert "Request timed out." in summary


def test_compact_tracert_output_empty():
    assert _compact_tracert_output("No useful lines here") == "Нет данных по переходам маршрута."
