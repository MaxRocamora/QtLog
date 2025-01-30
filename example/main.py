# ----------------------------------------------------------------------------------------
# Awesome Tool
# PySide2 Example Qt Maya Tool for showcase QtLog
#
"""# Run in Maya (add qtlog to pythonpath first).

import example.main as qtlog_example
qtlog_example.main()

"""
# ----------------------------------------------------------------------------------------
import os

import maya.cmds as cmds
from maya import OpenMayaUI as omui
from PySide2 import QtCore, QtUiTools
from PySide2.QtWidgets import QMainWindow, QWidget
from shiboken2 import wrapInstance

from qt_log.qt_ui_logger import QtUILogger
from qt_log.stream_log import get_stream_logger


def get_maya_main_window():
    """Returns wrapped maya main window for qt app's."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QWidget)


# get the loggers
log = get_stream_logger('AwesomeLog')
log_b = get_stream_logger('AnotherLog')

APP_NAME = 'AwesomeTool'
APP_VERSION = '1.0.0'
QT_NAME = 'awesome_tool_window'


class AwesomeTool(QMainWindow):
    def __init__(self, parent=get_maya_main_window()):
        """Main window for the Awesome Tool."""
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setObjectName(QT_NAME)
        ui_file = os.path.join(os.path.dirname(__file__), 'main.ui')
        self.ui = QtUiTools.QUiLoader().load(ui_file)
        self.setFixedSize(self.ui.maximumWidth(), self.ui.maximumHeight())
        self.setCentralWidget(self.ui)
        self.setWindowTitle(APP_NAME)

        # creating/storing loggers
        self.loggers = QtUILogger(self, self.ui.log_layout, [log, log_b])

        self.ui.btn_ok.clicked.connect(self.show_messages)
        self.ui.btn_cancel.clicked.connect(lambda: self.close())
        self.show()

    def show_messages(self):
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

        log.warning()

    def closeEvent(self, event):  # noqa: N802
        """Overloads the closeEvent to remove the widget from the loggers before call close()."""
        self.loggers.close()
        self.close()


# ----------------------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------------------


def load():
    """Loads the AwesomeTool."""
    if cmds.window(QT_NAME, q=1, ex=1):
        cmds.deleteUI(QT_NAME)
    AwesomeTool()
