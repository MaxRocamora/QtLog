from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
import unittest
from typing import Any, cast

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from qt_log.qt_ui_logger import QtUILogger


class QtUILoggerValidationTests(unittest.TestCase):
    application: QApplication

    @classmethod
    def setUpClass(cls) -> None:  # noqa: N802
        cls.application = cast(QApplication | None, QApplication.instance()) or QApplication([])

    def test_requires_a_qapplication_before_other_inputs(self) -> None:
        environment = os.environ.copy()
        environment['QT_QPA_PLATFORM'] = 'offscreen'
        result = subprocess.run(
            [
                sys.executable,
                '-c',
                ('from qt_log.qt_ui_logger import QtUILogger; QtUILogger(None, None, [])'),
            ],
            capture_output=True,
            check=False,
            env=environment,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn('QtUILogger requires an active QApplication', result.stderr)

    def test_rejects_construction_outside_the_gui_thread(self) -> None:
        parent = QWidget()
        layout = QVBoxLayout(parent)
        errors: list[BaseException] = []

        def construct_handler() -> None:
            try:
                QtUILogger(parent, layout, [])
            except BaseException as error:
                errors.append(error)

        worker = threading.Thread(target=construct_handler)
        worker.start()
        worker.join()

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], RuntimeError)
        self.assertEqual(str(errors[0]), 'QtUILogger must be created on the Qt GUI thread')
        parent.close()

    def test_rejects_invalid_parent_layout_and_logger_elements(self) -> None:
        parent = QWidget()
        layout = QVBoxLayout(parent)

        with self.assertRaisesRegex(TypeError, 'parent must be a QWidget'):
            QtUILogger(cast(Any, object()), layout, [])
        with self.assertRaisesRegex(TypeError, 'layout_widget must be a QLayout'):
            QtUILogger(parent, cast(Any, object()), [])
        with self.assertRaisesRegex(TypeError, 'loggers must be a sequence'):
            QtUILogger(parent, layout, cast(Any, object()))
        with self.assertRaisesRegex(
            TypeError,
            r'loggers\[1\] must be a logging.Logger',
        ):
            QtUILogger(parent, layout, [logging.getLogger('valid'), cast(Any, object())])

        parent.close()

    def test_deduplicates_logger_instances_by_identity(self) -> None:
        parent = QWidget()
        layout = QVBoxLayout(parent)
        logger = logging.getLogger('qtlog_validation_duplicate')
        handler = QtUILogger(parent, layout, [logger, logger])

        self.assertEqual(handler.loggers, [logger])
        self.assertEqual(logger.handlers.count(handler), 1)

        handler.close()
        self.assertNotIn(handler, logger.handlers)
        parent.close()


if __name__ == '__main__':
    unittest.main()
