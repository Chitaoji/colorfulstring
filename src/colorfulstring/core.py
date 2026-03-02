"""
Contains the core of colorfulstring.

NOTE: this module is private. All functions and objects are available in the main
`colorfulstring` namespace - use that instead.

"""

from functools import partial
from typing import Any, Callable, Self, overload

__all__ = ["c"]


class _DefaultReceiver:
    def __lshift__(self, obj: "ColorfulString") -> "ColorfulString":
        return obj


class ColorfulString:
    """Make colorful strings."""

    def __init__(
        self,
        default_color: str = "",
        string: str | None = None,
        status: tuple[bool, bool] | None = None,
        receiver: Self | _DefaultReceiver = _DefaultReceiver(),
        printer: Callable | None = None,
    ) -> None:
        self._default_color = default_color
        self._string = string
        self._status = status
        self._receiver = receiver
        self._printer = printer

    def __repr__(self) -> str:
        if self._status is None and self._string is not None:
            return self._string
        return super().__repr__()

    def __str__(self) -> str:
        return repr(self)

    def __add__(self, string: str) -> str:
        return self.__asstr() + string

    def __radd__(self, string: str) -> str:
        return string + self.__asstr()

    def __call__(self, string: str) -> str:
        return self.__make_str(string)

    def __lshift__(self, obj: str | Self | Any) -> Self:
        if isinstance(obj, self.__class__):
            if obj._status is not None:
                if (
                    not isinstance(obj._receiver, _DefaultReceiver)
                    or obj._string is not None
                ):
                    raise ValueError("unfinished call to ifelse(), iftrue() or ifnot()")
                obj._receiver = self
                return obj

            if obj._string is None:
                raise ValueError("<< c alone is not allowed")
        return self.__recv(obj)

    def __rlshift__(self, obj: str | Self | Any) -> Self:
        return c << obj << self

    def __rshift__[T](self, obj: type[T]) -> T:
        if self._status is None and self._string is not None:
            return obj(self._string)
        raise ValueError(f"nothing to convert to {obj}")

    def __matmul__(self, obj: str | Self | Any) -> Self:
        return self << obj

    def ifelse(self, condition: bool) -> Self:
        if self._status is not None:
            raise ValueError("duplicated call to ifelse(), iftrue() or ifnot()")
        return self.copy(status=(bool(condition), True))

    def iftrue(self, condition: bool) -> Self:
        if self._status is not None:
            raise ValueError("duplicated call to ifelse(), iftrue() or ifnot()")
        return self.copy(string="", status=(not bool(condition), False))

    def ifnot(self, condition: bool) -> Self:
        if self._status is not None:
            raise ValueError("duplicated call to ifelse(), iftrue() or ifnot()")
        return self.copy(string="", status=(bool(condition), False))

    def copy(
        self,
        *,
        default_color: str = ...,
        string: str | None = ...,
        status: tuple[bool, bool] | None = ...,
        receiver: Self | _DefaultReceiver = ...,
        printer: Callable | None = ...,
    ) -> Self:
        return self.__class__(
            self._default_color if default_color is Ellipsis else default_color,
            self._string if string is Ellipsis else string,
            self._status if status is Ellipsis else status,
            self._receiver if receiver is Ellipsis else receiver,
            self._printer if printer is Ellipsis else printer,
        )

    def __recv(self, obj: str | Self | Any) -> Self:
        if self._status is None:
            return self.copy(string=self.__asstr() + self.__make_str(obj))
        b, now = self._status
        if now:
            if b:
                return self.copy(
                    string=self.__asstr() + self.__make_str(obj), status=(b, False)
                )
            return self.copy(status=(b, False))
        elif b:
            return self._receiver << self.copy(status=None)
        return self._receiver << self.copy(
            string=self.__asstr() + self.__make_str(obj), status=None
        )

    def __make_str(self, obj: str | Self | Any) -> str:
        if isinstance(obj, ColorfulString):
            string = str(obj)
        else:
            string = str(obj)
            if self._default_color and string:
                string = f"${self._default_color}{string}$"
            string = (
                string.replace("$D", "\033[30m")  # Dark
                .replace("$R", "\033[31m")  # Red
                .replace("$G", "\033[32m")  # Green
                .replace("$Y", "\033[33m")  # Yellow
                .replace("$B", "\033[34m")  # Blue
                .replace("$P", "\033[35m")  # Purple
                .replace("$C", "\033[36m")  # Cyan
                .replace("$W", "\033[37m")  # White
                .replace("$", "\033[0m")
            )
        if self._printer is not None:
            self._printer(string)
        return string

    def __asstr(self) -> str:
        return "" if self._string is None else self._string

    @property
    def print(self) -> Self:
        return self.copy(printer=partial(print, end=""))

    @property
    def endl(self) -> Self:
        return ColorfulString(string="\n")

    @property
    def d(self) -> Self:
        return self.copy(default_color="D")

    @property
    def r(self) -> Self:
        return self.copy(default_color="R")

    @property
    def g(self) -> Self:
        return self.copy(default_color="G")

    @property
    def y(self) -> Self:
        return self.copy(default_color="Y")

    @property
    def b(self) -> Self:
        return self.copy(default_color="B")

    @property
    def p(self) -> Self:
        return self.copy(default_color="P")

    @property
    def c(self) -> Self:
        return self.copy(default_color="C")

    @property
    def w(self) -> Self:
        return self.copy(default_color="W")


c = ColorfulString()
