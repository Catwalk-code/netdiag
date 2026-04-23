"""Pydantic-модели конфигурации NetDiag."""

from pydantic import BaseModel, Field, field_validator


def _validate_port_list(ports):
    """Проверяет, что список портов содержит значения от 1 до 65535."""
    for port in ports:
        if not (1 <= port <= 65535):
            raise ValueError(f"Некорректный порт: {port}. Допустим диапазон 1..65535.")
    return ports


class Defaults(BaseModel):
    """Глобальные настройки диагностики по умолчанию."""

    ping_count: int = Field(default=4, description="Количество ping-запросов")
    ping_timeout_ms: int = Field(default=1000, description="Таймаут ping в миллисекундах")
    tcp_timeout_ms: int = Field(default=800, description="Таймаут TCP-подключения в миллисекундах")
    ports: list[int] = Field(default_factory=lambda: [80, 443], description="Порты для TCP-проверки")
    dns_servers: list[str] = Field(default_factory=lambda: ["1.1.1.1", "8.8.8.8"], description="DNS-серверы")

    @field_validator("ping_count")
    @classmethod
    def validate_ping_count(cls, value):
        """Проверяет, что число ping-запросов больше нуля."""
        if value <= 0:
            raise ValueError("Количество ping-запросов должно быть больше 0.")
        return value

    @field_validator("ping_timeout_ms", "tcp_timeout_ms")
    @classmethod
    def validate_timeouts(cls, value):
        """Проверяет, что таймауты больше нуля."""
        if value <= 0:
            raise ValueError("Таймаут должен быть больше 0.")
        return value

    @field_validator("ports")
    @classmethod
    def validate_ports(cls, value):
        """Проверяет корректность списка портов по умолчанию."""
        return _validate_port_list(value)


class Target(BaseModel):
    """Описание одной диагностируемой цели."""

    name: str
    host: str
    # Если список портов не задан, будут взяты defaults.ports.
    ports: list[int] | None = None

    @field_validator("name", "host")
    @classmethod
    def validate_required_text(cls, value):
        """Проверяет, что строковые поля цели не пустые."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Поле не может быть пустым.")
        return cleaned

    @field_validator("ports")
    @classmethod
    def validate_target_ports(cls, value):
        """Проверяет корректность пользовательского списка портов цели."""
        if value is None:
            return None
        return _validate_port_list(value)


class AppConfig(BaseModel):
    """Корневая модель файла targets.json."""

    defaults: Defaults
    targets: list[Target]

    @field_validator("targets")
    @classmethod
    def validate_targets(cls, value):
        """Проверяет, что в конфиге есть хотя бы одна цель."""
        if not value:
            raise ValueError("Список целей не может быть пустым.")
        return value
