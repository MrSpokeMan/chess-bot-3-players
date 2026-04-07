"""Coordinate system for a flat regular-hex 3-player board.

Construction:
- Outer boundary is a regular hexagon with flat top and bottom edges.
- Player bases lie on edges 1, 3, 5; gap edges are 2, 4, 6.
- The board is divided into 6 bilinear quadrilaterals (two per player).
- Each logical 4x4 section maps into one quadrilateral.
"""

from __future__ import annotations

import math

from chess_3.coords import Coord

CELL_SIZE = 56
BOARD_CENTER = (640, 400)
S_ROTATIONS: list[float] = [0.0, 60.0, 120.0, 180.0, 240.0, 300.0]

ROWS_PER_SECTION = 4
COLS_PER_SECTION = 4

# Circumradius of the outer regular hexagon.
HEX_RADIUS = CELL_SIZE * 4.0


class CoordSystem:
    """Converts between board coordinates and pixel positions."""

    def __init__(self, width: int = 1280, height: int = 800) -> None:
        self._center_x = float(BOARD_CENTER[0])
        self._center_y = float(BOARD_CENTER[1])
        self._hex_radius = float(HEX_RADIUS)
        self._label_offset = 40.0
        self.set_viewport(width, height)

    def set_viewport(self, width: int, height: int) -> None:
        """Recompute board geometry to fill the available viewport."""
        self._center_x = width * 0.5
        self._center_y = height * 0.47
        self._hex_radius = max(150.0, min(width * 0.34, height * 0.42))
        self._label_offset = max(24.0, self._hex_radius * 0.12)

    def board_center(self) -> tuple[float, float]:
        return self._center_x, self._center_y

    def label_offset(self) -> float:
        return self._label_offset

    def coord_to_pixel(self, coord: Coord) -> tuple[int, int]:
        """Return the center pixel (x, y) of a board cell."""
        p00, p10, p01, p11 = self._section_quad(coord.section)
        u, v = _cell_uv(coord.row, coord.col)
        x, y = _bilinear_quad(p00, p10, p01, p11, u, v)
        return int(round(x)), int(round(y))

    def cell_corners(self, coord: Coord) -> list[tuple[float, float]]:
        """Return four polygon corners for a board cell in draw order."""
        p00, p10, p01, p11 = self._section_quad(coord.section)
        u0 = coord.col / COLS_PER_SECTION
        u1 = (coord.col + 1) / COLS_PER_SECTION
        v0 = coord.row / ROWS_PER_SECTION
        v1 = (coord.row + 1) / ROWS_PER_SECTION

        return [
            _bilinear_quad(p00, p10, p01, p11, u0, v0),
            _bilinear_quad(p00, p10, p01, p11, u1, v0),
            _bilinear_quad(p00, p10, p01, p11, u1, v1),
            _bilinear_quad(p00, p10, p01, p11, u0, v1),
        ]

    def pixel_to_coord(self, px: int, py: int) -> Coord | None:
        """Find the board cell containing a pixel, or nearest cell near edges."""
        inside_best: Coord | None = None
        inside_best_dist = float("inf")
        nearest: Coord | None = None
        nearest_dist = float("inf")

        for section in range(6):
            for row in range(ROWS_PER_SECTION):
                for col in range(COLS_PER_SECTION):
                    coord = Coord(section, row, col)
                    corners = self.cell_corners(coord)
                    cx, cy = self.coord_to_pixel(coord)
                    dist = (px - cx) ** 2 + (py - cy) ** 2

                    if _point_in_convex_quad(float(px), float(py), corners):
                        if dist < inside_best_dist:
                            inside_best_dist = dist
                            inside_best = coord

                    if dist < nearest_dist:
                        nearest_dist = dist
                        nearest = coord

        if inside_best is not None:
            return inside_best

        if nearest is not None and nearest_dist <= (CELL_SIZE * 0.95) ** 2:
            return nearest

        return None

    def edge_midpoints(self) -> list[tuple[float, float]]:
        return _edge_midpoints(self._hex_vertices())

    def player_base_midpoint(self, player: int) -> tuple[float, float]:
        return self.edge_midpoints()[(2 * player) % 6]

    def _section_quad(
        self,
        section: int,
    ) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]:
        """Return bilinear quad corners (P00, P10, P01, P11) for one section."""
        vertices = self._hex_vertices()
        mids = _edge_midpoints(vertices)
        center = (self._center_x, self._center_y)

        player = section // 2
        is_right = (section % 2) == 1

        # Base edges 1/3/5 => start vertices V0/V2/V4
        va_idx = (2 * player) % 6
        vb_idx = (va_idx + 1) % 6
        base_edge_idx = (2 * player) % 6
        prev_gap_idx = (base_edge_idx - 1) % 6
        next_gap_idx = (base_edge_idx + 1) % 6

        va = vertices[va_idx]
        vb = vertices[vb_idx]
        m_base = mids[base_edge_idx]
        m_prev_gap = mids[prev_gap_idx]
        m_next_gap = mids[next_gap_idx]

        if is_right:
            return m_base, vb, center, m_next_gap
        return va, m_base, m_prev_gap, center

    def _hex_vertices(self) -> list[tuple[float, float]]:
        """Regular hex vertices ordered counter-clockwise from bottom-left."""
        angles_deg = [240.0, 300.0, 0.0, 60.0, 120.0, 180.0]
        return [
            (
                self._center_x + self._hex_radius * math.cos(math.radians(a)),
                self._center_y - self._hex_radius * math.sin(math.radians(a)),
            )
            for a in angles_deg
        ]


def _cell_uv(row: int, col: int) -> tuple[float, float]:
    """Cell-center coordinates in a 4x4 Cartesian grid."""
    return (col + 0.5) / COLS_PER_SECTION, (row + 0.5) / ROWS_PER_SECTION


def _edge_midpoints(vertices: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Edge midpoints for edges 1..6 with vertex order from _hex_vertices()."""
    mids: list[tuple[float, float]] = []
    for i in range(6):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % 6]
        mids.append(((x1 + x2) / 2.0, (y1 + y2) / 2.0))
    return mids


def _bilinear_quad(
    p00: tuple[float, float],
    p10: tuple[float, float],
    p01: tuple[float, float],
    p11: tuple[float, float],
    u: float,
    v: float,
) -> tuple[float, float]:
    """Standard bilinear interpolation over a quadrilateral."""
    a00 = (1.0 - u) * (1.0 - v)
    a10 = u * (1.0 - v)
    a01 = (1.0 - u) * v
    a11 = u * v
    x = p00[0] * a00 + p10[0] * a10 + p01[0] * a01 + p11[0] * a11
    y = p00[1] * a00 + p10[1] * a10 + p01[1] * a01 + p11[1] * a11
    return x, y


def _point_in_convex_quad(px: float, py: float, corners: list[tuple[float, float]]) -> bool:
    """Return True if a point is inside/on the boundary of a convex quadrilateral."""
    sign = 0
    for idx in range(4):
        x1, y1 = corners[idx]
        x2, y2 = corners[(idx + 1) % 4]
        cross = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
        if abs(cross) < 1e-7:
            continue
        current = 1 if cross > 0 else -1
        if sign == 0:
            sign = current
        elif current != sign:
            return False
    return True
