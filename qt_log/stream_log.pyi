import logging
from typing import Any, Protocol

DONE_LEVEL: int
HINT_LEVEL: int
OK_LEVEL: int
PROCESS_LEVEL: int
FILE_LEVEL: int
COLORS: dict[int, str]

class StreamLogger(Protocol):
    propagate: bool
    handlers: list[logging.Handler]

    def setLevel(self, level: int) -> None: ...  # noqa: N802
    def addHandler(self, hdlr: logging.Handler) -> None: ...  # noqa: N802
    def removeHandler(self, hdlr: logging.Handler) -> None: ...  # noqa: N802
    def isEnabledFor(self, level: int) -> bool: ...  # noqa: N802
    def _log(
        self,
        level: int,
        msg: object,
        args: tuple[Any, ...],
        exc_info: Any | None = None,
        extra: Any | None = None,
        stack_info: bool = False,
        stacklevel: int = 1,
    ) -> None: ...
    def debug(self, msg: object, *args: Any, **kwargs: Any) -> None: ...
    def info(self, msg: object, *args: Any, **kwargs: Any) -> None: ...
    def warning(self, msg: object, *args: Any, **kwargs: Any) -> None: ...
    def error(self, msg: object, *args: Any, **kwargs: Any) -> None: ...
    def critical(self, msg: object, *args: Any, **kwargs: Any) -> None: ...
    def done(self, message: object, *args: Any, **kwargs: Any) -> None: ...
    def hint(self, message: object, *args: Any, **kwargs: Any) -> None: ...
    def ok(self, message: object, *args: Any, **kwargs: Any) -> None: ...
    def process(self, message: object, *args: Any, **kwargs: Any) -> None: ...
    def file(self, message: object, *args: Any, **kwargs: Any) -> None: ...

def get_stream_logger(name: str) -> StreamLogger: ...
