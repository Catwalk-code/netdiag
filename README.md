# NetDiag (Windows, Python, Kivy)

NetDiag — desktop-утилита для базовой диагностики сетевых соединений в ОС Windows.  
Проект разработан в рамках курсовой работы по теме:
**«Разработка утилиты диагностики сетевых соединений для ОС Windows на языке Python»**.

## Цель проекта

Предоставить простое GUI-приложение, которое:
- загружает список целей из `targets.json`;
- выполняет ping, DNS и TCP-проверки;
- показывает человекочитаемый результат в окне приложения;
- сохраняет отчёт только в текстовый файл (`.txt`).

## Архитектура модулей

- `/netdiag/config.py` — загрузка и валидация `targets.json`.
- `/netdiag/models.py` — Pydantic-модели конфигурации (`Defaults`, `Target`, `AppConfig`).
- `/netdiag/checks/ping.py` — запуск `ping` (Windows `-n`, `-w`), парсинг среднего времени.
- `/netdiag/checks/dns_check.py` — DNS-резолв `host -> IP`.
- `/netdiag/checks/tcp_ports.py` — проверка доступности TCP-портов.
- `/netdiag/checks/traceroute.py` — (опционально) запуск `tracert` с компактным выводом.
- `/netdiag/checks/orchestrator.py` — общий запуск всех проверок и сбор итогового текста.
- `/netdiag/ui/main.kv` — разметка Kivy-интерфейса.
- `/netdiag/ui/app.py` — логика GUI (запуск диагностики, сохранение отчёта, обработка ошибок).
- `/netdiag/report.py` — сохранение отчёта только в `.txt` в папку `reports/`.

## Требования и установка

- ОС: **Windows**
- Python: 3.11+ (рекомендуется 3.12)

Установка зависимостей:

```bash
pip install -r requirements.txt
```

## Запуск GUI

Из корня проекта:

```bash
python -m netdiag
```

После запуска:
1. Нажмите **«Запустить диагностику»**.
2. После получения результата нажмите **«Сохранить отчёт»**.
3. В окне будет показан путь к сохранённому файлу.

## Пример `targets.json`

```json
{
  "defaults": {
    "ping_count": 4,
    "ping_timeout_ms": 1000,
    "tcp_timeout_ms": 800,
    "ports": [80, 443],
    "dns_servers": ["1.1.1.1", "8.8.8.8"]
  },
  "targets": [
    { "name": "Router", "host": "192.168.1.1", "ports": [80] },
    { "name": "Google DNS", "host": "8.8.8.8", "ports": [53, 443] },
    { "name": "GitHub", "host": "github.com", "ports": [80, 443] }
  ]
}
```

## Пример отчёта `.txt`

```text
[Router]
host: 192.168.1.1
ports: [80]
ping: OK, avg=2 ms
dns: OK (IP: 192.168.1.1)
tcp: FAIL (open: [80], closed: [])
----------------------------------------
```

Файлы отчётов сохраняются в папку `reports/` и имеют формат:
`netdiag_report_YYYYMMDD_HHMMSS.txt`

## Ограничения

- Утилита ориентирована **только на Windows**.
- Логика `ping`/`tracert` использует Windows-утилиты и их ключи.
- Формат сохранения отчёта — **только `.txt`**.
