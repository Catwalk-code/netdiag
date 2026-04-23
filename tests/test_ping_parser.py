from netdiag.checks.ping import _parse_avg_ms


def test_parse_avg_ms_en_output():
    sample = "Minimum = 13ms, Maximum = 21ms, Average = 17ms"
    assert _parse_avg_ms(sample) == 17


def test_parse_avg_ms_ru_output():
    sample = "Минимальное = 13мс, Максимальное = 21мс, Среднее = 17мс"
    assert _parse_avg_ms(sample) == 17


def test_parse_avg_ms_not_found():
    assert _parse_avg_ms("Нет данных") is None
