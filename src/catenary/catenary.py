"""Geometry and forces for a cable hanging under its own weight."""

from dataclasses import dataclass, field
import math


def _length_excess(u: float) -> float:
    """Return sinh(u)/u - 1 without cancellation for shallow cables."""
    if u < 0.01:
        squared = u * u
        return squared * (1 / 6 + squared * (1 / 120 + squared / 5040))
    return math.sinh(u) / u - 1


def _sag_ratio(u: float) -> float:
    """Return sag/span, using cosh(u)-1 = 2*sinh(u/2)**2."""
    return math.sinh(u / 2) ** 2 / u


def _bisect(function, target: float) -> float:
    """Solve a positive, increasing dimensionless relation by bisection."""
    lower, upper = 0.0, 1.0
    # Both geometry relations increase from zero. Expand until bracketed.
    while function(upper) < target:
        # u <= 700 keeps the hyperbolic expressions below float overflow.
        if upper == 700.0:
            raise ValueError("Geometry exceeds the supported numerical range")
        upper = min(2 * upper, 700.0)
    # Allow enough halvings to reach very small roots near float underflow.
    for _ in range(1100):
        midpoint = (lower + upper) / 2
        value = function(midpoint)
        if math.isclose(value, target, rel_tol=1e-12, abs_tol=0.0):
            return midpoint
        if midpoint == lower or midpoint == upper:
            break
        if value < target:
            lower = midpoint
        else:
            upper = midpoint
    raise ValueError("Geometry solver did not converge within numerical precision")


@dataclass(frozen=True, kw_only=True)
class Catenary:
    """A symmetric, flexible cable between supports at equal elevation.

    Supply span with cable_length, sag, or a; alternatively supply
    horizontal_tension and weight_per_length to determine a alone.
    Lengths are metres, forces newtons, weight_per_length N/m, and
    support_angle radians above horizontal (positive magnitude).
    vertical_support_force is the upward reaction at each support.
    Quantities that cannot be determined remain None. Redundant inputs
    must agree within relative tolerance 1e-9 or absolute tolerance 1e-12
    in their respective SI units. Instances are immutable.
    """

    span: float | None = None
    cable_length: float | None = None
    sag: float | None = None
    a: float | None = None
    weight_per_length: float | None = None
    horizontal_tension: float | None = None
    support_angle: float | None = field(default=None, init=False)
    vertical_support_force: float | None = field(default=None, init=False)
    support_tension: float | None = field(default=None, init=False)
    minimum_tension: float | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self._validate_inputs()
        try:
            parameter = self._solve_parameter()
            self._solve_geometry(parameter)
            self._solve_forces(parameter)
        except (OverflowError, ZeroDivisionError) as error:
            raise ValueError("Inputs exceed the supported numerical range") from error

    def _validate_inputs(self) -> None:
        """Check input values and basic physical constraints before solving."""
        inputs = {
            name: getattr(self, name)
            for name in ("span", "cable_length", "sag", "a",
                         "weight_per_length", "horizontal_tension")
        }
        for name, value in inputs.items():
            if value is not None:
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise ValueError(f"{name} must be a finite positive number")
                if not math.isfinite(value) or value <= 0:
                    raise ValueError(f"{name} must be a finite positive number")

        span, length, sag = self.span, self.cable_length, self.sag
        weight, horizontal = self.weight_per_length, self.horizontal_tension
        if (span is None and length is None and sag is None
                and weight is None and horizontal is None):
            raise ValueError("Supply geometry or a force scale in addition to a")
        if span is not None and length is not None and length <= span:
            raise ValueError("cable_length must exceed span for a hanging cable")

    def _solve_parameter(self) -> float:
        """Determine a from supplied a, force ratio, or span and geometry."""
        parameter = self.a
        span, length, sag = self.span, self.cable_length, self.sag
        weight, horizontal = self.weight_per_length, self.horizontal_tension
        if parameter is None and horizontal is not None and weight is not None:
            parameter = horizontal / weight
        if parameter is None and span is not None:
            # a cannot be isolated algebraically from length or sag.
            if length is not None:
                u = _bisect(_length_excess, (length - span) / span)
                parameter = span / (2 * u)
            elif sag is not None:
                u = _bisect(_sag_ratio, sag / span)
                parameter = span / (2 * u)
        if parameter is None:
            raise ValueError("Supply span with cable_length, sag, or a, "
                             "or horizontal_tension with weight_per_length")
        self._set_result("a", parameter)
        return parameter

    def _solve_geometry(self, parameter: float) -> None:
        """Determine span when possible, then calculate length, sag, and angle."""
        span, length, sag = self.span, self.cable_length, self.sag
        if span is None:
            if length is not None:
                span = 2 * parameter * math.asinh(length / (2 * parameter))
            elif sag is not None:
                span = 4 * parameter * math.asinh(math.sqrt(sag / parameter / 2))
        if span is not None:
            self._set_result("span", span)
            u = span / (2 * parameter)
            self._set_result("cable_length", span * (1 + _length_excess(u)))
            self._set_result("sag", span * _sag_ratio(u))
            self._set_result("support_angle", math.atan(math.sinh(u)))

    def _solve_forces(self, parameter: float) -> None:
        """Resolve H = a*w, then calculate minimum tension and support forces."""
        weight, horizontal = self.weight_per_length, self.horizontal_tension
        if horizontal is None and weight is not None:
            horizontal = parameter * weight
        if weight is None and horizontal is not None:
            weight = horizontal / parameter
        if weight is not None:
            self._set_result("weight_per_length", weight)
        if horizontal is not None:
            self._set_result("horizontal_tension", horizontal)
            if weight is not None and not math.isclose(
                horizontal, parameter * weight, rel_tol=1e-9, abs_tol=1e-12
            ):
                raise ValueError("horizontal_tension contradicts a and weight_per_length")
            self._set_result("minimum_tension", horizontal)
            if self.cable_length is not None and weight is not None:
                vertical = weight * (self.cable_length / 2)
                self._set_result("vertical_support_force", vertical)
                self._set_result("support_tension", math.hypot(horizontal, vertical))

    def _set_result(self, name: str, value: float) -> None:
        """Validate a calculated result and check any redundant input."""
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"Calculated {name} is outside the supported numerical range")
        supplied = getattr(self, name)
        if supplied is not None and not math.isclose(
            supplied, value, rel_tol=1e-9, abs_tol=1e-12
        ):
            raise ValueError(f"{name} contradicts the other supplied parameters")
        object.__setattr__(self, name, value)
