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
