'''Custom Streamlogger
Used for standard log in maya/hou/nuke qt tools

# create a stream logger
from stream_log import get_stream_logger
log = get_stream_log('MyToolLog')
# send messages
log.hint('Message')

'''
import logging

# Log Levels

DONE_LEVEL = logging.INFO + 1  # long operations completed
HINT_LEVEL = logging.INFO + 2  # suggestions to the user
OK_LEVEL = logging.INFO + 3  # short operation completed
PROCESS_LEVEL = logging.INFO + 4  # the beggining of a process that requires time
FILE_LEVEL = logging.INFO + 5  # filepaths or filenames

COLORS = {
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


def get_stream_logger(name):
    ''' returns a configured custom logger '''
    log = logging.getLogger(name)
    log.propagate = False

    # adding a stream handler to our logger
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(name + ' - %(levelname)-7s | %(message)s')
    stream_handler.setFormatter(formatter)
    if len(log.handlers) == 0:
        log.addHandler(stream_handler)

    # calls
    def _done(message, *args, **kwargs):
        if log.isEnabledFor(DONE_LEVEL):
            log._log(DONE_LEVEL, message, args, **kwargs)

    def _hint(message, *args, **kwargs):
        if log.isEnabledFor(HINT_LEVEL):
            log._log(HINT_LEVEL, message, args, **kwargs)

    def _ok(message, *args, **kwargs):
        if log.isEnabledFor(OK_LEVEL):
            log._log(OK_LEVEL, message, args, **kwargs)

    def _process(message, *args, **kwargs):
        if log.isEnabledFor(PROCESS_LEVEL):
            log._log(PROCESS_LEVEL, message, args, **kwargs)

    def _file(message, *args, **kwargs):
        if log.isEnabledFor(FILE_LEVEL):
            log._log(FILE_LEVEL, message, args, **kwargs)

    # Custom Levels
    CUSTOM_LEVELS = [
        (DONE_LEVEL, 'DONE', _done),
        (HINT_LEVEL, 'HINT', _hint),
        (OK_LEVEL, 'OK', _ok),
        (PROCESS_LEVEL, 'PROCESS', _process),
        (FILE_LEVEL, 'FILE', _file),

    ]

    for item in CUSTOM_LEVELS:
        level, name, method = item

        # adding four steps of a custom levels
        logging.addLevelName(level, name)
        setattr(log, name, level)
        setattr(logging.getLoggerClass(), name, method)
        setattr(log, name.lower(), method)

    log.setLevel(logging.DEBUG)
    return log


if __name__ == '__main__':
    custom_log = get_stream_logger('my_log')
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
