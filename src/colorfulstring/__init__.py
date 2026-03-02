"""
# colorfulstring
A template repository for building python packages.

## See Also
### Github repository
* https://github.com/Chitaoji/colorfulstring/

### PyPI project
* https://pypi.org/project/colorfulstring/

## License
This project falls under the BSD 3-Clause License.

"""

from . import core
from ._version import __version__
from .core import *

__all__: list[str] = []
__all__.extend(core.__all__)
