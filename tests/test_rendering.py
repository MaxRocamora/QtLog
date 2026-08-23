from __future__ import annotations

import logging
import os
import sys
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from qt_log import qt_ui_logger
from qt_log.stream_log import DONE_LEVEL


class RecordRenderingTests(unittest.TestCase):
    formatter = logging.Formatter('%(levelname)-7s | %(message)s')

    def test_formats_arguments_and_escapes_html_metacharacters(self) -> None:
        record = logging.LogRecord(
            name='render_test',
            level=logging.WARNING,
            pathname=__file__,
            lineno=1,
            msg='open %s & continue',
            args=('<project>',),
            exc_info=None,
        )

        rendered = qt_ui_logger._record_to_html(record, self.formatter)

        self.assertEqual(
            rendered,
            '<font color = "orange" > WARNING | open &lt;project&gt; &amp; continue </font>',
        )

    def test_escapes_formatted_exception_text(self) -> None:
        try:
            raise ValueError('bad <value>')
        except ValueError:
            record = logging.LogRecord(
                name='render_test',
                level=logging.ERROR,
                pathname=__file__,
                lineno=1,
                msg='operation failed',
                args=(),
                exc_info=sys.exc_info(),
            )

        rendered = qt_ui_logger._record_to_html(record, self.formatter)

        self.assertIn('ERROR   | operation failed', rendered)
        self.assertIn('ValueError: bad &lt;value&gt;', rendered)
        self.assertNotIn('<value>', rendered)

    def test_uses_white_for_an_unknown_level(self) -> None:
        record = logging.LogRecord(
            name='render_test',
            level=15,
            pathname=__file__,
            lineno=1,
            msg='custom message',
            args=(),
            exc_info=None,
        )

        rendered = qt_ui_logger._record_to_html(record, self.formatter)

        self.assertEqual(
            rendered,
            '<font color = "white" > Level 15 | custom message </font>',
        )


class WidgetRenderingSmokeTests(unittest.TestCase):
    application: QApplication

    @classmethod
    def setUpClass(cls) -> None:  # noqa: N802
        cls.application = QApplication.instance() or QApplication([])

    def test_representative_levels_render_as_literal_colored_text(self) -> None:
        parent = QWidget()
        layout = QVBoxLayout(parent)
        handler = qt_ui_logger.QtUILogger(parent, layout, [])
        cases = (
            (logging.INFO, 'info <tag>', '#ffffff'),
            (logging.WARNING, 'warning', '#ffa500'),
            (logging.ERROR, 'error', '#ff0000'),
            (DONE_LEVEL, 'done', '#00ff00'),
        )

        for level, message, _ in cases:
            handler.emit(
                logging.LogRecord(
                    name='render_test',
                    level=level,
                    pathname=__file__,
                    lineno=1,
                    msg=message,
                    args=(),
                    exc_info=None,
                )
            )
        self.application.processEvents()

        self.assertEqual(
            handler.widget.toPlainText().splitlines(),
            ['INFO | info <tag> ', 'WARNING | warning ', 'ERROR | error ', 'DONE | done '],
        )
        block = handler.widget.document().firstBlock()
        rendered_colors: list[str] = []
        while block.isValid():
            fragment = block.begin().fragment()
            rendered_colors.append(fragment.charFormat().foreground().color().name())
            block = block.next()

        self.assertEqual(rendered_colors, [color for _, _, color in cases])
        handler.close()
        parent.close()


if __name__ == '__main__':
    unittest.main()
