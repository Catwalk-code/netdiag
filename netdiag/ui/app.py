from datetime import datetime
import math
from pathlib import Path
from random import Random
import sys

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy_garden.graph import BarPlot

from netdiag.checks.orchestrator import run_all_checks
from netdiag.checks.ping import run_ping_check
from netdiag.config import load_config
from netdiag.report import save_report

DEFAULT_CONFIG_PATH = "targets.json"


def _get_config_path():
    """Возвращает путь к targets.json: рядом с exe или в рабочей директории"""
    if getattr(sys, 'frozen', False):
        # Запущен как скомпилированный exe
        base_path = Path(sys.executable).parent
    else:
        # Запущен как скрипт
        base_path = Path.cwd()

    config_path = base_path / DEFAULT_CONFIG_PATH
    return str(config_path)


PING_INTERVAL_SECONDS = 1.0
EMPTY_GRAPH_YMIN = 0.0
EMPTY_GRAPH_YMAX = 100.0
MIN_Y_MARGIN = 5.0
MIN_Y_RANGE = 5.0
MIN_TICK_STEP = 0.1
MIN_BAR_SPACING = 0.05
MAX_BAR_SPACING = 0.6
MAX_SPACING_TARGET_COUNT = 12
LATENCY_GREEN_THRESHOLD = 50
LATENCY_YELLOW_THRESHOLD = 150
INACTIVE_BAR_COLOR = [0.4, 0.4, 0.4, 0.7]
GREEN_BAR_COLOR = [0.2, 0.8, 0.2, 1]
YELLOW_BAR_COLOR = [0.95, 0.8, 0.2, 1]
RED_BAR_COLOR = [0.9, 0.25, 0.25, 1]


class NetDiagApp(App):
    """Приложение мониторинга сетевой задержки в реальном времени"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._bar_plots = []
        self._slot_values = []
        self._history = []
        self._monitor_event = None
        self._rng = Random()
        self._targets = []
        self._target_names = []
        self._target_count = 0
        self._bar_spacing = MIN_BAR_SPACING
        self._defaults = None

    def build(self):
        kv_path = Path(__file__).parent / "main.kv"
        return Builder.load_file(str(kv_path))

    def on_start(self):
        config_path = _get_config_path()
        try:
            self._load_targets(config_path)
        except Exception as exc:
            self.root.ids.output_box.text = f"Ошибка загрузки {config_path}: {exc}"
            self.root.ids.ping_legend.text = "Цели для диагностики не загружены."
            return

        self._initialize_graph()
        self._render_target_indices()
        self._refresh_graph()
        self.root.ids.output_box.text = "Нажмите «Старт мониторинга», чтобы начать сбор ping по целям."

    def on_stop(self):
        self.stop_monitoring()

    def start_monitoring(self):
        if self._monitor_event is not None:
            self.root.ids.output_box.text = "Мониторинг уже запущен."
            return

        if not self._targets:
            config_path = _get_config_path()
            self.root.ids.output_box.text = f"Цели диагностики не загружены. Проверьте {config_path}."
            return

        self._slot_values = [None] * self._target_count
        self._history.clear()
        self._refresh_graph()
        self._monitor_event = Clock.schedule_interval(self._collect_ping_sample, PING_INTERVAL_SECONDS)
        self.root.ids.output_box.text = "Мониторинг запущен. Данные обновляются каждую секунду."

    def stop_monitoring(self):
        if self._monitor_event is None:
            return
        self._monitor_event.cancel()
        self._monitor_event = None
        config_path = _get_config_path()
        try:
            report_text = run_all_checks(config_path)
        except Exception as exc:
            self.root.ids.output_box.text = f"Мониторинг остановлен. Ошибка диагностики: {exc}"
            return
        self.root.ids.output_box.text = report_text

    def reload_targets(self):
        """Перезагружает цели и пересоздает график с новым количеством столбцов."""
        self.stop_monitoring()
        config_path = _get_config_path()
        try:
            self._load_targets(config_path)
        except Exception as exc:
            self.root.ids.output_box.text = f"Ошибка перезагрузки целей: {exc}"
            return

        self._initialize_graph()
        self._render_target_indices()
        self._refresh_graph()
        self.root.ids.output_box.text = f"Цели перезагружены. Найдено {self._target_count} целей."

    def _initialize_graph(self):
        graph = self.root.ids.ping_graph
        graph.xmin = -0.5
        graph.xmax = max(self._target_count - 0.5, 0.5)
        graph.ymin = EMPTY_GRAPH_YMIN
        graph.ymax = EMPTY_GRAPH_YMAX
        graph.y_ticks_major = 10
        graph.x_ticks_major = 1

        for plot in list(graph.plots):
            graph.remove_plot(plot)

        self._bar_plots = []
        self._bar_spacing = self._bar_spacing_for_count(self._target_count)
        for x in range(self._target_count):
            plot = BarPlot(color=INACTIVE_BAR_COLOR, bar_spacing=self._bar_spacing)
            plot.points = [(x, 0)]
            graph.add_plot(plot)
            plot.bind_to_graph(graph)
            self._bar_plots.append(plot)

    def _collect_ping_sample(self, _dt):
        values = []
        defaults = self._defaults
        ping_count = defaults.ping_count if defaults else 4
        ping_timeout_ms = defaults.ping_timeout_ms if defaults else 1000

        for target in self._targets:
            try:
                result = run_ping_check(
                    host=target.host,
                    count=ping_count,
                    timeout_ms=ping_timeout_ms,
                )
            except Exception:
                values.append(None)
                continue

            if result.get("ok") and result.get("avg_ms") is not None:
                values.append(result.get("avg_ms"))
            else:
                values.append(None)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self._slot_values = values
        self._history.append((timestamp, list(values)))

        self._refresh_graph()

    def _refresh_graph(self):
        graph = self.root.ids.ping_graph
        values = [value for value in self._slot_values if value is not None]

        if values:
            y_min = float(min(values))
            y_margin = max(MIN_Y_MARGIN, max(values) * 0.2)
            y_max = float(max(values) + y_margin)
            if y_max <= y_min:
                y_max = y_min + MIN_Y_RANGE
            graph.ymin = y_min
            graph.ymax = y_max
            graph.y_ticks_major = self._nice_tick((y_max - y_min) / 5)
        else:
            graph.ymin = EMPTY_GRAPH_YMIN
            graph.ymax = EMPTY_GRAPH_YMAX
            graph.y_ticks_major = 10

        baseline = graph.ymin
        for index, plot in enumerate(self._bar_plots):
            value = self._slot_values[index] if index < len(self._slot_values) else None
            if value is None:
                plot.points = [(index, baseline)]
                plot.color = INACTIVE_BAR_COLOR
                continue

            plot.points = [(index, value)]
            plot.color = self._latency_color(value)

        self.root.ids.ping_legend.text = self._build_target_summary()

    def save_report(self):
        if not self._history:
            self.root.ids.output_box.text = "Нет данных для отчёта. Сначала запустите мониторинг."
            return

        report_text = self._build_session_report()
        report_path = save_report(report_text)
        self.root.ids.output_box.text = f"Отчёт сохранён: {report_path}"

    def _build_session_report(self):
        header = ["Сеанс мониторинга ping", "======================", ""]
        if self._target_names:
            targets_line = " | ".join(
                f"{index}) {name}" for index, name in enumerate(self._target_names, start=1)
            )
            header.extend([f"Цели: {targets_line}", ""])
        rows = [
            f"{timestamp} | {' | '.join(self._format_latency(value) for value in values)}"
            for timestamp, values in self._history
        ]
        report_lines = header + rows
        diagnostics = self._build_diagnostics_section()
        if diagnostics:
            report_lines.append("")
            report_lines.extend(diagnostics)
        return "\n".join(report_lines)

    def _build_diagnostics_section(self):
        config_path = _get_config_path()
        try:
            diagnostics_text = run_all_checks(config_path)
        except Exception as exc:
            return [f"Ошибка диагностики: {exc}"]
        return diagnostics_text.splitlines()

    @staticmethod
    def _latency_color(value):
        if value < LATENCY_GREEN_THRESHOLD:
            return GREEN_BAR_COLOR
        if value <= LATENCY_YELLOW_THRESHOLD:
            return YELLOW_BAR_COLOR
        return RED_BAR_COLOR

    @staticmethod
    def _nice_tick(raw_step):
        if raw_step <= 0:
            return MIN_TICK_STEP

        magnitude = 10 ** math.floor(math.log10(raw_step))
        normalized = raw_step / magnitude
        if normalized <= 1:
            nice = 1
        elif normalized <= 2:
            nice = 2
        elif normalized <= 5:
            nice = 5
        else:
            nice = 10
        return max(MIN_TICK_STEP, nice * magnitude)

    def _load_targets(self, config_path=None):
        if config_path is None:
            config_path = _get_config_path()
        config = load_config(config_path)
        self._targets = list(config.targets)
        self._target_names = [target.name for target in self._targets]
        self._target_count = len(self._targets)
        self._slot_values = [None] * self._target_count
        self._bar_spacing = self._bar_spacing_for_count(self._target_count)
        self._defaults = config.defaults

    def _render_target_indices(self):
        indices_layout = self.root.ids.target_indices
        indices_layout.clear_widgets()
        if not self._target_names:
            indices_layout.cols = 1
            return

        indices_layout.cols = self._target_count
        for index in range(1, self._target_count + 1):
            label = Label(text=str(index), halign="center", valign="middle")
            label.bind(size=label.setter("text_size"))
            # Добавляем небольшой отступ для центрирования над столбцом
            label.padding = (dp(2), dp(2))
            indices_layout.add_widget(label)

    def _build_target_summary(self):
        if not self._target_names:
            return "Цели для диагностики не загружены."

        entries = []
        for index, name in enumerate(self._target_names, start=1):
            value = self._slot_values[index - 1] if index - 1 < len(self._slot_values) else None
            entries.append(f"{index}) {name} ({self._format_latency(value)})")
        return f"Пинг (мс): {' | '.join(entries)}"

    @staticmethod
    def _format_latency(value):
        if value is None:
            return "н/д"
        return f"{value} мс"

    @staticmethod
    def _bar_spacing_for_count(count):
        if count <= 0:
            return MIN_BAR_SPACING
        if count == 1:
            return MIN_BAR_SPACING
        normalized = min(1.0, (count - 1) / (MAX_SPACING_TARGET_COUNT - 1))
        spacing = MIN_BAR_SPACING + (MAX_BAR_SPACING - MIN_BAR_SPACING) * normalized
        return max(MIN_BAR_SPACING, min(MAX_BAR_SPACING, spacing))
