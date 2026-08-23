import logging
from typing import Any

DONE_LEVEL: int
HINT_LEVEL: int
OK_LEVEL: int
PROCESS_LEVEL: int
FILE_LEVEL: int
COLORS: dict[int, str]

class StreamLogger(logging.Logger):
    DONE: int
    HINT: int
    OK: int
    PROCESS: int
    FILE: int

    def done(self, message: object, *args: Any, **kwargs: Any) -> None: ...
    def hint(self, message: object, *args: Any, **kwargs: Any) -> None: ...
    def ok(self, message: object, *args: Any, **kwargs: Any) -> None: ...
    def process(self, message: object, *args: Any, **kwargs: Any) -> None: ...
    def file(self, message: object, *args: Any, **kwargs: Any) -> None: ...

def get_stream_logger(name: str) -> StreamLogger: ...
