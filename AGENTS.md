AGENTS.md

Project purpose

This project is a small technical Python library for solving catenary problems.

The main goal is to make catenary calculations understandable, transparent, and reusable.

The library should allow a user to provide a sufficient combination of known parameters, such as:

* span
* cable length
* sag
* catenary parameter a
* weight per unit length
* horizontal tension

The program should then calculate all other quantities that can be uniquely determined.

The project is intended both as:

1. a practical engineering calculation tool, and
2. an educational tool that makes the underlying mechanics and mathematics easy to understand.

The project may eventually be published publicly on GitHub and should therefore use English for:

* source code
* class names
* variable names
* comments
* documentation
* tests

⸻

Core engineering model

The first version of the project should focus on a symmetric catenary between two supports at the same elevation.

The basic catenary equation is:

y = a * (cosh(x / a) - 1)

with the lowest point of the cable at:

x = 0
y = 0

Important relations include:

a = H / w

where:

* a = catenary parameter [m]
* H = horizontal component of cable tension [N]
* w = cable weight per unit cable length [N/m]

Cable length for a symmetric span:

S = 2 * a * sinh(L / (2 * a))

Sag:

f = a * (cosh(L / (2 * a)) - 1)

The program may use numerical root finding when a parameter cannot be isolated algebraically.

Numerical solutions are not a workaround. They are a normal and intended part of the project.

⸻

Main class

The main public class should be called:

Catenary

Typical construction should look like:

cable = Catenary(
    span=20.0,
    cable_length=21.0,
    weight_per_length=100.0,
)

The object should calculate all additional quantities that can be determined from the supplied data.

Examples of properties may include:

* span
* cable_length
* sag
* a
* weight_per_length
* horizontal_tension
* support_angle
* vertical_support_force
* support_tension
* minimum_tension

Names may be improved if there is a clear engineering reason, but terminology should remain conventional and easy to understand.

⸻

Design principles

Keep the implementation simple.

Prefer clear engineering logic over clever software abstractions.

The code should be readable by an engineer who understands mechanics but is not a professional software developer.

Do not introduce additional frameworks, architectural layers, design patterns, or dependencies unless they solve a real current problem.

Avoid premature generalization.

For example, do not immediately build a general cable-network solver, finite-element model, GUI, web application, or optimization framework.

First make the basic Catenary class correct and understandable.

⸻

Numerical methods

Some combinations of input parameters require numerical root solving.

Use a robust and understandable method.

A simple bisection method is acceptable for the first implementation.

SciPy may be considered later, but the basic library should preferably avoid unnecessary external dependencies.

Numerical algorithms should:

* check that a valid solution is bracketed
* use reasonable tolerances
* fail clearly if the supplied parameters cannot produce a physical solution
* never silently return an invalid result

Where practical, explain in comments why numerical solving is necessary.

⸻

Physical validation

Input data must be checked for physical consistency.

Examples:

* cable length cannot be shorter than the straight-line distance between supports
* span must be positive
* weight per unit length must be positive
* a must be positive
* sag must be positive for the current symmetric hanging-cable model

If the user provides redundant parameters, the program should eventually be able to check whether they are mutually consistent.

Do not silently overwrite contradictory user input.

⸻

Units

Use SI units internally.

Expected units:

* length: metres
* force: newtons
* weight per unit length: newtons per metre
* angles: radians internally, degrees only where explicitly presented to users

Do not build a full unit-handling system in the first version.

Document expected units clearly.

⸻

Code style

Prefer:

* short functions
* descriptive names
* explicit calculations
* type hints where useful
* docstrings for public methods and properties
* conventional Python formatting

Avoid:

* unnecessary inheritance
* deeply nested logic
* hidden state changes
* cryptic mathematical variable names except where they are established engineering notation such as a, H, w, L, and S

Internal formulas may use mathematical notation in comments, but public API names should be descriptive.

⸻

Tests

Every important physical relation should have tests.

At minimum, test:

1. solving from span + cable length
2. solving from span + sag
3. solving from span + a
4. solving from horizontal tension + weight per length
5. calculation of support forces
6. impossible input combinations
7. consistency of redundant input data

Use simple reference examples whose results can also be checked manually.

A useful initial reference case is:

* span = 20 m
* cable length = 21 m
* weight per length = 100 N/m

Expected approximate values:

* a ≈ 18.4 m
* sag ≈ 2.8 m
* horizontal tension ≈ 1.84 kN
* support angle ≈ 30 degrees
* support tension ≈ 2.12 kN

Tests should use tolerances rather than demand exact floating-point equality.

⸻

Documentation

The README should explain:

* what a catenary is
* what the library calculates
* which inputs can be supplied
* one simple example
* the underlying equations
* when numerical solving is required

Documentation should favor understanding over mathematical formality.

A reader should be able to understand both what the program does and why.

⸻

How the coding agent should work

Before making a substantial change:

1. understand the current engineering model
2. identify the smallest change needed
3. preserve existing behavior unless a change is intentional
4. explain any change that affects the mathematical model or public API
5. run relevant tests

Do not make unrelated improvements simply because they appear useful.

Do not rename public concepts, restructure the whole project, or add new dependencies without a clear reason.

If there are several reasonable implementation choices, prefer the simplest one and state the alternative briefly.

The engineering model has priority over software elegance.

⸻

Current scope

For now, the project is limited to:

* static catenary
* flexible cable
* self-weight distributed uniformly per unit cable length
* two supports
* equal support elevation
* symmetric geometry

Possible future extensions include:

* supports at different elevations
* additional distributed loads
* temperature effects
* elastic cable extension
* prescribed pretension
* plotting
* engineering design checks

These are future possibilities, not current requirements.

Do not implement them unless explicitly requested.

⸻

Guiding principle

The project should remain small enough that the complete physical model can be understood by reading the source code.

When choosing between a sophisticated solution and a transparent solution that is sufficiently accurate and robust, prefer the transparent solution.