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

You can chain them for background presets, e.g. `c.b.g` means blue foreground + green background.

Chaining is limited to two colors; `c.b.g.g` is not allowed.

```python
print(c.y << "Warning")
print(c.b.g << "Blue on green via chaining")
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

### 5) Underline

Use `.underline` to add underline style:

```python
print(c.underline << "plain underline")
print(c.underline.g << "green underline")
print(c.underline.g.b << "green on blue underline")
```



### 6) Light/Faint Foreground

Use `.faint` to switch the foreground to a faint ANSI variant (`\033[2;COLORm`). It must follow the foreground color token.

```python
print(c.r.faint << "faint red")
print(c.g.faint.b << "faint green on blue")
```

### 7) Inline Token Grammar

Besides fluent chaining, `colorfulstring` can also parse inline token fragments from plain strings:

```python
print(c("$R:error$"))
print(c("$G-.B:faint green on blue$"))
print(c("$_Y:underlined yellow$"))
```

Grammar (inside `$...$`):

- `TOKEN:text`
- `TOKEN`:
  - `FG` (foreground), e.g. `R`, `G`, `B`
  - `FG-` (faint foreground)
  - `FG.BG` (foreground + background)
  - `FG-.BG` (faint foreground + background)
  - optional underline prefix: `_${TOKEN}`

Escaping:

- `$$` becomes a literal `$`.
- Non-token fragments keep their original form, e.g. `$hello$` stays `$hello$`.

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
