"""Tests for CoordSystem pixel conversion — round-trip correctness on all six sections."""

from __future__ import annotations

import pytest

from chess_3.coords import Coord
from chess_3.coord_system import CoordSystem


@pytest.fixture
def cs() -> CoordSystem:
    return CoordSystem()


class TestCoordRoundTrip:
    """coord_to_pixel -> pixel_to_coord must return the original coord."""

    @pytest.mark.parametrize("section", range(6))
    def test_center_cell_round_trips(self, cs: CoordSystem, section: int) -> None:
        coord = Coord(section, 1, 1)
        px, py = cs.coord_to_pixel(coord)
        result = cs.pixel_to_coord(px, py)
        assert result == coord

    @pytest.mark.parametrize("section", range(6))
    def test_corner_cells_round_trip(self, cs: CoordSystem, section: int) -> None:
        corners = [
            Coord(section, 0, 0),
            Coord(section, 0, 3),
            Coord(section, 3, 0),
            Coord(section, 3, 3),
        ]
        for coord in corners:
            px, py = cs.coord_to_pixel(coord)
            result = cs.pixel_to_coord(px, py)
            assert result == coord, f"Round-trip failed for {coord}: pixel ({px}, {py}) -> {result}"

    @pytest.mark.parametrize("section", range(6))
    def test_all_cells_round_trip(self, cs: CoordSystem, section: int) -> None:
        for row in range(4):
            for col in range(4):
                coord = Coord(section, row, col)
                px, py = cs.coord_to_pixel(coord)
                result = cs.pixel_to_coord(px, py)
                assert result == coord, f"Round-trip failed for {coord}"


class TestPixelToCoordEdgeCases:
    def test_far_away_returns_none(self, cs: CoordSystem) -> None:
        result = cs.pixel_to_coord(-9999, -9999)
        assert result is None

    def test_origin_returns_something_or_none(self, cs: CoordSystem) -> None:
        result = cs.pixel_to_coord(0, 0)
        assert result is None or isinstance(result, Coord)


class TestCoordToPixelDistinct:
    def test_adjacent_cells_produce_different_pixels(self, cs: CoordSystem) -> None:
        a = cs.coord_to_pixel(Coord(0, 1, 1))
        b = cs.coord_to_pixel(Coord(0, 1, 2))
        assert a != b

    def test_all_sections_produce_different_origins(self, cs: CoordSystem) -> None:
        """Same row/col in different sections must map to different screen positions."""
        pixels = [cs.coord_to_pixel(Coord(s, 1, 1)) for s in range(6)]
        assert len(set(pixels)) == 6


class TestCoordValidation:
    def test_invalid_section_raises(self) -> None:
        with pytest.raises(ValueError, match="section"):
            Coord(6, 0, 0)

    def test_negative_row_raises(self) -> None:
        with pytest.raises(ValueError, match="row"):
            Coord(0, -1, 0)

    def test_col_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError, match="col"):
            Coord(0, 0, 4)

    def test_coord_is_hashable(self) -> None:
        """Coord must be usable as a dict key."""
        d: dict[Coord, str] = {Coord(0, 0, 0): "test"}
        assert d[Coord(0, 0, 0)] == "test"

    def test_coord_str_round_trip(self) -> None:
        c = Coord(3, 2, 1)
        assert Coord.from_str(str(c)) == c
