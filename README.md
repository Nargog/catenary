# catenary

A small Python library for a symmetric catenary: the curve formed by a flexible
cable hanging under its own weight between two supports at equal elevation.
Weight is uniform per unit cable length. The library has no runtime dependencies.

## Usage

```python
from catenary import Catenary

cable = Catenary(span=20.0, cable_length=21.0, weight_per_length=100.0)
print(cable.a)                       # 18.3928 m approximately
print(cable.sag)                     # 2.7861 m
print(cable.horizontal_tension)      # 1839.28 N
print(cable.vertical_support_force)  # 1050 N at each support
print(cable.support_tension)         # 2117.89 N at each support
```

Supply `span` with `cable_length`, `sag`, or `a`. Adding `weight_per_length`
determines the forces; adding `horizontal_tension` instead determines the weight
per length and forces. `horizontal_tension` with `weight_per_length` determines
`a` and `minimum_tension`; add a span, cable length, or sag to determine geometry.
Known `a` with cable length or sag also determines span.

Lengths are in metres, forces in newtons, and weight per length in N/m.
`support_angle` is the positive angle above horizontal in radians. The vertical
support force is the upward reaction at **each** support; minimum tension occurs
at the lowest point and equals horizontal tension.

All inputs are keyword-only, finite, and positive. Cable length must exceed span:
a perfectly straight cable has no finite hanging-catenary solution in this model.
Insufficient or contradictory inputs raise `ValueError`. Quantities that cannot
be uniquely determined remain `None`; geometry alone does not determine forces.
Results are immutable so changing an input cannot leave stale calculations.
Redundant inputs are checked with relative tolerance `1e-9` and absolute tolerance
`1e-12` in their respective SI units. Accepted values are normalized to the
calculated solution within that tolerance.

## Equations

With the lowest point at `(0, 0)`, the cable follows
`y = a * (cosh(x/a) - 1)`. For span `L`, length `S`, sag `f`, horizontal
tension `H`, and weight per cable length `w`:

```text
a = H / w
S = 2*a*sinh(L/(2*a))
f = a*(cosh(L/(2*a)) - 1)
support_angle = atan(sinh(L/(2*a)))
vertical_support_force = w*S/2
support_tension = sqrt(H**2 + (w*S/2)**2)
minimum_tension = H
```

Given span and length or sag, `a` cannot be isolated algebraically. The library
solves for `u = L/(2*a)` using bracket expansion followed by bisection, with a
relative residual tolerance of `1e-12`. Small-argument formulas avoid subtracting
nearly equal numbers for shallow cables. Inputs outside floating-point range or
solutions that do not converge raise `ValueError`.

The scope is static self-weight loading, flexible cable, and equal support
elevations. Elasticity, other loads, and unequal support heights are not modeled.

## Project structure

```text
src/catenary/      Python package
tests/            Standard-library unittest tests
README.md         Project documentation
pyproject.toml    Package metadata and build configuration
.gitignore        Files excluded from version control
```

## Development

Requires Python 3.10 or newer. From the project root:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

After installation, run the standard-library tests:

```sh
python -m unittest discover -s tests
```

Alternatively, run from the checkout without installing:

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
```
