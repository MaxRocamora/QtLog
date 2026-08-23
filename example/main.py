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
from importlib import import_module
from pathlib import Path
from typing import Any, cast

from PySide6 import QtCore, QtUiTools
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QWidget
from shiboken6 import wrapInstance

from qt_log.qt_ui_logger import QtUILogger
from qt_log.stream_log import get_stream_logger


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

APP_NAME = 'AwesomeTool'
APP_VERSION = '1.0.0'
QT_NAME = 'awesome_tool_window'


class AwesomeTool(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Main window for the Awesome Tool."""
        if parent is None:
            parent = get_maya_main_window()
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setObjectName(QT_NAME)
        ui_file = Path(__file__).with_name('main.ui')
        loaded_ui = QtUiTools.QUiLoader().load(str(ui_file))
        if loaded_ui is None:
            raise RuntimeError(f'Could not load UI file: {ui_file}')
        self.ui: Any = loaded_ui
        self.setFixedSize(self.ui.maximumWidth(), self.ui.maximumHeight())
        self.setCentralWidget(self.ui)
        self.setWindowTitle(APP_NAME)

        # creating/storing loggers
        self.loggers = QtUILogger(self, self.ui.log_layout, [log, log_b])

        self.ui.btn_ok.clicked.connect(self.show_messages)
        self.ui.btn_cancel.clicked.connect(self.close)
        self.show()

    def show_messages(self) -> None:
        """Shows output messages."""
        log.ok(f'{APP_NAME} {APP_VERSION}')
        log.info('This is log.info')
        log.debug('This is log.debug')
        log.warning('This is log.warning')
        log.error('This is log.error')
        log.critical('This is log.critical')
        log.done('This is log.done')
        log.file('This is log.file')
        log.process('This is log.process')
        log.ok('This is log.ok')

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
