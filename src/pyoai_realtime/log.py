import datetime
import json
import os
from enum import StrEnum, auto

from rich.console import Console


# Log levels
class LogLevel(StrEnum):
    """The log levels."""

    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

    def __le__(self, other: "LogLevel") -> bool:
        """Compare log levels.

        Args:
            other: The other log level.

        Returns:
            True if the log level is less than or equal to the other log level.
        """
        levels = list(LogLevel)
        return levels.index(self) <= levels.index(other)


console = Console()
LEVEL = LogLevel(os.environ.get("LOGLEVEL", LogLevel.INFO))


def print(*args, _stack_offset: int = 2, **kwargs):
    """Print a message.

    Args:
        msg: The message to print.
        kwargs: Keyword arguments to pass to the print function.
    """
    console.log(*args, _stack_offset=_stack_offset, **kwargs)


def debug(*args, **kwargs):
    """Print a debug message.

    Args:
        msg: The debug message.
        kwargs: Keyword arguments to pass to the print function.
    """
    if LEVEL <= LogLevel.DEBUG:
        print(f"[blue]Debug: {args}[/blue]", **kwargs)


def info(*args, _stack_offset: int = 3, **kwargs):
    """Print an info message.

    Args:
        msg: The info message.
        kwargs: Keyword arguments to pass to the print function.
    """
    if LEVEL <= LogLevel.INFO:
        print(f"[cyan]Info: {args}[/cyan]", _stack_offset=_stack_offset, **kwargs)


def success(*args, **kwargs):
    """Print a success message.

    Args:
        msg: The success message.
        kwargs: Keyword arguments to pass to the print function.
    """
    if LEVEL <= LogLevel.INFO:
        print(f"[green]Success: {args}[/green]", **kwargs)


def log(*args, _stack_offset: int = 2, **kwargs):
    """Takes a string and logs it to the console.

    Args:
        msg: The message to log.
        kwargs: Keyword arguments to pass to the print function.
    """
    if LEVEL <= LogLevel.INFO:
        console.log(*args, _stack_offset=_stack_offset, **kwargs)


def _log(debug: bool = False, *args, **kwargs):
    if debug:
        date = datetime.datetime.now().isoformat()
        log_items = [f"[Websocket/{date}]"]
        for arg in args:
            if isinstance(arg, (dict, list)):
                log_items.append(json.dumps(arg, indent=2))
            else:
                log_items.append(str(arg))
        log.print(" ".join(log_items))
