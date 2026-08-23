import logging
from typing import assert_type

from qt_log.stream_log import StreamLogger, get_stream_logger

logger = get_stream_logger('typecheck')
assert_type(logger, StreamLogger)

child: logging.Logger = logger.getChild('child')
logger.log(logging.INFO, 'standard log')
logger.exception('standard exception')
logger.done('custom done')
logger.hint('custom hint')
logger.ok('custom ok')
logger.process('custom process')
logger.file('custom file')
