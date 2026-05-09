from netdiag.ui.plot_data import parse_ping_avg_ms


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
