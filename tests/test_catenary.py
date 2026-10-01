"""Reference cases, force equilibrium, and input validation."""

from dataclasses import FrozenInstanceError
import math
import unittest

from catenary import Catenary


class CatenaryTests(unittest.TestCase):
    def assertClose(self, actual, expected, relative=1e-9):
        self.assertTrue(math.isclose(actual, expected, rel_tol=relative),
                        f"{actual} != {expected}")

    def test_reference_span_and_length(self):
        cable = Catenary(span=20, cable_length=21, weight_per_length=100)
        self.assertClose(cable.a, 18.3927926007)
        self.assertClose(cable.sag, 2.78608413184)
        self.assertClose(cable.horizontal_tension, 1839.27926007)
        self.assertClose(cable.support_angle, 0.518729302609)
        self.assertClose(cable.support_tension, 2117.88767326)
        self.assertClose(cable.minimum_tension, cable.horizontal_tension)

    def test_span_and_sag(self):
        cable = Catenary(span=20, sag=2.78608413184, weight_per_length=100)
        self.assertClose(cable.a, 18.3927926007)
        self.assertClose(cable.cable_length, 21)

    def test_span_and_a(self):
        cable = Catenary(span=20, a=18.3927926007, weight_per_length=100)
        self.assertClose(cable.cable_length, 21)
        self.assertClose(cable.sag, 2.78608413184)

    def test_tension_and_weight_without_geometry(self):
        cable = Catenary(horizontal_tension=2000, weight_per_length=100)
        self.assertEqual(cable.a, 20)
        self.assertEqual(cable.minimum_tension, 2000)
        for name in ("span", "sag", "cable_length", "support_angle",
                     "vertical_support_force", "support_tension"):
            self.assertIsNone(getattr(cable, name))

    def test_tension_and_weight_with_span(self):
        cable = Catenary(span=20, horizontal_tension=1839.27926007,
                         weight_per_length=100)
        self.assertClose(cable.cable_length, 21)

    def test_recover_span_from_length_or_sag_with_a(self):
        for geometry in ({"cable_length": 21}, {"sag": 2.78608413184}):
            with self.subTest(geometry=geometry):
                cable = Catenary(a=18.3927926007, **geometry)
                self.assertClose(cable.span, 20)

    def test_support_equilibrium(self):
        cable = Catenary(span=20, cable_length=21, weight_per_length=100)
        self.assertClose(2 * cable.vertical_support_force, 2100)
        self.assertClose(cable.support_tension * math.cos(cable.support_angle),
                         cable.horizontal_tension)
        self.assertClose(cable.support_tension * math.sin(cable.support_angle),
                         cable.vertical_support_force)

    def test_geometry_without_force_scale(self):
        cable = Catenary(span=20, cable_length=21)
        self.assertClose(cable.sag, 2.78608413184)
        for name in ("weight_per_length", "horizontal_tension", "minimum_tension",
                     "vertical_support_force", "support_tension"):
            self.assertIsNone(getattr(cable, name))

    def test_recover_weight_from_tension(self):
        cable = Catenary(span=20, a=18.3927926007,
                         horizontal_tension=1839.27926007)
        self.assertClose(cable.weight_per_length, 100)

    def test_consistent_redundant_inputs(self):
        cable = Catenary(span=20, cable_length=21, sag=2.78608413184,
                         a=18.3927926007, weight_per_length=100,
                         horizontal_tension=1839.27926007)
        self.assertClose(cable.vertical_support_force, 1050)

    def test_contradictory_inputs(self):
        cases = [
            {"span": 20, "cable_length": 21, "sag": 4},
            {"span": 20, "cable_length": 21, "a": 10},
            {"span": 20, "a": 10, "sag": 1},
            {"a": 20, "horizontal_tension": 1000, "weight_per_length": 100},
        ]
        for inputs in cases:
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                Catenary(**inputs)

    def test_invalid_inputs(self):
        for name in ("span", "cable_length", "sag", "a",
                     "horizontal_tension", "weight_per_length"):
            for value in (0, -1, math.inf, -math.inf, math.nan, True, "20"):
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    Catenary(**{name: value})
        for length in (19, 20):
            with self.subTest(length=length), self.assertRaises(ValueError):
                Catenary(span=20, cable_length=length)

    def test_insufficient_inputs(self):
        for inputs in ({}, {"span": 20}, {"a": 20},
                       {"span": 20, "weight_per_length": 100}):
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                Catenary(**inputs)

    def test_shallow_cable(self):
        # First-order shallow-cable approximation: sag = L^2/(8*a).
        cable = Catenary(span=20, sag=1e-7)
        self.assertClose(cable.a, 20**2 / (8e-7))
        self.assertClose(cable.sag, 1e-7)

    def test_deep_cable_bracket_expansion(self):
        # u = L/(2*a) = 10 requires expanding the initial bracket.
        cable = Catenary(span=20, sag=math.cosh(10) - 1)
        self.assertClose(cable.a, 1)
        from_length = Catenary(span=20, cable_length=2 * math.sinh(10))
        self.assertClose(from_length.a, 1)

    def test_extreme_inputs_fail_clearly(self):
        for inputs in ({"span": 20, "a": 1e-300},
                       {"span": 1e-300, "sag": 1e300},
                       {"horizontal_tension": 1e300, "weight_per_length": 1e-300}):
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                Catenary(**inputs)

    def test_immutable_results(self):
        cable = Catenary(span=20, a=10)
        with self.assertRaises(FrozenInstanceError):
            cable.span = 30


if __name__ == "__main__":
    unittest.main()
