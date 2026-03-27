from pydantic import BaseModel, Field, field_validator 
class Defaults(BaseModel):
    ping_count: int = Field(default=4, description="Количество пингов для каждого теста")
    ping_timeout_ms: int = Field(default=1000, description="Макс. время ответа на пинг в миллисекундах")
    tcp_timeout_ms: int = Field(default=800, description="Макс. время ответа на TCP-запрос в миллисекундах")
    ports: list[int] = Field(default_factory=lambda: [80, 443], description="Список портов для проверки TCP-соединения")
    dns_servers: list[str] = Field(default_factory=lambda: ["1.1.1.1", "8.8.8.8"], 
                                   description="Список DNS-серверов для проверки")

    @field_validator('ping_count')
    @classmethod
    def validate_ping_count(cls, value):
        if value < 1:
            raise ValueError('Количество пингов должно быть больше 0')
        return value
    
    @field_validator('ping_timeout_ms', 'tcp_timeout_ms')
    @classmethod
    def validate_timeouts(cls, value):
        if value <= 0:
            raise ValueError('Таймаут должен быть больше 0 мс')
        return value
    

    @field_validator("ports")
    @classmethod
    def validate_ports(cls, value: list[int]) -> list[int]:
        for port in value:
            if not (1 <= port <= 65535):
                raise ValueError(f"Некорректный порт: {port}")
        return value

class Target(BaseModel):
    name: str
    host: str
    ports: list[int] | None = None # Если у цели нет своих портов, возьмём порты из общих настроек в Defaults

    @field_validator('name', 'host')
    @classmethod
    def validate_target_fields(cls, value):
        if not value:
            raise ValueError('Поле не может быть пустым')
        return value
    
    @field_validator("ports")
    @classmethod
    def validate_target_ports(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return value
        for port in value:
            if not (1 <= port <= 65535):
                raise ValueError(f"Некорректный порт: {port}")
        return value

class AppConfig(BaseModel):
    defaults: Defaults
    targets: list[Target]

    @field_validator('targets')
    @classmethod
    def validate_targets(cls, value):
        if not value:
            raise ValueError('Список целей не может быть пустым')
        return value