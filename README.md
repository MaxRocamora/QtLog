[![PyPI version](https://badge.fury.io/py/qt-log.svg?style=flat-square&logo=appveyor)](https://badge.fury.io/py/qt-log)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/qt-log.svg?style=flat-square&logo=appveyor)](https://pypi.python.org/pypi/qt-log/)
[![Message](https://img.shields.io/badge/qtlog-python-blue?style=flat-square&logo=appveyor)](https://github.com/MaxRocamora/QtLog)

# QtLog
Custom Python Log with colored message display for Maya/Houdini/Nuke

*PySide6/Python 3.9+*

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
from qt_log.stream_log import get_stream_logger

log = get_stream_logger('MyToolLog')
log_ext = get_stream_logger('SomeOtherExternalLog')
```

Import the QtUILogger widget and create an instance of the widget, passing the app, the layout widget and the loggers, a layout widget is required.

```python
from qt_log.qt_ui_logger import QtUILogger

# Inside your app
self.loggers = QtUILogger(
    parent=self,
    layout_widget=self.ui.log_layout,
    loggers=[log, log_ext],
)
```

Create `QtUILogger` on the Qt GUI thread after constructing `QApplication`. The parent must be a
`QWidget`, the destination must be a `QLayout`, and every logger must be a `logging.Logger`.
Repeated references to the same logger are attached only once.

In your Qt app, you can use `QtUILogger` to display log messages in a widget.

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

Records can be emitted from worker threads. Display updates are queued to the Qt GUI thread, so
the widget changes when the Qt event loop processes pending events. Pending display records are
bounded at 4,096; under sustained overload, the oldest pending record is discarded. Use
`self.loggers.dropped_records` and `self.loggers.peak_pending_records` to monitor overload.

Lastly, when you close the app, remove the handler from its loggers by overriding `closeEvent()`.
Call the base implementation rather than recursively closing the window.

```python
def closeEvent(self, event):
    """Detach the UI logger before the window is destroyed."""
    self.loggers.close()
    super().closeEvent(event)
```

### Standalone example

Run the host-neutral PySide6 example from the repository root:

```shell
uv run python -m example.standalone
```

The Maya-hosted example remains in `example/maya_tool.py` and is loaded inside Maya with
`example.maya_tool.load()`.

## Install

```shell
pip install qt-log
```
