from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import statistics
import threading
from dataclasses import asdict, dataclass
from time import perf_counter

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6 import __version__ as pyside_version
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from qt_log.qt_ui_logger import QtUILogger, _record_to_html


@dataclass(frozen=True)
class FormattingResult:
    records: int
    seconds: float
    records_per_second: float


@dataclass(frozen=True)
class DeliveryResult:
    mode: str
    records: int
    delivered: int
    seconds: float
    records_per_second: float
    median_latency_ms: float
    p95_latency_ms: float
    maximum_latency_ms: float
    peak_pending_records: int
    dropped_records: int
    ordered: bool


def _record(index: int) -> logging.LogRecord:
    return logging.LogRecord(
        name='qtlog_benchmark',
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='record %d <benchmark>',
        args=(index,),
        exc_info=None,
    )


def benchmark_formatting(records: int) -> FormattingResult:
    """Measure pure record formatting throughput."""
    formatter = logging.Formatter('%(levelname)-7s | %(message)s')
    record = _record(1)
    started = perf_counter()
    for _ in range(records):
        _record_to_html(record, formatter)
    seconds = perf_counter() - started
    return FormattingResult(records, seconds, records / seconds)


def _percentile(values: list[float], percentile: float) -> float:
    ordered_values = sorted(values)
    index = min(len(ordered_values) - 1, int(len(ordered_values) * percentile))
    return ordered_values[index]


def benchmark_delivery(records: int, *, concurrent: bool) -> DeliveryResult:
    """Measure ordered queued delivery into an offscreen Qt widget."""
    application = QApplication.instance() or QApplication([])
    parent = QWidget()
    layout = QVBoxLayout(parent)
    handler = QtUILogger(parent, layout, [])
    emission_times = [0.0] * records
    delivery_times: list[float] = []

    handler.widget.textChanged.connect(lambda: delivery_times.append(perf_counter()))

    def produce() -> None:
        for index in range(records):
            emission_times[index] = perf_counter()
            handler.emit(_record(index))

    started = perf_counter()
    worker = threading.Thread(target=produce)
    worker.start()
    if not concurrent:
        worker.join()

    deadline = started + 30.0
    while worker.is_alive() or len(delivery_times) < records - handler.dropped_records:
        application.processEvents()
        if perf_counter() >= deadline:
            raise TimeoutError(f'delivered {len(delivery_times)} of {records} records')
    worker.join()
    seconds = delivery_times[-1] - started

    latencies = [
        (delivered_at - emitted_at) * 1000
        for emitted_at, delivered_at in zip(emission_times, delivery_times, strict=True)
    ]
    expected_lines = [f'INFO | record {index} <benchmark> ' for index in range(records)]
    ordered = handler.widget.toPlainText().splitlines() == expected_lines
    result = DeliveryResult(
        mode='concurrent' if concurrent else 'burst',
        records=records,
        delivered=len(delivery_times),
        seconds=seconds,
        records_per_second=records / seconds,
        median_latency_ms=statistics.median(latencies),
        p95_latency_ms=_percentile(latencies, 0.95),
        maximum_latency_ms=max(latencies),
        peak_pending_records=handler.peak_pending_records,
        dropped_records=handler.dropped_records,
        ordered=ordered,
    )
    handler.close()
    parent.close()
    return result


def main() -> None:
    """Run the benchmark and print a JSON report."""
    parser = argparse.ArgumentParser(description='Benchmark QtLog formatting and Qt delivery.')
    parser.add_argument('--format-records', type=int, default=100_000)
    parser.add_argument('--delivery-records', type=int, default=2_000)
    args = parser.parse_args()

    report = {
        'environment': {
            'python': platform.python_version(),
            'pyside': pyside_version,
            'platform': platform.platform(),
            'processor': platform.processor(),
        },
        'formatting': asdict(benchmark_formatting(args.format_records)),
        'burst_delivery': asdict(benchmark_delivery(args.delivery_records, concurrent=False)),
        'concurrent_delivery': asdict(benchmark_delivery(args.delivery_records, concurrent=True)),
    }
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
