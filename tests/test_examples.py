from __future__ import annotations

import importlib
import inspect
import logging
import os
import unittest
from time import perf_counter
from typing import cast
from unittest.mock import Mock, patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication, QWidget


class ExampleTests(unittest.TestCase):
    application: QApplication

    @classmethod
    def setUpClass(cls) -> None:  # noqa: N802
        cls.application = cast(QApplication | None, QApplication.instance()) or QApplication([])

    def test_maya_example_import_and_parent_lookup_are_host_deferred(self) -> None:
        maya_example = importlib.import_module('example.maya_tool')
        parent_parameter = inspect.signature(maya_example.AwesomeTool.__init__).parameters[
            'parent'
        ]

        self.assertIsNone(parent_parameter.default)

    def test_maya_example_builds_ui_and_streams_500_messages(self) -> None:
        maya_example = importlib.import_module('example.maya_tool')
        parent = QWidget()
        window = maya_example.AwesomeTool(parent=parent)
        write_message = Mock()

        self.assertEqual(window.btn_ok.text(), 'OK')
        self.assertEqual(window.stream_button.text(), 'Stream messages')
        self.assertEqual(window.btn_cancel.text(), 'CANCEL')

        with patch.object(
            maya_example.random,
            'choice',
            return_value=write_message,
        ) as random_choice:
            window.stream_button.click()

        self.assertEqual(random_choice.call_count, 500)
        self.assertEqual(write_message.call_count, 500)
        write_message.assert_any_call('Stream message %03d/500', 1)
        write_message.assert_any_call('Stream message %03d/500', 500)
        window.close()
        self.application.processEvents()

    def test_standalone_example_renders_and_detaches_on_close(self) -> None:
        standalone = importlib.import_module('example.standalone')
        window = standalone.StandaloneLogWindow()
        logger = window.logger
        handler = window.log_handler

        window.show_messages()
        self.application.processEvents()

        rendered_text = handler.widget.toPlainText()
        self.assertIn('INFO | QtLog standalone example', rendered_text)
        self.assertIn('DONE | Messages delivered on the Qt GUI thread', rendered_text)
        self.assertIn(handler, logger.handlers)

        window.close()
        self.application.processEvents()

        self.assertNotIn(handler, logger.handlers)

    def test_stream_button_renders_500_random_level_messages(self) -> None:
        standalone = importlib.import_module('example.standalone')
        window = standalone.StandaloneLogWindow()
        stream_handler = next(
            handler
            for handler in window.logger.handlers
            if getattr(handler, '_qt_log_owned', False)
        )
        original_stream_level = stream_handler.level
        self.addCleanup(stream_handler.setLevel, original_stream_level)
        stream_handler.setLevel(logging.CRITICAL + 1)

        with patch.object(
            standalone.random,
            'choice',
            wraps=standalone.random.choice,
        ) as random_choice:
            window.stream_button.click()

        self.assertEqual(random_choice.call_count, 500)
        deadline = perf_counter() + 5.0
        while len(window.log_handler.widget.toPlainText().splitlines()) < 500:
            self.application.processEvents()
            if perf_counter() >= deadline:
                self.fail('timed out while rendering streamed messages')

        rendered_lines = window.log_handler.widget.toPlainText().splitlines()
        self.assertEqual(len(rendered_lines), 500)
        self.assertIn('Stream message 001/500', rendered_lines[0])
        self.assertIn('Stream message 500/500', rendered_lines[-1])
        window.close()
        self.application.processEvents()


if __name__ == '__main__':
    unittest.main()
