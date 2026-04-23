import json

import pytest

from netdiag.config import load_config


def test_load_config_success(tmp_path):
    config_path = tmp_path / "targets.json"
    config_path.write_text(
        json.dumps(
            {
                "defaults": {
                    "ping_count": 4,
                    "ping_timeout_ms": 1000,
                    "tcp_timeout_ms": 800,
                    "ports": [80, 443],
                    "dns_servers": ["1.1.1.1", "8.8.8.8"],
                },
                "targets": [
                    {"name": "Google", "host": "google.com", "ports": [80, 443]},
                ],
            }
        ),
        encoding="utf-8",
    )

    config = load_config(str(config_path))
    assert config.targets[0].name == "Google"


def test_load_config_invalid_port(tmp_path):
    config_path = tmp_path / "targets.json"
    config_path.write_text(
        json.dumps(
            {
                "defaults": {
                    "ping_count": 4,
                    "ping_timeout_ms": 1000,
                    "tcp_timeout_ms": 800,
                    "ports": [70000],
                    "dns_servers": ["1.1.1.1"],
                },
                "targets": [{"name": "Bad", "host": "localhost"}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Ошибка валидации конфигурации"):
        load_config(str(config_path))
