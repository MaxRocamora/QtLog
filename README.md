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
    from stream_log import get_stream_log
    from qt_ui_logger import QtUILogger

    # get loggers
    log = get_stream_log('MyToolLog')
    log_ext = get_stream_log('ExternalLog')

    # create the log widget
    self.loggers = QtUILogger(parent=self, layout_widget=self.ui.log_layout, loggers=[log, log_ext])

    # sent messages are displayed in color on the ui widget and maya
    log.hint('Message')

```
