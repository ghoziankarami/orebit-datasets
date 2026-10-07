"""Synthetic strike-oriented prospect footprint, not a geological resource solid."""

import math

WIDTH, HEIGHT = 1900.0, 1500.0
ANGLE = math.radians(37.0)


def strike_coordinates(x, y):
    dx, dy = x - WIDTH / 2, y - HEIGHT / 2
    return dx * math.cos(ANGLE) + dy * math.sin(ANGLE), -dx * math.sin(
        ANGLE
    ) + dy * math.cos(ANGLE)


def inside_prospect(x, y):
    u, v = strike_coordinates(x, y)
    centre = 65 * math.sin(u / 310)
    flank = 490 * (0.88 + 0.11 * math.sin(u / 210) + 0.08 * math.cos(u / 370))
    return (u / 1030) ** 2 + ((v - centre) / flank) ** 2 <= 1


def place_collar(planned, rng, slope, placed):
    """Synthetic field siting near a planned pad, preferring gentler terrain.

    Retain regional/infill intent without implying that a real field crew can
    drill a perfect lattice. Position errors are not geological uncertainty.
    """
    candidates = []
    x, y = planned
    for _ in range(24):
        dx, dy = rng.normal(0, 18, 2)
        point = (float(x + dx), float(y + dy))
        distance = math.hypot(dx, dy)
        if distance > 44 or not inside_prospect(*point):
            continue
        if any(math.dist(point, previous) < 20 for previous in placed):
            continue
        # Field access and departure from the planned target both matter.
        score = float(slope(*point)) + 0.04 * distance
        candidates.append((score, point))
    if not candidates:
        raise ValueError("No safe synthetic collar position near planned pad")
    return min(candidates, key=lambda value: value[0])[1]


def drill_nodes(count=350):
    regional = {
        (float(x), float(y))
        for x in range(50, 1900, 100)
        for y in range(50, 1500, 100)
        if inside_prospect(x, y)
    }
    infill = {
        (float(x), float(y))
        for x in range(50, 1900, 50)
        for y in range(50, 1500, 50)
        if inside_prospect(x, y)
    } - regional

    # Infill follows the central prospect, rather than occupying a rectangular block.
    def priority(p):
        u, v = strike_coordinates(*p)
        return abs(u) / 600 + abs(v - 65 * math.sin(u / 310)) / 260, p[1], p[0]

    needed = count - len(regional)
    if needed < 0 or needed > len(infill):
        raise ValueError(
            "Requested count cannot retain the regional footprint and infill programme"
        )
    return sorted(
        regional | set(sorted(infill, key=priority)[:needed]),
        key=lambda p: (p[1], p[0]),
    )
