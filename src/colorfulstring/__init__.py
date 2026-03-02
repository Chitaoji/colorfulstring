"""Public package API for `colorfulstring`.

`colorfulstring` offers a fluent API for composing ANSI-colored strings in terminals.
Most users only need the exported singleton `c`:

>>> from colorfulstring import c
>>> print(c.g << "done")

"""

from . import core
from ._version import __version__
from .core import *

__all__: list[str] = []
__all__.extend(core.__all__)
