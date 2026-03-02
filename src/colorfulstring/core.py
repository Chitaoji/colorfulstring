"""
Contains the core of colorfulstring.

This module defines :class:`ColorfulString` and the singleton ``c`` used to build
ANSI-colored terminal strings with a fluent API.

NOTE: this module is private. All functions and objects are available in the main
`colorfulstring` namespace - use that instead.

"""

from functools import partial
from typing import Any, Callable, Self

__all__ = ["c"]


class _DefaultReceiver:
    """Fallback receiver used by conditional pipelines."""

    def __lshift__(self, obj: "ColorfulStringBuilder") -> "ColorfulStringBuilder":
        return obj


class ColorfulStringBuilder:
    """Fluent builder for ANSI-colored strings.

    ``ColorfulString`` supports color shortcuts (``.r``, ``.g`` ...), concatenation,
    piping with ``<<``/``@``, and conditional output with ``ifelse``/``iftrue``/``ifnot``.

    Typical usage starts from the module-level singleton ``c``.
    """

    def __init__(
        self,
        default_color: str = "",
        string: str | None = None,
        status: tuple[bool, bool] | None = None,
        receiver: Self | _DefaultReceiver = _DefaultReceiver(),
        printer: Callable | None = None,
    ) -> None:
        """Create an internal builder state.

        Args:
            default_color: Default color token applied to plain strings.
            string: Accumulated output string.
            status: Internal state for conditional chaining.
            receiver: Target builder used by conditional chains.
            printer: Optional side-effect callback invoked on generated fragments.
        """
        self._default_color = default_color
        self._string = string
        self._status = status
        self._receiver = receiver
        self._printer = printer

    def __repr__(self) -> str:
        """Return accumulated string when finalized, else default repr."""
        if self._status is None and self._string is not None:
            return self._string
        return super().__repr__()

    def __str__(self) -> str:
        """Return the user-facing string representation."""
        return repr(self)

    def __add__(self, string: str) -> str:
        """Append a Python string to the built output."""
        return self.__asstr() + string

    def __radd__(self, string: str) -> str:
        """Prepend a Python string to the built output."""
        return string + self.__asstr()

    def __call__(self, string: str) -> str:
        """Convert input to colored output according to current color context."""
        return self.__make_str(string)

    def __lshift__(self, obj: str | Self | Any) -> Self:
        """Pipe data into the builder.

        ``builder << value`` appends ``value`` after converting color tokens.
        Passing another ``ColorfulString`` is used internally to wire conditional chains.
        """
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
        """Support ``value << builder`` style piping."""
        return c << obj << self

    def __rshift__[T](self, obj: type[T]) -> T:
        """Cast the finalized string to another type.

        Example:
            ``(c.r << "42") >> int``
        """
        if self._status is None and self._string is not None:
            return obj(self._string)
        raise ValueError(f"nothing to convert to {obj}")

    def __matmul__(self, obj: str | Self | Any) -> Self:
        """Alias of ``<<`` for users who prefer ``@`` syntax."""
        return self << obj

    def ifelse(self, condition: bool) -> Self:
        """Start a two-branch conditional chain.

        The first subsequent value is used when ``condition`` is true; the second one
        is used otherwise.
        """
        if self._status is not None:
            raise ValueError("duplicated call to ifelse(), iftrue() or ifnot()")
        return self.copy(status=(bool(condition), True))

    def iftrue(self, condition: bool) -> Self:
        """Append next value only when ``condition`` is true."""
        if self._status is not None:
            raise ValueError("duplicated call to ifelse(), iftrue() or ifnot()")
        return self.copy(string="", status=(not bool(condition), False))

    def ifnot(self, condition: bool) -> Self:
        """Append next value only when ``condition`` is false."""
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
        """Return a cloned builder with selected fields overridden."""
        return self.__class__(
            self._default_color if default_color is Ellipsis else default_color,
            self._string if string is Ellipsis else string,
            self._status if status is Ellipsis else status,
            self._receiver if receiver is Ellipsis else receiver,
            self._printer if printer is Ellipsis else printer,
        )

    def __recv(self, obj: str | Self | Any) -> Self:
        """Receive an object and merge it into current/conditional pipeline."""
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
        """Convert value to final ANSI text and optionally emit to printer."""
        if isinstance(obj, ColorfulStringBuilder):
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
        """Get accumulated output or an empty string."""
        return "" if self._string is None else self._string

    @property
    def print(self) -> Self:
        """Return builder that prints each generated fragment immediately."""
        return self.copy(printer=partial(print, end=""))

    @property
    def endl(self) -> Self:
        """Return a newline fragment."""
        return ColorfulStringBuilder(string="\n")

    @property
    def d(self) -> Self:
        """Return a builder with dark/black default color."""
        return self.copy(default_color="D")

    @property
    def r(self) -> Self:
        """Return a builder with red default color."""
        return self.copy(default_color="R")

    @property
    def g(self) -> Self:
        """Return a builder with green default color."""
        return self.copy(default_color="G")

    @property
    def y(self) -> Self:
        """Return a builder with yellow default color."""
        return self.copy(default_color="Y")

    @property
    def b(self) -> Self:
        """Return a builder with blue default color."""
        return self.copy(default_color="B")

    @property
    def p(self) -> Self:
        """Return a builder with purple default color."""
        return self.copy(default_color="P")

    @property
    def c(self) -> Self:
        """Return a builder with cyan default color."""
        return self.copy(default_color="C")

    @property
    def w(self) -> Self:
        """Return a builder with white default color."""
        return self.copy(default_color="W")


c = ColorfulStringBuilder()
