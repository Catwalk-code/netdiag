"""Загрузка и валидация конфигурации NetDiag."""

import json
from pathlib import Path

from pydantic import ValidationError

from netdiag.models import AppConfig


def _format_validation_error(exc):
    """Преобразует ошибки Pydantic в понятный для пользователя текст."""
    lines: list[str] = []
    for err in exc.errors():
        location = " -> ".join(str(item) for item in err.get("loc", []))
        message = err.get("msg", "Неизвестная ошибка валидации.")
        lines.append(f"- {location}: {message}")
    return "\n".join(lines)


def load_config(path="targets.json"):
    """Надёжно загружает targets.json и возвращает валидированный AppConfig."""
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")

    try:
        raw_data = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise OSError(f"Не удалось прочитать файл конфигурации: {config_path}") from exc

    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Некорректный JSON в {config_path} (строка {exc.lineno}, столбец {exc.colno}): {exc.msg}"
        ) from exc

    try:
        return AppConfig.model_validate(data)
    except ValidationError as exc:
        details = _format_validation_error(exc)
        raise ValueError(f"Ошибка валидации конфигурации {config_path}:\n{details}") from exc
