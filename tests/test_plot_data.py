from netdiag.ui.plot_data import TargetChecks, parse_ping_avg_ms, parse_ping_bars, parse_target_checks


def test_parse_ping_avg_ms_extracts_all_ok_values():
    report = "\n".join(
        [
            "[Router]",
            "ping: OK, avg=1 ms",
            "[Google DNS]",
            "ping: OK, avg=62 ms",
            "[NoData]",
            "ping: OK, avg=н/д",
        ]
    )

    assert parse_ping_avg_ms(report) == [1, 62]


def test_parse_ping_avg_ms_returns_empty_for_missing_values():
    report = "ping: FAIL\nping: ERROR (timeout)"
    assert parse_ping_avg_ms(report) == []


def test_parse_ping_bars_extracts_target_names_and_values():
    report = "\n".join(
        [
            "[Router]",
            "ping: OK, avg=1 ms",
            "[Google DNS]",
            "ping: OK, avg=62 ms",
            "[NoData]",
            "ping: OK, avg=н/д",
        ]
    )

    assert parse_ping_bars(report) == [("Router", 1), ("Google DNS", 62)]


def test_parse_target_checks_extracts_all_metrics():
    report = "\n".join(
        [
            "[Router]",
            "ping: OK, avg=1 ms",
            "dns: OK (IP: 192.168.1.1)",
            "tcp: FAIL (open: [], closed: [80])",
            "[Google DNS]",
            "ping: OK, avg=62 ms",
            "dns: FAIL (timeout)",
            "tcp: OK (open: [53], closed: [])",
        ]
    )

    assert parse_target_checks(report) == [
        TargetChecks(name="Router", ping_avg_ms=1, dns_ok=True, tcp_ok=False),
        TargetChecks(name="Google DNS", ping_avg_ms=62, dns_ok=False, tcp_ok=True),
    ]
