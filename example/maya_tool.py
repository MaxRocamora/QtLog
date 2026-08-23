from __future__ import annotations

# ----------------------------------------------------------------------------------------
# Awesome Tool
# PySide6 example Qt Maya tool for showcasing QtLog
#
"""# Run in Maya (add qtlog to pythonpath first).

import example.main as qtlog_example
qtlog_example.load()

"""

# ----------------------------------------------------------------------------------------
import random
from importlib import import_module
from typing import cast

from PySide6 import QtCore
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from shiboken6 import wrapInstance

from qt_log.qt_ui_logger import QtUILogger
from qt_log.stream_log import get_stream_logger
from qt_log.version import app_name, version


def get_maya_main_window() -> QWidget | None:
    """Return Maya's wrapped main window when one exists."""
    omui = import_module('maya.OpenMayaUI')
    main_window_ptr = omui.MQtUtil.mainWindow()
    if main_window_ptr is None:
        return None
    return cast(QWidget, wrapInstance(int(main_window_ptr), QWidget))


# get the loggers
log = get_stream_logger('AwesomeLog')
log_b = get_stream_logger('AnotherLog')

QT_NAME = 'awesome_tool_window'


class AwesomeTool(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Main window for the Awesome Tool."""
        if parent is None:
            parent = get_maya_main_window()
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setObjectName(QT_NAME)
        self.setFixedSize(473, 276)
        self.setWindowTitle(app_name + ' ' + version)

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        log_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.btn_ok = QPushButton('OK', central_widget)
        self.stream_button = QPushButton('Stream messages', central_widget)
        self.btn_cancel = QPushButton('CANCEL', central_widget)
        button_layout.addWidget(self.btn_ok)
        button_layout.addWidget(self.stream_button)
        button_layout.addWidget(self.btn_cancel)
        layout.addLayout(log_layout)
        layout.addLayout(button_layout)
        self.setCentralWidget(central_widget)

        # creating/storing loggers
        self.loggers = QtUILogger(self, log_layout, [log, log_b])

        self.btn_ok.clicked.connect(self.show_messages)
        self.stream_button.clicked.connect(self.stream_messages)
        self.btn_cancel.clicked.connect(self.close)
        self.show()

    def show_messages(self) -> None:
        """Shows output messages."""
        log.ok(f'{app_name} - {version} is running')
        log.info('This is log.info')
        log.debug('This is log.debug')
        log.warning('This is log.warning')
        log.error('This is log.error')
        log.critical('This is log.critical')
        log.done('This is log.done')
        log.file('This is log.file')
        log.process('This is log.process')
        log.ok('This is log.ok')

    def stream_messages(self) -> None:
        """Write a burst of 500 randomly leveled messages."""
        log_methods = (
            log.debug,
            log.info,
            log.warning,
            log.error,
            log.critical,
            log.done,
            log.hint,
            log.ok,
            log.process,
            log.file,
        )
        for index in range(1, 501):
            random.choice(log_methods)('Stream message %03d/500', index)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Detach the UI logger before closing the window."""
        self.loggers.close()
        super().closeEvent(event)


# ----------------------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------------------


def load() -> AwesomeTool:
    """Loads the AwesomeTool."""
    cmds = import_module('maya.cmds')
    if cmds.window(QT_NAME, q=1, ex=1):
        cmds.deleteUI(QT_NAME)
    return AwesomeTool()
