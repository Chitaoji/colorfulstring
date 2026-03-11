"""
Contains the core of colorfulstring.

This module defines :class:`ColorfulString` and the singleton `c` used to build
ANSI-colored terminal strings with a fluent API.

NOTE: this module is private. All functions and objects are available in the main
`colorfulstring` namespace - use that instead.

"""

import re
from functools import partial
from typing import Any, Callable, Self

__all__ = ["c"]


ANSI_TOKEN_COLORS: dict[str, str] = {
    "D": "\x1b[30m",  # Dark/Black
    "R": "\x1b[31m",  # Red
    "G": "\x1b[32m",  # Green
    "Y": "\x1b[33m",  # Yellow
    "B": "\x1b[34m",  # Blue
    "P": "\x1b[35m",  # Purple
    "C": "\x1b[36m",  # Cyan
    "W": "\x1b[37m",  # White
}


ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-9;]*m")


class _DefaultReceiver:
    """Fallback receiver used by conditional pipelines."""

    def __lshift__(self, obj: "ColorfulStringBuilder") -> "ColorfulStringBuilder":
        return obj


class ColorfulStringBuilder:
    """Fluent builder for ANSI-colored strings.

    `ColorfulString` supports color shortcuts (`.r`, `.g` ...), concatenation,
    piping with `<<`/`@`, and conditional output with `ifelse`/`iftrue`/`ifnot`.

    Typical usage starts from the module-level singleton `c`.
    """

    def __init__(
        self,
        default_color: str = "",
        faint: bool = False,
        underlined: bool = False,
        string: str | None = None,
        status: tuple[bool, bool] | None = None,
        receiver: Self | _DefaultReceiver = _DefaultReceiver(),
        printer: Callable | None = None,
    ) -> None:
        """Create an internal builder state.

        Args:
            default_color: Default color token applied to plain strings.
            faint: Whether foreground color should use the faint ANSI variant.
            underlined: Whether generated strings should apply underline formatting.
            string: Accumulated output string.
            status: Internal state for conditional chaining.
            receiver: Target builder used by conditional chains.
            printer: Optional side-effect callback invoked on generated fragments.
        """
        self._default_color = default_color
        self._faint = faint
        self._underlined = underlined
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

        `builder << value` appends `value` after converting color tokens.
        Passing another `ColorfulString` is used internally to wire conditional chains.
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
        """Support `value << builder` style piping."""
        return c << obj << self

    def __rshift__[T](self, obj: type[T]) -> T:
        """Cast the finalized string to another type.

        Example:
            `(c.r << "42") >> int`
        """
        if self._status is not None:
            raise ValueError("unfinished call to ifelse(), iftrue() or ifnot()")
        if self._string is not None:
            return obj(repr(self))
        raise ValueError(f"nothing to convert to {obj}")

    def __matmul__(self, obj: str | Self | Any) -> Self:
        """Alias of `<<` for users who prefer `@` syntax."""
        return self << obj

    @staticmethod
    def plaintext(obj: "str | ColorfulStringBuilder") -> str:
        """Return finalized output of a builder with ANSI escape codes removed."""
        if isinstance(obj, ColorfulStringBuilder):
            if obj._status is None and obj._string is not None:
                return ANSI_ESCAPE_RE.sub("", obj._string)
            raise ValueError("nothing to convert to plain text")
        if isinstance(obj, str):
            return ANSI_ESCAPE_RE.sub("", obj)
        raise TypeError(
            f"{ColorfulStringBuilder.plaintext.__name__}() expected a str or "
            f"{ColorfulStringBuilder.__name__} object, got instance of {type(obj)} "
            "instead"
        )

    def ifelse(self, condition: bool) -> Self:
        """Start a two-branch conditional chain.

        The first subsequent value is used when `condition` is true; the second one
        is used otherwise.
        """
        if self._status is not None:
            raise ValueError("duplicated call to ifelse(), iftrue() or ifnot()")
        return self.copy(status=(bool(condition), True))

    def iftrue(self, condition: bool) -> Self:
        """Append next value only when `condition` is true."""
        if self._status is not None:
            raise ValueError("duplicated call to ifelse(), iftrue() or ifnot()")
        return self.copy(string="", status=(not bool(condition), False))

    def ifnot(self, condition: bool) -> Self:
        """Append next value only when `condition` is false."""
        if self._status is not None:
            raise ValueError("duplicated call to ifelse(), iftrue() or ifnot()")
        return self.copy(string="", status=(bool(condition), False))

    def matchcase(self, *conditions: bool) -> Self:
        if len(conditions) == 0:
            raise ValueError("no conditions")
        obj = self
        for cond in conditions:
            obj = obj.ifelse(cond)
        return obj

    def copy(
        self,
        *,
        default_color: str = ...,
        faint: bool = ...,
        underlined: bool = ...,
        string: str | None = ...,
        status: tuple[bool, bool] | None = ...,
        receiver: Self | _DefaultReceiver = ...,
        printer: Callable | None = ...,
    ) -> Self:
        """Return a cloned builder with selected fields overridden."""
        return self.__class__(
            self._default_color if default_color is Ellipsis else default_color,
            self._faint if faint is Ellipsis else faint,
            self._underlined if underlined is Ellipsis else underlined,
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
            if self._underlined and not self._default_color and string:
                string = f"\x1b[4m{string}\x1b[0m"
            else:
                has_default_style = bool(self._default_color or self._underlined)
                if has_default_style and string:
                    string = self.__render_ansi_tokens(string)
                    string = string.replace("$", "$$")
                    token = self._default_color
                    if self._faint and token:
                        if "." in token:
                            token = f"{token[0]}-{token[1:]}"
                        else:
                            token = f"{token}-"
                    if self._underlined:
                        token = f"_{token}"
                    string = f"${token}:{string}$"
            string = self.__render_ansi_tokens(string)
        if self._printer is not None:
            self._printer(repr(self.copy(string=string, status=None)))
        return string

    def __render_ansi_tokens(self, value: str) -> str:
        """Translate `$TOKEN:text$` fragments to ANSI escape codes.

        Valid inline format is `$TOKEN:text$` where `TOKEN` is `FG`, `FG-`,
        `FG.BG`, `FG-.BG`, and can optionally be prefixed by `_` for underline.
        """
        parts: list[str] = []
        active_styles: list[tuple[str, str, int]] = []
        i = 0
        while i < len(value):
            if value[i] != "$":
                parts.append(value[i])
                i += 1
                continue

            if i + 1 < len(value) and value[i + 1] == "$":
                parts.append("$")
                i += 2
                continue

            parsed = self.__parse_inline_token(value, i + 1)
            if parsed is not None:
                style_prefix, marker, marker_index, i = parsed
                parts.append(style_prefix)
                active_styles.append((style_prefix, marker, marker_index))
                continue

            if active_styles:
                active_styles.pop()
                parts.append("\x1b[0m")
                if active_styles:
                    parts.append("".join(style for style, _, _ in active_styles))
                i += 1
                continue

            raise ValueError(
                f"invalid inline token expression at index {i}: expected a closing '$' "
                "or a token opener in the form $TOKEN:text$"
            )

        if active_styles:
            opened_segments = ", ".join(
                f"'{marker}' at index {marker_index}"
                for _, marker, marker_index in active_styles
            )
            raise ValueError(
                "missing closing '$' for one or more "
                f"opened $TOKEN:text$ segments ({opened_segments})"
            )

        return "".join(parts)

    def __parse_inline_token(
        self, value: str, start: int
    ) -> tuple[str, str, int, int] | None:
        """Parse a token starting at ``start`` (right after ``$``)."""
        token_chars: list[str] = []
        j = start
        while j < len(value):
            if value[j] == ":":
                break
            if value[j] == "$":
                return None
            token_chars.append(value[j])
            j += 1

        if j >= len(value) or value[j] != ":":
            return None

        token = "".join(token_chars)
        underlined = token.startswith("_")
        if underlined:
            token = token[1:]

        fg_token = token[:1].upper()
        if fg_token not in ANSI_TOKEN_COLORS:
            raise ValueError(
                f"invalid inline token '{token}': invalid foreground color field"
            )

        parsed_end = 1
        faint = False
        if len(token) > parsed_end and token[parsed_end] == "-":
            faint = True
            parsed_end += 1

        bg_token = ""
        if len(token) > parsed_end and token[parsed_end] == ".":
            if len(token) <= parsed_end + 1:
                raise ValueError(
                    f"invalid inline token '{token}': missing background color field"
                )
            bg_token = token[parsed_end + 1 : parsed_end + 2].upper()
            if bg_token not in ANSI_TOKEN_COLORS:
                raise ValueError(
                    f"invalid inline token '{token}': invalid background color field"
                )
            parsed_end += 2

        if parsed_end != len(token):
            if "_" in token:
                raise ValueError("underline marker '_' must be before foreground color")
            raise ValueError(
                f"invalid inline token '{token}': unexpected characters after color fields"
            )

        prefix_parts: list[str] = []
        if underlined:
            prefix_parts.append("\x1b[4m")

        fg_base_code = int(ANSI_TOKEN_COLORS[fg_token][2:4])
        if faint:
            prefix_parts.append(f"\x1b[2;{fg_base_code}m")
        else:
            prefix_parts.append(ANSI_TOKEN_COLORS[fg_token])

        if bg_token:
            bg_code = f"\x1b[{int(ANSI_TOKEN_COLORS[bg_token][2:4]) + 10}m"
            prefix_parts.append(bg_code)

        marker = f"${''.join(token_chars)}:"
        return "".join(prefix_parts), marker, start - 1, j + 1

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

    def __with_color_token(self, token: str) -> Self:
        """Set foreground token or one background token (at most two chained colors)."""
        if not self._default_color:
            return self.copy(default_color=token)
        if "." not in self._default_color:
            return self.copy(default_color=f"{self._default_color}.{token}")
        raise ValueError("only two chained colors are supported, e.g. c.b.g")

    @property
    def underline(self) -> Self:
        """Return a builder that applies underline formatting."""
        return self.copy(underlined=True)

    @property
    def faint(self) -> Self:
        """Return a builder that applies faint foreground color."""
        return self.copy(faint=True)

    @property
    def d(self) -> Self:
        """Return a builder with dark/black default color."""
        return self.__with_color_token("D")

    @property
    def r(self) -> Self:
        """Return a builder with red default color."""
        return self.__with_color_token("R")

    @property
    def g(self) -> Self:
        """Return a builder with green default color."""
        return self.__with_color_token("G")

    @property
    def y(self) -> Self:
        """Return a builder with yellow default color."""
        return self.__with_color_token("Y")

    @property
    def b(self) -> Self:
        """Return a builder with blue default color."""
        return self.__with_color_token("B")

    @property
    def p(self) -> Self:
        """Return a builder with purple default color."""
        return self.__with_color_token("P")

    @property
    def c(self) -> Self:
        """Return a builder with cyan default color."""
        return self.__with_color_token("C")

    @property
    def w(self) -> Self:
        """Return a builder with white default color."""
        return self.__with_color_token("W")


c = ColorfulStringBuilder()
