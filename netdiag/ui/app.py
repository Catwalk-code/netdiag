from kivy.app import App
from kivy.lang import Builder
from kivy_garden.graph import BarPlot
from pathlib import Path

from netdiag.ui.plot_data import parse_target_checks

EMPTY_GRAPH_X_RANGE = (0, 1)
EMPTY_GRAPH_Y_RANGE = (0, 100)
GROUP_X_MARGIN = 0.5
MIN_GRAPH_Y_MAX = 10
GRAPH_Y_TOP_MARGIN = 10
BAR_WIDTH = 0.18
BAR_SPACING = 0.25
GRAPH_PING_COLOR = [0.3, 0.8, 1, 1]
GRAPH_DNS_COLOR = [0.4, 0.9, 0.4, 1]
GRAPH_TCP_COLOR = [1, 0.7, 0.2, 1]


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

        if self.root:
            axis_targets_label = self.root.ids.get("ping_axis_targets")
            if axis_targets_label is not None:
                axis_targets_label.text = ""
            legend_label = self.root.ids.get("ping_legend")
            if legend_label is not None:
                legend_label.text = ""

    def update_ping_graph(self, report_text):
        """Обновляет график ping средними значениями по целям."""
        graph = self.root.ids.get("ping_graph") if self.root else None
        if graph is None:
            return

        targets = parse_target_checks(report_text)
        target_names = [target.name for target in targets]
        point_count = len(targets)
        if point_count == 0:
            graph.xmin, graph.xmax = EMPTY_GRAPH_X_RANGE
            graph.ymin, graph.ymax = EMPTY_GRAPH_Y_RANGE
            return

        graph.xmin, graph.xmax = -GROUP_X_MARGIN, point_count - 1 + GROUP_X_MARGIN
        graph.ymin = 0
        series = [
            ("ping_avg_ms", GRAPH_PING_COLOR, lambda value: value),
            ("dns_ok", GRAPH_DNS_COLOR, lambda value: 1 if value else 0),
            ("tcp_ok", GRAPH_TCP_COLOR, lambda value: 1 if value else 0),
        ]
        offsets = [
            (index - (len(series) - 1) / 2) * BAR_SPACING
            for index in range(len(series))
        ]
        all_values: list[int] = []
        for (attr_name, color, transform), offset in zip(series, offsets, strict=True):
            plot = BarPlot(color=color, bar_width=BAR_WIDTH)
            points = []
            for index, target in enumerate(targets):
                raw_value = getattr(target, attr_name)
                if raw_value is None:
                    continue
                value = transform(raw_value)
                points.append((index + offset, value))
                all_values.append(value)
            if points:
                plot.points = points
                graph.add_plot(plot)

        if not all_values:
            graph.xmin, graph.xmax = EMPTY_GRAPH_X_RANGE
            graph.ymin, graph.ymax = EMPTY_GRAPH_Y_RANGE
            return
        graph.ymax = max(MIN_GRAPH_Y_MAX, max(all_values) + GRAPH_Y_TOP_MARGIN)

        axis_targets_label = self.root.ids.get("ping_axis_targets") if self.root else None
        if axis_targets_label is not None:
            axis_targets_label.text = " | ".join(target_names)

        legend_label = self.root.ids.get("ping_legend") if self.root else None
        if legend_label is not None:
            legend_lines = ["Пояснение: DNS/TCP — 1 = OK, 0 = FAIL (значение столбца)"]
            for target in targets:
                ping_text = (
                    f"{target.ping_avg_ms} ms" if target.ping_avg_ms is not None else "н/д"
                )
                dns_text = (
                    "OK"
                    if target.dns_ok is True
                    else "FAIL"
                    if target.dns_ok is False
                    else "н/д"
                )
                tcp_text = (
                    "OK"
                    if target.tcp_ok is True
                    else "FAIL"
                    if target.tcp_ok is False
                    else "н/д"
                )
                legend_lines.append(
                    f"{target.name}: ping={ping_text}, dns={dns_text}, tcp={tcp_text}"
                )
            legend_label.text = "\n".join(legend_lines)

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
