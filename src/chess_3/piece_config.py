"""Config-driven piece stat loader with strict validation."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

REQUIRED_PIECE_TYPES = frozenset({"pawn", "knight", "bishop", "rook", "queen", "king"})


@dataclass(frozen=True)
class PieceStats:
    """Immutable stats for a single piece type."""
    life: int
    power: int


class ConfigError(Exception):
    """Raised when pieces.toml is missing, malformed, or has invalid values."""


class PieceConfig:
    """Loads and validates piece stats from a TOML config file.

    Usage:
        config = PieceConfig(Path("pieces.toml"))
        pawn_stats = config.get("pawn")  # PieceStats(life=1, power=1)
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._stats: dict[str, PieceStats] = self._load_and_validate(path)

    def get(self, piece_type: str) -> PieceStats:
        """Return stats for a piece type. Raises KeyError if type unknown."""
        return self._stats[piece_type]

    def all_types(self) -> list[str]:
        """Return all loaded piece type names."""
        return list(self._stats.keys())

    @staticmethod
    def _load_and_validate(path: Path) -> dict[str, PieceStats]:
        if not path.exists():
            raise ConfigError(
                f"Config file not found: {path}. "
                f"Expected a pieces.toml file with sections for: {', '.join(sorted(REQUIRED_PIECE_TYPES))}"
            )

        try:
            with path.open("rb") as f:
                raw = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ConfigError(f"Invalid TOML in {path}: {e}") from e

        if "pieces" not in raw:
            raise ConfigError(
                f"Config file {path} is missing the [pieces] section. "
                f"Expected sections like [pieces.pawn], [pieces.knight], etc."
            )

        pieces_raw = raw["pieces"]
        if not isinstance(pieces_raw, dict):
            raise ConfigError(f"Config file {path}: [pieces] must be a table, got {type(pieces_raw).__name__}")

        # Check for missing piece types
        found_types = set(pieces_raw.keys())
        missing = REQUIRED_PIECE_TYPES - found_types
        if missing:
            raise ConfigError(
                f"Config file {path} is missing piece types: {', '.join(sorted(missing))}. "
                f"Required: {', '.join(sorted(REQUIRED_PIECE_TYPES))}"
            )

        # Check for unrecognized piece types
        extra = found_types - REQUIRED_PIECE_TYPES
        if extra:
            raise ConfigError(
                f"Config file {path} has unrecognized piece types: {', '.join(sorted(extra))}. "
                f"Valid types: {', '.join(sorted(REQUIRED_PIECE_TYPES))}"
            )

        stats: dict[str, PieceStats] = {}
        for name, data in pieces_raw.items():
            if not isinstance(data, dict):
                raise ConfigError(f"Config file {path}: [pieces.{name}] must be a table, got {type(data).__name__}")

            for key in ("life", "power"):
                if key not in data:
                    raise ConfigError(f"Config file {path}: [pieces.{name}] is missing required key '{key}'")
                val = data[key]
                if not isinstance(val, int):
                    raise ConfigError(
                        f"Config file {path}: [pieces.{name}].{key} must be an integer, got {type(val).__name__} ({val!r})"
                    )
                if val < 1:
                    raise ConfigError(
                        f"Config file {path}: [pieces.{name}].{key} must be >= 1, got {val}"
                    )

            stats[name] = PieceStats(life=data["life"], power=data["power"])

        return stats
