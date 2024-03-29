[![PyPI version](https://badge.fury.io/py/qt-log.svg?style=flat-square&logo=appveyor)](https://badge.fury.io/py/qt-log)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/qt-log.svg?style=flat-square&logo=appveyor)](https://pypi.python.org/pypi/qt-log/)
[![GitHub version](https://badge.fury.io/gh/MaxRocamora%2FQtLog.svg?style=flat-square&logo=appveyor)](https://badge.fury.io/gh/MaxRocamora%2FQtLog)
[![Message](https://img.shields.io/badge/qtlog-python-blue?style=flat-square&logo=appveyor)](https://github.com/MaxRocamora/QtLog)

# QtLog
Custom Python Log with colored message display for Maya/Houdini/Nuke

*PySide2/Python3 - Maya +2022, Houdini +19, Nuke +13*

#### Message Levels

```python
    log = get_stream_logger('my_log')

    log.info('test info')  # white
    log.warning('test warning')  # orange
    log.error('test error')  # red
    log.critical('test critical')  # purple
    log.debug('test debug')  # yellow
    log.ok('test ok')  # sky blue
    log.file('test file')  # super light blue
    log.process('test process')  # light blue
    log.done('test done')  # green
    log.hint('hint to the user')  # yellow
```

![Example APP ScreenShot](https://github.com/MaxRocamora/QtLog/blob/main/images/example_tool.png?raw=true)

#### Usage

```python

    # imports
    from qtlog.stream_log import get_stream_logger
    from qtlog.qt_ui_logger import QtUILogger

    # get loggers
    log = get_stream_logger('MyToolLog')
    log_ext = get_stream_logger('ExternalLog')

    # inside your qt app, you need a qtLayout to place the logger output widget.
    
    class MyTool(QMainWindow):
        def __init__(self, parent=get_maya_main_window()):
            ...

            # creating/storing loggers (self, QtLayout, loggers)
            self.loggers = QtUILogger(parent=self, layout_widget=self.ui.log_layout, loggers=[log, log_ext])
            self.ui.btn_ok.clicked.connect(self.show_messages)

        def closeEvent(self, event):
            # remove the widget from the loggers, call .close() on closeEvent()
            self.loggers.close()
            self.close()
    
    # sent messages are displayed in color on the ui widget and maya
    log.hint('Message')

```
#### Install
pip install qt-log
