# colorfulstring

`colorfulstring` is a lightweight Python utility for building ANSI-colored terminal strings with a fluent, chainable API.

## Installation

```bash
pip install colorfulstring
```

## Quick Start

```python
from colorfulstring import c

print(c.r << "Error:" << " something went wrong")
print(c.g("OK"))
```

## Core Usage

### 1) Color Shortcuts

Available color properties are `d/r/g/y/b/p/c/w`, which map to dark, red, green, yellow, blue, purple, cyan, and white.

```python
from colorfulstring import c

msg = c.y << "Warning"
print(msg)
```

### 2) Pipe-Style Chaining

Use `<<` (or `@`) to append fragments in sequence:

```python
from colorfulstring import c

line = c.b << "[INFO]" << " service started"
print(line)
```

### 3) Conditional Output

- `iftrue(condition)`: include the next fragment only when `condition` is `True`.
- `ifnot(condition)`: include the next fragment only when `condition` is `False`.
- `ifelse(condition)`: choose between the next two fragments.

```python
from colorfulstring import c

ok = True
line = c << "status: " << c.ifelse(ok) << c.g("success") << c.r("failed")
print(line)
```

### 4) Immediate Printing

`.print` outputs each generated fragment immediately (without an automatic newline). It can be combined with `.endl`.

```python
from colorfulstring import c

c.print.r("hello")
c.print.endl
```

## See Also

- GitHub: https://github.com/Chitaoji/colorfulstring/
- PyPI: https://pypi.org/project/colorfulstring/

## License

BSD 3-Clause License.
