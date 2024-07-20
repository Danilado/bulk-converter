import sys
from types import TracebackType
from typing import Optional, Type, Iterator, Iterable, TextIO


class LineStream(TextIO):
    def __init__(self, parent: 'MultilineOutputManager', descriptor: int) -> None:
        self.parent = parent
        self.desc = descriptor
        super().__init__()

    def __enter__(self) -> TextIO:
        pass

    def close(self) -> None:
        self.parent._line_closed(self.desc)

    def fileno(self) -> int:
        pass

    def flush(self) -> None:
        pass

    def isatty(self) -> bool:
        pass

    def read(self, n: int = ...) -> str:
        pass

    def readable(self) -> bool:
        pass

    def readline(self, limit: int = ...) -> str:
        pass

    def readlines(self, hint: int = ...) -> list[str]:
        pass

    def seek(self, offset: int, whence: int = ...) -> int:
        pass

    def seekable(self) -> bool:
        pass

    def tell(self) -> int:
        pass

    def truncate(self, size: Optional[int] = ...) -> int:
        pass

    def writable(self) -> bool:
        pass

    def writelines(self, lines: Iterable[str]) -> None:
        pass

    def __next__(self) -> str:
        pass

    def __iter__(self) -> Iterator[str]:
        pass

    def __exit__(self, t: Optional[Type[BaseException]], value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> Optional[bool]:
        pass

    def write(self, text: str):
        self.parent._set_line(self.desc, text)


dbg = open("dbg.txt", "a")


class MultilineOutputManager:
    def __init__(self) -> None:
        self.linecount = 0
        self.offset = 0
        self.before = ""
        self._updating = False
        self._lines: dict[int, str] = {}

    def _clear_line(self) -> None:
        sys.stdout.write("\x1b[1A\x1b[2K")

    def _clear_lines(self) -> None:
        sys.stdout.write("\x1b[1A\x1b[2K" * (len(self._lines) - self.offset))
        self.offset = 0

    def _print_lines(self) -> None:
        res = ""
        for _, line in list(self._lines.items()):
            res += line + "\n"

        sys.stdout.write(self.before)
        self.before = ""
        sys.stdout.write(res)

    def request_line(self) -> LineStream:
        self.linecount += 1
        res = LineStream(self, self.linecount)

        self._lines[self.linecount] = "\n"
        self.offset += 1

        return res

    def _line_closed(self, descriptor: int):
        self.before += (self._lines.pop(descriptor) + "\n")
        self.offset -= 1
        self._update()

    def _update(self):
        if self._updating:
            return

        self._updating = True
        self._clear_lines()
        self._print_lines()
        self._updating = False

    def _set_line(self, descriptor: int, text: str):
        dbg.write(f"{descriptor=}\t{text=}\n")
        res = text.strip(" \n\r").replace("\r", "").replace('\x1b[A', "")

        if res == "":
            return

        self._lines[descriptor] = res
        self._update()
