"""A QPlainTextEdit Widget linked to stream_loggers.

Write log messages color formatted to the given ui

# get loggers
log = get_stream_log('MyToolLog')
log_ext = get_stream_log('ExternalLog')

# create the log widget
self.loggers = QtUILogger(self, self.ui.log_layout, [log, log_ext])

log.hint('Message')

"""

from __future__ import annotations

import contextlib
import copy
import html
import logging
import threading
from collections import deque
from collections.abc import Sequence

from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QLayout, QPlainTextEdit, QWidget

from qt_log.stream_log import COLORS

_DISPLAY_BATCH_SIZE = 128
_MAX_PENDING_RECORDS = 4096


def _record_to_html(record: logging.LogRecord, formatter: logging.Formatter) -> str:
    color = COLORS.get(record.levelno, 'white')
    formatted_message = formatter.format(copy.copy(record))
    return f'<font color = "{color}" > {html.escape(formatted_message)} </font>'


class _LogDisplayBridge(QObject):
    display_requested = Signal()

    def __init__(self, widget: QPlainTextEdit) -> None:
        super().__init__(widget)
        self._widget = widget
        self._active = True
        self._delivery_scheduled = False
        self._dropped_records = 0
        self._peak_pending_records = 0
        self._pending_records: deque[str] = deque()
        self._lock = threading.Lock()
        self.display_requested.connect(
            self._deliver_pending,
            Qt.ConnectionType.QueuedConnection,
        )

    def display(self, rendered_record: str) -> None:
        should_schedule = False
        with self._lock:
            if not self._active:
                return
            if len(self._pending_records) >= _MAX_PENDING_RECORDS:
                self._pending_records.popleft()
                self._dropped_records += 1
            self._pending_records.append(rendered_record)
            self._peak_pending_records = max(
                self._peak_pending_records,
                len(self._pending_records),
            )
            if not self._delivery_scheduled:
                self._delivery_scheduled = True
                should_schedule = True

        if should_schedule:
            with contextlib.suppress(RuntimeError):
                self.display_requested.emit()

    @property
    def dropped_records(self) -> int:
        with self._lock:
            return self._dropped_records

    @property
    def peak_pending_records(self) -> int:
        with self._lock:
            return self._peak_pending_records

    @Slot()
    def _deliver_pending(self) -> None:
        with self._lock:
            if not self._active:
                self._pending_records.clear()
                self._delivery_scheduled = False
                return
            batch = [
                self._pending_records.popleft()
                for _ in range(min(_DISPLAY_BATCH_SIZE, len(self._pending_records)))
            ]

        for rendered_record in batch:
            with contextlib.suppress(RuntimeError):
                self._widget.appendHtml(rendered_record)

        should_schedule = False
        with self._lock:
            if not self._active:
                self._pending_records.clear()
                self._delivery_scheduled = False
            elif self._pending_records:
                should_schedule = True
            else:
                self._delivery_scheduled = False

        if should_schedule:
            with contextlib.suppress(RuntimeError):
                self.display_requested.emit()

    def close(self) -> None:
        with self._lock:
            self._active = False
            self._pending_records.clear()
            self._delivery_scheduled = False
        with contextlib.suppress(RuntimeError):
            self.display_requested.disconnect(self._deliver_pending)


class QtUILogger(logging.Handler):
    def __init__(
        self,
        parent: QWidget,
        layout_widget: QLayout,
        loggers: Sequence[logging.Logger],
    ) -> None:
        """Creates a log widget and parent the loggers to the layout widget provided.

        Args:
            parent: Parent widget that owns the log display.
            layout_widget: Layout that receives the log display.
            loggers: Loggers whose records should appear in the display.

        Raises:
            RuntimeError: If no QApplication exists or construction is off the GUI thread.
            TypeError: If parent, layout_widget, or a logger has an invalid type.
        """
        application = QApplication.instance()
        if not isinstance(application, QApplication):
            raise RuntimeError('QtUILogger requires an active QApplication')
        if QThread.currentThread() is not application.thread():
            raise RuntimeError('QtUILogger must be created on the Qt GUI thread')
        if not isinstance(parent, QWidget):
            raise TypeError('parent must be a QWidget')
        if not isinstance(layout_widget, QLayout):
            raise TypeError('layout_widget must be a QLayout')
        if not isinstance(loggers, Sequence) or isinstance(loggers, (str, bytes)):
            raise TypeError('loggers must be a sequence of logging.Logger instances')

        validated_loggers: list[logging.Logger] = []
        logger_ids: set[int] = set()
        for index, logger in enumerate(loggers):
            if not isinstance(logger, logging.Logger):
                raise TypeError(f'loggers[{index}] must be a logging.Logger')
            if id(logger) not in logger_ids:
                validated_loggers.append(logger)
                logger_ids.add(id(logger))

        super().__init__()

        # create output display widget, attach it to the layout widget
        self.widget = QPlainTextEdit(parent)
        layout_widget.addWidget(self.widget)

        # set font, css, message format
        font = QFont('Courier New')
        self.widget.setFont(font)
        self.widget.setStyleSheet(
            """
                border: 3px solid rgb(80, 80, 80);
                color: rgb(255, 255, 255);
                background-color: rgb(20, 20, 20);
                """
        )
        self.widget.setReadOnly(True)
        self.setFormatter(logging.Formatter('%(levelname)-7s | %(message)s'))
        self._display_bridge = _LogDisplayBridge(self.widget)

        # add loggers handlers to the widget
        self.loggers = validated_loggers
        for logger in self.loggers:
            logger.addHandler(self)

    def close(self) -> None:
        """Removes all handlers from this widget."""
        display_bridge = getattr(self, '_display_bridge', None)
        if display_bridge is not None:
            display_bridge.close()
        for logger in self.loggers:
            logger.removeHandler(self)
        self.loggers.clear()
        super().close()

    @property
    def dropped_records(self) -> int:
        """Returns the number of pending records discarded during overflow."""
        return self._display_bridge.dropped_records

    @property
    def peak_pending_records(self) -> int:
        """Returns the highest number of records waiting for display."""
        return self._display_bridge.peak_pending_records

    def emit(self, record: logging.LogRecord) -> None:
        """Writes the message formatted, uses font color based on error level number.

        Args:
            record: (logger record)
        """
        formatter = self.formatter
        assert formatter is not None
        rendered_record = _record_to_html(record, formatter)
        self._display_bridge.display(rendered_record)

    def clear(self) -> None:
        """Clears widget text."""
        self.widget.clear()
