from kivy.app import App
from kivy.lang import Builder
from kivy_garden.graph import MeshLinePlot
from pathlib import Path

from netdiag.ui.plot_data import parse_ping_avg_ms


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
            self.clear_plots()
            from netdiag.checks.orchestrator import run_all_checks

            result = run_all_checks("targets.json")
            self.last_report_text = result
            self.root.ids.output_box.text = result or "Диагностика завершена, но данных нет."
            self.update_ping_graph(result)
        except Exception as e:
            self.root.ids.output_box.text = f"Ошибка: {e}"

    def clear_plots(self):
        """Безопасно очищает график, если он присутствует в интерфейсе."""
        if not self.root:
            return

        graph = self.root.ids.get("graph")
        if graph is None:
            graph = self.root.ids.get("ping_graph")
        if graph is None:
            return

        plots = getattr(graph, "plots", None)
        if not plots:
            return

        for plot in list(plots):
            graph.remove_plot(plot)

    def update_ping_graph(self, report_text):
        """Обновляет график ping средними значениями по целям."""
        graph = self.root.ids.get("ping_graph") if self.root else None
        if graph is None:
            return

        values = parse_ping_avg_ms(report_text)
        point_count = len(values)
        if point_count == 0:
            graph.xmin, graph.xmax = 0, 1
            graph.ymin, graph.ymax = 0, 100
            return

        if point_count == 1:
            graph.xmin, graph.xmax = -0.5, 0.5
        else:
            graph.xmin, graph.xmax = 0, point_count - 1
        graph.ymin = 0
        graph.ymax = max(100, max(values) + 10)

        plot = MeshLinePlot(color=[0.3, 0.8, 1, 1])
        plot.points = [(index, value) for index, value in enumerate(values)]
        graph.add_plot(plot)

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
