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

Chaining is limited to two colors; `c.b.g.r` is not allowed.

```python
print(c.y << "Warning")
print(c.b.g << "Blue on green via chaining")
```

### 2) Pipe-Style Chaining

Use `<<` (or `@`) to append fragments in sequence:

```python
print(c.b << "[INFO]" << " service started")
```

Use `>>` to convert a finished builder:

- `builder >> str`: finalize as a regular Python string (same as `str(builder)`).
- `builder >> c.plain_text`: finalize and strip ANSI escape codes.

```python
ansi = c.r << "Error" >> str
plain = c.r << "Error" >> c.plain_text
```

### 3) `c()` Shortcut

`c(text)` immediately converts one fragment using the current style context and returns a string.

```python
print(c.r("error"))
print(c.underline.g("underlined green"))
```

### 4) Conditional Output

- `iftrue(condition)`: include the next fragment only when `condition` is `True`.
- `ifnot(condition)`: include the next fragment only when `condition` is `False`.
- `ifelse(condition)`: choose between the next two fragments.

```python

ok = True
line = c << "status: " << c.ifelse(ok) << c.g("success") << c.r("failed")
print(line)
```

### 5) Immediate Printing

`c.print` outputs each generated fragment immediately (without an automatic newline). It can be combined with `c.endl`.

```python
line = c.print << "hello" << c.endl
```

### 6) Underline

Use `.underline` to add underline style:

```python
print(c.underline << "plain underline")
print(c.underline.g << "green underline")
print(c.underline.g.b << "green on blue underline")
```

### 7) Faint Foreground

Use `.faint` to switch the foreground to a faint ANSI variant. 

```python
print(c.faint.r << "faint red")
print(c.faint.underline.g.b << "faint green on blue underline")
```

Note: 

- `c.faint` is no different from `c`, if you need a faint dark color, try `c.faint.d`. 

### 8) Inline Token Grammar

Besides fluent chaining, `colorfulstring` can also parse inline token fragments from plain strings:

```python
print(c << "$R:error$")
print(c << "$G-.B:faint green on blue$")
print(c << "$_Y:underlined yellow$")
```

Grammar (inside `$...$`):

- `TOKEN:text`
- `TOKEN`:
  - `FG` (foreground), e.g. `R`, `G`, `B`
  - `FG-` (faint foreground)
  - `FG.BG` (foreground + background)
  - `FG-.BG` (faint foreground + background)
  - optional underline prefix: `_{TOKEN}`

Escaping:

- Only `$$` is treated as an escaped dollar sign (`$`).
- Any `$...$` fragment that is not a valid token expression raises `ValueError`.
- A single unmatched `$` is treated as an error and raises `ValueError`.

## See Also
### Github repository
* https://github.com/Chitaoji/colorfulstring/

### PyPI project
* https://pypi.org/project/colorfulstring/


## License
This project falls under the BSD 3-Clause License.

## History
### v0.0.6
* Added `builder >> c.plain_text` / `c.plain_text(...)` support to strip ANSI escape sequences from finalized output.

### v0.0.5
* Improved inline token parsing diagnostics with clearer `ValueError` messages for malformed token expressions.
* Added strict handling for unmatched single `$` markers and now raises explicit errors instead of silently accepting invalid input.
* Fixed token rendering order so inline token fragments are interpreted before default style wrapping in chained color contexts.

### v0.0.4
* Removed unnecessary imports.

### v0.0.3
* Now correctly handles escaped dollar sequences like `$$` in inline token parsing.
* Improved README structure and polished API usage descriptions.

### v0.0.2
* Added inline token grammar support (`$TOKEN:text$`) to render ANSI styles directly from plain strings.
* Added `.underline` and `.faint` style modifiers, including combinations with foreground/background colors.
* Improved chaining/conditional flow documentation and examples (`iftrue`, `ifnot`, `ifelse`, `<<`, `@`).

### v0.0.1
* Renamed `ColorfulString` to `ColorfulStringBuilder` to avoid conflicts.

### v0.0.0
* Initial release.
