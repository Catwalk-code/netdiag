from __future__ import annotations

from datetime import datetime
import math
from pathlib import Path
from random import Random

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy_garden.graph import BarPlot

from netdiag.report import save_report

SLOT_COUNT = 24
PING_INTERVAL_SECONDS = 1.0
BAR_SPACING = 0.4
EMPTY_GRAPH_YMIN = 0.0
EMPTY_GRAPH_YMAX = 100.0
MIN_Y_MARGIN = 5.0
MIN_Y_RANGE = 5.0
MIN_TICK_STEP = 0.1
LATENCY_GREEN_THRESHOLD = 50
LATENCY_YELLOW_THRESHOLD = 150
INACTIVE_BAR_COLOR = [0.4, 0.4, 0.4, 0.7]
GREEN_BAR_COLOR = [0.2, 0.8, 0.2, 1]
YELLOW_BAR_COLOR = [0.95, 0.8, 0.2, 1]
RED_BAR_COLOR = [0.9, 0.25, 0.25, 1]


class NetDiagApp(App):
    """Приложение мониторинга сетевой задержки в реальном времени."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._bar_plots: list[BarPlot] = []
        self._slot_values: list[int | None] = [None] * SLOT_COUNT
        self._history: list[tuple[str, int]] = []
        self._next_slot = 0
        self._monitor_event = None
        self._rng = Random()

    def build(self):
        kv_path = Path(__file__).parent / "main.kv"
        return Builder.load_file(str(kv_path))

    def on_start(self):
        self._initialize_graph()
        self.root.ids.output_box.text = "Нажмите «Старт мониторинга», чтобы начать сбор ping каждые 1 сек."

    def on_stop(self):
        self.stop_monitoring()

    def run_diagnostics(self):
        """Совместимость со старой кнопкой: запускает мониторинг."""
        self.start_monitoring()

    def start_monitoring(self):
        if self._monitor_event is not None:
            self.root.ids.output_box.text = "Мониторинг уже запущен."
            return

        self._slot_values = [None] * SLOT_COUNT
        self._history.clear()
        self._next_slot = 0
        self._refresh_graph()
        self._monitor_event = Clock.schedule_interval(self._collect_ping_sample, PING_INTERVAL_SECONDS)
        self.root.ids.output_box.text = "Мониторинг запущен. Данные обновляются каждую секунду."

    def stop_monitoring(self):
        if self._monitor_event is None:
            return
        self._monitor_event.cancel()
        self._monitor_event = None
        self.root.ids.output_box.text = "Мониторинг остановлен."

    def _initialize_graph(self):
        graph = self.root.ids.ping_graph
        graph.xmin = -0.5
        graph.xmax = SLOT_COUNT - 0.5
        graph.ymin = EMPTY_GRAPH_YMIN
        graph.ymax = EMPTY_GRAPH_YMAX
        graph.y_ticks_major = 10

        for plot in list(graph.plots):
            graph.remove_plot(plot)

        self._bar_plots = []
        for x in range(SLOT_COUNT):
            plot = BarPlot(color=INACTIVE_BAR_COLOR, bar_spacing=BAR_SPACING)
            plot.points = [(x, 0)]
            graph.add_plot(plot)
            plot.bind_to_graph(graph)
            self._bar_plots.append(plot)

    def _collect_ping_sample(self, _dt):
        latency_ms = self._simulate_ping_ms()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self._slot_values[self._next_slot] = latency_ms
        self._next_slot = (self._next_slot + 1) % SLOT_COUNT
        self._history.append((timestamp, latency_ms))

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
            value = self._slot_values[index]
            if value is None:
                plot.points = [(index, baseline)]
                plot.color = INACTIVE_BAR_COLOR
                continue

            plot.points = [(index, value)]
            plot.color = self._latency_color(value)

        if self._history:
            last_timestamp, last_value = self._history[-1]
            self.root.ids.ping_legend.text = (
                f"Последний замер: {last_value} мс в {last_timestamp}. "
                f"Всего замеров: {len(self._history)}"
            )
        else:
            self.root.ids.ping_legend.text = "Ожидание данных ping..."

    def save_report(self):
        if not self._history:
            self.root.ids.output_box.text = "Нет данных для отчёта. Сначала запустите мониторинг."
            return

        report_text = self._build_session_report()
        report_path = save_report(report_text)
        self.root.ids.output_box.text = f"Отчёт сохранён: {report_path}"

    def _build_session_report(self):
        header = ["Сеанс мониторинга ping", "======================", ""]
        rows = [f"{timestamp} | {latency} ms" for timestamp, latency in self._history]
        return "\n".join(header + rows)

    def _simulate_ping_ms(self):
        base = self._rng.randint(18, 60)
        if self._rng.random() < 0.15:
            return base + self._rng.randint(60, 120)
        if self._rng.random() < 0.05:
            return base + self._rng.randint(160, 260)
        return base

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
            return 1

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
