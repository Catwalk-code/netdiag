from kivy.app import App
from kivy.lang import Builder
from pathlib import Path


class NetDiagApp(App):
    """Главное Kivy-приложение NetDiag."""

    def __init__(self, **kwargs):
        """Инициализирует состояние приложения."""
        super().__init__(**kwargs)
        self.last_report_text = ""

    def build(self):
        """Загружает интерфейс из kv-файла."""
        kv_path = Path(__file__).parent / "main.kv"
        return Builder.load_file(str(kv_path))

    def run_diagnostics(self):
        """Запускает диагностику и выводит результат в интерфейс."""
        try:
            from netdiag.checks.orchestrator import run_all_checks

            result = run_all_checks("targets.json")
            self.last_report_text = result
            self.root.ids.output_box.text = result or "Диагностика завершена, но данных нет."
        except Exception as e:
            self.root.ids.output_box.text = f"Ошибка: {e}"

    def save_report(self):
        """Сохраняет последний отчёт в TXT и показывает путь к файлу."""
        if not self.last_report_text.strip():
            self.root.ids.output_box.text = "Нет отчёта для сохранения. Сначала запустите диагностику."
            return

        try:
            from netdiag.report import save_report

            report_path = save_report(self.last_report_text)
            self.root.ids.output_box.text = f"{self.last_report_text}\n\nОтчёт сохранён: {report_path}"
        except Exception as e:
            self.root.ids.output_box.text = f"Ошибка сохранения отчёта: {e}"
