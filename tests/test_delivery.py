from __future__ import annotations

import logging
import os
import threading
import unittest
from time import perf_counter

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from shiboken6 import isValid

from qt_log.qt_ui_logger import _MAX_PENDING_RECORDS, QtUILogger


class QtDeliveryTests(unittest.TestCase):
    application: QApplication

    @classmethod
    def setUpClass(cls) -> None:  # noqa: N802
        cls.application = QApplication.instance() or QApplication([])

    def test_worker_thread_records_are_queued_in_order_for_the_gui_thread(self) -> None:
        parent = QWidget()
        layout = QVBoxLayout(parent)
        handler = QtUILogger(parent, layout, [])
        messages = [f'message {index}' for index in range(25)]

        def emit_records() -> None:
            for message in messages:
                handler.emit(
                    logging.LogRecord(
                        name='delivery_test',
                        level=logging.INFO,
                        pathname=__file__,
                        lineno=1,
                        msg=message,
                        args=(),
                        exc_info=None,
                    )
                )

        worker = threading.Thread(target=emit_records)
        worker.start()
        worker.join()

        self.assertEqual(handler.widget.toPlainText(), '')
        self.assertIs(handler.widget.thread(), self.application.thread())

        self.application.processEvents()

        self.assertEqual(
            handler.widget.toPlainText().splitlines(),
            [f'INFO | {message} ' for message in messages],
        )
        handler.close()
        parent.close()

    def test_close_discards_pending_and_future_delivery(self) -> None:
        logger = logging.getLogger('qtlog_delivery_close')
        parent = QWidget()
        layout = QVBoxLayout(parent)
        handler = QtUILogger(parent, layout, [logger])
        record = logging.LogRecord(
            name=logger.name,
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg='must not render',
            args=(),
            exc_info=None,
        )

        handler.emit(record)
        handler.close()
        handler.emit(record)
        self.application.processEvents()

        self.assertNotIn(handler, logger.handlers)
        self.assertEqual(handler.widget.toPlainText(), '')
        parent.close()

    def test_widget_deletion_discards_pending_delivery(self) -> None:
        parent = QWidget()
        layout = QVBoxLayout(parent)
        handler = QtUILogger(parent, layout, [])
        record = logging.LogRecord(
            name='delivery_test',
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg='pending deletion',
            args=(),
            exc_info=None,
        )

        handler.emit(record)
        parent.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        self.application.processEvents()

        self.assertFalse(isValid(parent))
        self.assertFalse(isValid(handler.widget))
        handler.emit(record)
        handler.close()

    def test_pending_delivery_is_bounded_and_reports_overflow(self) -> None:
        parent = QWidget()
        layout = QVBoxLayout(parent)
        handler = QtUILogger(parent, layout, [])
        overflow = 8

        for index in range(_MAX_PENDING_RECORDS + overflow):
            handler.emit(
                logging.LogRecord(
                    name='delivery_test',
                    level=logging.INFO,
                    pathname=__file__,
                    lineno=1,
                    msg='message %d',
                    args=(index,),
                    exc_info=None,
                )
            )

        self.assertEqual(handler.dropped_records, overflow)
        self.assertEqual(handler.peak_pending_records, _MAX_PENDING_RECORDS)

        deadline = perf_counter() + 5.0
        while len(handler.widget.toPlainText().splitlines()) < _MAX_PENDING_RECORDS:
            self.application.processEvents()
            if perf_counter() >= deadline:
                self.fail('timed out while draining pending records')

        rendered_lines = handler.widget.toPlainText().splitlines()
        self.assertEqual(len(rendered_lines), _MAX_PENDING_RECORDS)
        self.assertEqual(rendered_lines[0], f'INFO | message {overflow} ')
        self.assertEqual(
            rendered_lines[-1],
            f'INFO | message {_MAX_PENDING_RECORDS + overflow - 1} ',
        )
        handler.close()
        parent.close()


if __name__ == '__main__':
    unittest.main()
