from __future__ import annotations

import logging
import sys
import unittest
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock, patch

from qt_log.qt_ui_logger import QtUILogger
from qt_log.stream_log import (
    DONE_LEVEL,
    FILE_LEVEL,
    HINT_LEVEL,
    OK_LEVEL,
    PROCESS_LEVEL,
    get_stream_logger,
)


class RecordingHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


class FakeLogger:
    def __init__(self) -> None:
        self.removed_handlers: list[logging.Handler] = []

    def removeHandler(self, handler: logging.Handler) -> None:  # noqa: N802
        self.removed_handlers.append(handler)


class StreamLoggerTests(unittest.TestCase):
    logger_names = ('qtlog_test_a', 'qtlog_test_b', 'qtlog_test_existing')

    def tearDown(self) -> None:
        for logger_name in self.logger_names:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
                handler.close()
            logging.Logger.manager.loggerDict.pop(logger_name, None)

    def test_custom_levels_keep_their_public_contract(self) -> None:
        expected_levels = {
            'done': (DONE_LEVEL, 'DONE'),
            'hint': (HINT_LEVEL, 'HINT'),
            'ok': (OK_LEVEL, 'OK'),
            'process': (PROCESS_LEVEL, 'PROCESS'),
            'file': (FILE_LEVEL, 'FILE'),
        }
        logger = get_stream_logger('qtlog_test_a')
        recorder = RecordingHandler()
        logger.addHandler(recorder)

        for method_name, (level, _) in expected_levels.items():
            getattr(logger, method_name)('%s message', method_name)
            self.assertEqual(getattr(logger, method_name.upper()), level)

        self.assertEqual(
            [
                (record.levelno, record.levelname, record.getMessage())
                for record in recorder.records
            ],
            [
                (level, level_name, f'{method_name} message')
                for method_name, (level, level_name) in expected_levels.items()
            ],
        )

    def test_standard_levels_keep_their_public_contract(self) -> None:
        logger = get_stream_logger('qtlog_test_a')
        recorder = RecordingHandler()
        logger.addHandler(recorder)

        expected_levels = (
            ('debug', logging.DEBUG, 'DEBUG'),
            ('info', logging.INFO, 'INFO'),
            ('warning', logging.WARNING, 'WARNING'),
            ('error', logging.ERROR, 'ERROR'),
            ('critical', logging.CRITICAL, 'CRITICAL'),
        )
        for method_name, _, _ in expected_levels:
            getattr(logger, method_name)('%s message', method_name)

        self.assertEqual(
            [
                (record.levelno, record.levelname, record.getMessage())
                for record in recorder.records
            ],
            [
                (level, level_name, f'{method_name} message')
                for method_name, level, level_name in expected_levels
            ],
        )

    def test_custom_methods_route_through_the_invoking_logger(self) -> None:
        logger_a = get_stream_logger('qtlog_test_a')
        logger_b = get_stream_logger('qtlog_test_b')
        recorder_a = RecordingHandler()
        recorder_b = RecordingHandler()
        logger_a.addHandler(recorder_a)
        logger_b.addHandler(recorder_b)

        logger_a.done('from a')  # type: ignore[attr-defined]
        logger_b.done('from b')  # type: ignore[attr-defined]

        self.assertEqual(
            [(record.name, record.getMessage()) for record in recorder_a.records],
            [('qtlog_test_a', 'from a')],
        )
        self.assertEqual(
            [(record.name, record.getMessage()) for record in recorder_b.records],
            [('qtlog_test_b', 'from b')],
        )

    def test_factory_preserves_foreign_handlers_and_adds_one_owned_handler(self) -> None:
        logger = logging.getLogger('qtlog_test_existing')
        foreign_handler = logging.NullHandler()
        logger.addHandler(foreign_handler)

        first_result = get_stream_logger('qtlog_test_existing')
        owned_handler = next(
            handler for handler in logger.handlers if getattr(handler, '_qt_log_owned', False)
        )
        second_result = get_stream_logger('qtlog_test_existing')

        self.assertIs(first_result, logger)
        self.assertIs(second_result, logger)
        self.assertIn(foreign_handler, logger.handlers)
        self.assertIn(owned_handler, logger.handlers)
        self.assertEqual(
            sum(
                bool(getattr(handler, '_qt_log_owned', False))
                for handler in logger.handlers
            ),
            1,
        )
        self.assertEqual(
            owned_handler.formatter._fmt,
            'qtlog_test_existing - %(asctime)s | %(levelname)-7s | %(message)s',
        )
        self.assertEqual(owned_handler.formatter.datefmt, '%Y-%m-%d %H:%M:%S')

    def test_factory_uses_standard_stream_handler_outside_unreal(self) -> None:
        with patch.dict(sys.modules, {'unreal': None}):
            logger = get_stream_logger('qtlog_test_a')

        self.assertIs(type(logger.handlers[0]), logging.StreamHandler)

    def test_factory_routes_levels_through_unreal_logging(self) -> None:
        unreal = SimpleNamespace(
            log=Mock(),
            log_warning=Mock(),
            log_error=Mock(),
        )

        with patch.dict(sys.modules, {'unreal': unreal}):
            logger = get_stream_logger('qtlog_test_a')
            logger.info('ready')
            logger.warning('careful')
            logger.error('failed')

        self.assertIn('INFO', unreal.log.call_args.args[0])
        self.assertIn('ready', unreal.log.call_args.args[0])
        self.assertIn('WARNING', unreal.log_warning.call_args.args[0])
        self.assertIn('careful', unreal.log_warning.call_args.args[0])
        self.assertIn('ERROR', unreal.log_error.call_args.args[0])
        self.assertIn('failed', unreal.log_error.call_args.args[0])

    def test_factory_does_not_mutate_the_global_logger_class(self) -> None:
        get_stream_logger('qtlog_test_a')

        for method_name in ('DONE', 'HINT', 'OK', 'PROCESS', 'FILE'):
            self.assertNotIn(method_name, logging.Logger.__dict__)


class QtUILoggerLifecycleTests(unittest.TestCase):
    def test_close_detaches_the_handler_once_and_releases_loggers(self) -> None:
        logger_a = FakeLogger()
        logger_b = FakeLogger()
        handler = QtUILogger.__new__(QtUILogger)
        logging.Handler.__init__(handler)
        handler.loggers = [logger_a, logger_b]  # type: ignore[list-item]
        handler.widget = Any

        handler.close()
        handler.close()

        self.assertEqual(logger_a.removed_handlers, [handler])
        self.assertEqual(logger_b.removed_handlers, [handler])
        self.assertEqual(handler.loggers, [])


if __name__ == '__main__':
    unittest.main()
