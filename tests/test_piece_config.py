"""Tests for PieceConfig loader and validation."""

from __future__ import annotations

import pytest
from pathlib import Path

from chess_3.piece_config import PieceConfig, PieceStats, ConfigError


@pytest.fixture
def valid_toml(tmp_path: Path) -> Path:
    p = tmp_path / "pieces.toml"
    p.write_text("""\
[pieces.pawn]
life = 1
power = 1

[pieces.knight]
life = 2
power = 3

[pieces.bishop]
life = 1
power = 3

[pieces.rook]
life = 3
power = 4

[pieces.queen]
life = 4
power = 5

[pieces.king]
life = 5
power = 3
""")
    return p


def test_loads_all_six_piece_types(valid_toml: Path) -> None:
    config = PieceConfig(valid_toml)
    assert sorted(config.all_types()) == ["bishop", "king", "knight", "pawn", "queen", "rook"]


def test_pawn_stats(valid_toml: Path) -> None:
    config = PieceConfig(valid_toml)
    pawn = config.get("pawn")
    assert pawn == PieceStats(life=1, power=1)


def test_king_stats(valid_toml: Path) -> None:
    config = PieceConfig(valid_toml)
    king = config.get("king")
    assert king == PieceStats(life=5, power=3)


def test_stats_are_frozen(valid_toml: Path) -> None:
    config = PieceConfig(valid_toml)
    with pytest.raises(AttributeError):
        config.get("pawn").life = 99  # type: ignore[misc]


def test_missing_file_raises_config_error() -> None:
    with pytest.raises(ConfigError, match="Config file not found"):
        PieceConfig(Path("/nonexistent/pieces.toml"))


def test_invalid_toml_raises_config_error(tmp_path: Path) -> None:
    p = tmp_path / "pieces.toml"
    p.write_text("this is not valid toml [[[")
    with pytest.raises(ConfigError, match="Invalid TOML"):
        PieceConfig(p)


def test_missing_pieces_section_raises_config_error(tmp_path: Path) -> None:
    p = tmp_path / "pieces.toml"
    p.write_text("[other]\nfoo = 1\n")
    with pytest.raises(ConfigError, match="missing the \\[pieces\\] section"):
        PieceConfig(p)


def test_missing_piece_type_raises_config_error(tmp_path: Path) -> None:
    p = tmp_path / "pieces.toml"
    # Only pawn — missing 5 others
    p.write_text("[pieces.pawn]\nlife = 1\npower = 1\n")
    with pytest.raises(ConfigError, match="missing piece types"):
        PieceConfig(p)


def test_unrecognized_piece_type_raises_config_error(tmp_path: Path) -> None:
    p = tmp_path / "pieces.toml"
    content = """\
[pieces.pawn]
life = 1
power = 1
[pieces.knight]
life = 2
power = 3
[pieces.bishop]
life = 1
power = 3
[pieces.rook]
life = 3
power = 4
[pieces.queen]
life = 4
power = 5
[pieces.king]
life = 5
power = 3
[pieces.dragon]
life = 10
power = 10
"""
    p.write_text(content)
    with pytest.raises(ConfigError, match="unrecognized piece types.*dragon"):
        PieceConfig(p)


def test_missing_life_key_raises_config_error(tmp_path: Path) -> None:
    p = tmp_path / "pieces.toml"
    content = """\
[pieces.pawn]
power = 1
[pieces.knight]
life = 2
power = 3
[pieces.bishop]
life = 1
power = 3
[pieces.rook]
life = 3
power = 4
[pieces.queen]
life = 4
power = 5
[pieces.king]
life = 5
power = 3
"""
    p.write_text(content)
    with pytest.raises(ConfigError, match="missing required key 'life'"):
        PieceConfig(p)


def test_wrong_type_for_life_raises_config_error(tmp_path: Path) -> None:
    p = tmp_path / "pieces.toml"
    content = """\
[pieces.pawn]
life = "lots"
power = 1
[pieces.knight]
life = 2
power = 3
[pieces.bishop]
life = 1
power = 3
[pieces.rook]
life = 3
power = 4
[pieces.queen]
life = 4
power = 5
[pieces.king]
life = 5
power = 3
"""
    p.write_text(content)
    with pytest.raises(ConfigError, match="must be an integer"):
        PieceConfig(p)


def test_zero_life_raises_config_error(tmp_path: Path) -> None:
    p = tmp_path / "pieces.toml"
    content = """\
[pieces.pawn]
life = 0
power = 1
[pieces.knight]
life = 2
power = 3
[pieces.bishop]
life = 1
power = 3
[pieces.rook]
life = 3
power = 4
[pieces.queen]
life = 4
power = 5
[pieces.king]
life = 5
power = 3
"""
    p.write_text(content)
    with pytest.raises(ConfigError, match="must be >= 1"):
        PieceConfig(p)


def test_loads_from_project_assets() -> None:
    """Smoke test: the actual pieces.toml in the project loads successfully."""
    assets_path = Path(__file__).resolve().parent.parent / "src" / "chess_3" / "assets" / "pieces.toml"
    if assets_path.exists():
        config = PieceConfig(assets_path)
        assert len(config.all_types()) == 6
