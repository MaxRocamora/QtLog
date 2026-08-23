"""Standalone PySide6 application demonstrating QtLog without a DCC host."""

from __future__ import annotations

import random
import sys
from typing import TYPE_CHECKING

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from qt_log.qt_ui_logger import QtUILogger
from qt_log.stream_log import get_stream_logger

if TYPE_CHECKING:
    from qt_log.stream_log import StreamLogger


class StandaloneLogWindow(QMainWindow):
    """Small host-neutral window for exercising QtLog."""

    def __init__(self) -> None:
        """Create the example controls and attach a UI logger."""
        super().__init__()
        self.setWindowTitle('QtLog Standalone Example')
        self.resize(640, 360)

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        button_layout = QHBoxLayout()
        write_button = QPushButton('Write messages', central_widget)
        self.stream_button = QPushButton('Stream messages', central_widget)
        clear_button = QPushButton('Clear', central_widget)
        close_button = QPushButton('Close', central_widget)
        button_layout.addWidget(write_button)
        button_layout.addWidget(self.stream_button)
        button_layout.addWidget(clear_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        self.setCentralWidget(central_widget)

        self.logger: StreamLogger = get_stream_logger('QtLogStandalone')
        self.log_handler = QtUILogger(self, layout, [self.logger])

        write_button.clicked.connect(self.show_messages)
        self.stream_button.clicked.connect(self.stream_messages)
        clear_button.clicked.connect(self.log_handler.clear)
        close_button.clicked.connect(self.close)

    def show_messages(self) -> None:
        """Write representative records to the stream and UI handlers."""
        self.logger.info('QtLog standalone example')
        self.logger.warning('Messages may originate from worker threads')
        self.logger.done('Messages delivered on the Qt GUI thread')

    def stream_messages(self) -> None:
        """Write a burst of 500 randomly leveled messages."""
        log_methods = (
            self.logger.debug,
            self.logger.info,
            self.logger.warning,
            self.logger.error,
            self.logger.critical,
            self.logger.done,
            self.logger.hint,
            self.logger.ok,
            self.logger.process,
            self.logger.file,
        )
        for index in range(1, 501):
            random.choice(log_methods)('Stream message %03d/500', index)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Detach the UI handler before the window is destroyed."""
        self.log_handler.close()
        super().closeEvent(event)


def main() -> int:
    """Run the standalone QtLog example."""
    application = QApplication.instance() or QApplication(sys.argv)
    window = StandaloneLogWindow()
    window.show()
    return application.exec()


if __name__ == '__main__':
    raise SystemExit(main())
