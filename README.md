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

## Usage

### 1) Color Shortcuts

Available shortcut color properties are `d/r/g/y/b/p/c/w` (dark/red/green/yellow/blue/purple/cyan/white).

You can chain them for background presets, e.g. `c.b.g` means blue foreground + green background (same as `$B.G`).

Chaining is limited to two colors; `c.b.g.g` is not allowed.

Background syntax supports `$FG.BG` (foreground.background), for example `$B.G` means blue text on green background.

Background helper properties are also available: `bg_black`, `bg_red`, `bg_green`, `bg_yellow`, `bg_blue`, `bg_purple`, `bg_cyan`, `bg_white`.

```python
print(c.y << "Warning")
print(c.b.g << "Blue on green via chaining")
```

```python
print(c << "$B.GBlue on green$")
print(c << "$D.YDark on yellow$")
print(c.bg_blue << "Blue background preset")
```

### 2) Pipe-Style Chaining

Use `<<` (or `@`) to append fragments in sequence:

```python
print(c.b << "[INFO]" << " service started")
```

### 3) Conditional Output

- `iftrue(condition)`: include the next fragment only when `condition` is `True`.
- `ifnot(condition)`: include the next fragment only when `condition` is `False`.
- `ifelse(condition)`: choose between the next two fragments.

```python

ok = True
line = c << "status: " << c.ifelse(ok) << c.g("success") << c.r("failed")
print(line)
```

### 4) Immediate Printing

`c.print` outputs each generated fragment immediately (without an automatic newline). It can be combined with `c.endl`.

```python
line = c.print << "hello" << c.endl
```

## See Also
### Github repository
* https://github.com/Chitaoji/colorfulstring/

### PyPI project
* https://pypi.org/project/colorfulstring/


## License
BSD 3-Clause License.

## History
### v0.0.1
* Renamed `ColorfulString` to `ColorfulStringBuilder` to avoid conflicts.

### v0.0.0
* Initial release.
