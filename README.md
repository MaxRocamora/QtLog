[![PyPI version](https://badge.fury.io/py/qt-log.svg?style=flat-square&logo=appveyor)](https://badge.fury.io/py/qt-log)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/qt-log.svg?style=flat-square&logo=appveyor)](https://pypi.python.org/pypi/qt-log/)
[![Message](https://img.shields.io/badge/qtlog-python-blue?style=flat-square&logo=appveyor)](https://github.com/MaxRocamora/QtLog)

# QtLog
Custom Python Log with colored message display for Maya/Houdini/Nuke

*PySide2/Python3 - Maya +2022, Houdini +19, Nuke +13*   
*PySide6/Python3 - Maya +2025*

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

Import the logger and create a logger instance, you can create multiple loggers and output them into the same widget.

```python
    from qtlog.stream_log import get_stream_logger

    log = get_stream_logger('MyToolLog')
    log_ext = get_stream_logger('SomeOtherExternalLog')
```

Import the QtUILogger widget and create an instance of the widget, passing the app, the layout widget and the loggers, a layout widget is required.

```python
    from qtlog.qt_ui_logger import QtUILogger

    # inside your app
    self.loggers = QtUILogger(parent=self, layout_widget=self.ui.log_layout, loggers=[log, log_ext])
```

In you qt app, you can use the QtUILogger to display the log messages in a widget.

```python
    log.info('Message')
    log.warning('Message')
    log.error('Message')
    log.critical('Message')
    log.debug('Message')
    log.ok('Message')
    log.file('Message')
    log.process('Message')
    log.done('Message')
    log.hint('Message')
```

Lastly, when you close the app, remove the loggers from the widget by overriding the closeEvent() method.


```python

    def closeEvent(self, event):
        """Remove the widget from the loggers, call .close() on closeEvent()."""
        self.loggers.close()
        self.close()

```

See the full example tool in the examples folder.

## Install
pip install qt-log
