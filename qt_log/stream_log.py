"""Custom StreamLogger.

Used for standard log in maya/hou/nuke qt tools

# create a stream logger
from stream_log import get_stream_logger
log = get_stream_log('MyToolLog')
# send messages
log.hint('Message')

"""

from __future__ import annotations

import importlib
import logging
from collections.abc import Callable
from typing import Any

# Log Levels

DONE_LEVEL = logging.INFO + 1  # long operations completed
HINT_LEVEL = logging.INFO + 2  # suggestions to the user
OK_LEVEL = logging.INFO + 3  # short operation completed
PROCESS_LEVEL = logging.INFO + 4  # the beginning of a process that requires time
FILE_LEVEL = logging.INFO + 5  # filepaths or filenames

COLORS: dict[int, str] = {
    logging.DEBUG: 'yellow',
    logging.INFO: 'white',
    logging.WARNING: 'orange',
    logging.ERROR: 'red',
    logging.CRITICAL: 'purple',
    DONE_LEVEL: 'lime',
    HINT_LEVEL: 'yellow',
    OK_LEVEL: '#85c1e9',  # SKY BLUE
    PROCESS_LEVEL: '#5dade2',  # lIGHT BLUE
    FILE_LEVEL: '#aed6f1',  # SUPER LIGHT BLUE
}

CUSTOM_LEVELS: tuple[tuple[int, str], ...] = (
    (DONE_LEVEL, 'DONE'),
    (HINT_LEVEL, 'HINT'),
    (OK_LEVEL, 'OK'),
    (PROCESS_LEVEL, 'PROCESS'),
    (FILE_LEVEL, 'FILE'),
)

for custom_level, custom_level_name in CUSTOM_LEVELS:
    logging.addLevelName(custom_level, custom_level_name)


def _custom_log_method(log: logging.Logger, level: int) -> Callable[..., None]:
    def log_at_level(message: object, *args: Any, **kwargs: Any) -> None:
        if log.isEnabledFor(level):
            log._log(level, message, args, **kwargs)

    return log_at_level


class _UnrealLogHandler(logging.Handler):
    def __init__(self, unreal_module: Any) -> None:
        super().__init__()
        self._unreal = unreal_module

    def emit(self, record: logging.LogRecord) -> None:
        try:
            message = self.format(record)
            if record.levelno >= logging.ERROR:
                self._unreal.log_error(message)
            elif record.levelno >= logging.WARNING:
                self._unreal.log_warning(message)
            else:
                self._unreal.log(message)
        except Exception:
            self.handleError(record)


def _create_stream_handler() -> logging.Handler:
    try:
        unreal = importlib.import_module('unreal')
    except ModuleNotFoundError as exc:
        if exc.name != 'unreal':
            raise
        return logging.StreamHandler()
    return _UnrealLogHandler(unreal)


def get_stream_logger(name: str) -> logging.Logger:
    """Returns a configured custom logger."""
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    # this prevent double logging in maya script editor
    log.propagate = False

    stream_handler = next(
        (handler for handler in log.handlers if getattr(handler, '_qt_log_owned', False)),
        None,
    )
    if stream_handler is None:
        stream_handler = _create_stream_handler()
        stream_handler._qt_log_owned = True  # type: ignore[attr-defined]
        formatter = logging.Formatter(
            name + ' - %(asctime)s | %(levelname)-7s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        stream_handler.setFormatter(formatter)
        log.addHandler(stream_handler)

    for level, level_name in CUSTOM_LEVELS:
        setattr(log, level_name, level)
        setattr(log, level_name.lower(), _custom_log_method(log, level))

    return log


if __name__ == '__main__':
    custom_log: Any = get_stream_logger('my_log')
    custom_log.info('test info')
    custom_log.warning('test warning')
    custom_log.error('test error')
    custom_log.critical('test critical')
    custom_log.debug('test debug')
    custom_log.ok('test ok')
    custom_log.file('test file')
    custom_log.process('test process')
    custom_log.done('test done')
    custom_log.hint('hint to the user')
