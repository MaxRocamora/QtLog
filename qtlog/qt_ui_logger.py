'''A QPlainTextEdit Widget linked to stream_loggers
Write log messages color formatted to the given ui

# get loggers
log = get_stream_log('MyToolLog')
log_ext = get_stream_log('ExternalLog')

# create the log widget
self.loggers = QtUILogger(self, self.ui.log_layout, [log, log_ext])

log.hint('Message')

'''
import contextlib
import logging

from PySide2.QtWidgets import QPlainTextEdit
from PySide2.QtGui import QFont

from a2log.stream_log import COLORS


class QtUILogger(logging.Handler):

    def __init__(self, parent: type, layout_widget: type, loggers: list):
        super().__init__()
        '''creates the log widget and parent the loggers to the layout widget provided

        Args:
            parent (QtMainWindow): qt MainWindow
            layout_widget (QtLayoutWidget): the layout container for the text widget
            loggers (list): list of stream_loggers
        '''

        # create output display widget, attach it to the layout widget
        self.widget = QPlainTextEdit(parent)
        layout_widget.addWidget(self.widget)

        # add loggers handlers to the widget
        self.loggers = []
        for log in loggers:
            self.loggers.append(log)
            log.addHandler(self)

        # set font, css, message format
        font = QFont('nosuchfont')
        font.setStyleHint(font.Monospace)
        self.widget.setFont(font)
        self.widget.setStyleSheet('''
                border: 3px solid rgb(80, 80, 80);
                color: rgb(255, 255, 255);
                background-color: rgb(20, 20, 20);
                ''')
        self.widget.setReadOnly(True)
        self.setFormatter(logging.Formatter('%(levelname)-7s | %(message)s'))

    def close(self):
        ''' removes all handlers from this widget '''
        for logger in self.loggers:
            if logger is not None:
                logger.removeHandler(self.widget)

    def emit(self, record):
        '''writes the message formatted, uses font
        color based on error level number

        Args:
            record (logger record)
        '''
        color = COLORS.get(record.levelno, 'white')
        msg = self.format(record)
        s = f"""<font color = "{color}" > {msg} </font>"""
        with contextlib.suppress(RuntimeError):
            self.widget.appendHtml(s)

    def clear(self):
        ''' clears widget text '''
        self.widget.clear()
