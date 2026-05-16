from dataclasses import dataclass

from app.game.models import Difficulty


@dataclass(frozen=True)
class DifficultyProfile:
    skill_level: int
    depth: int
    move_time_ms: int


DIFFICULTY_PROFILES: dict[Difficulty, DifficultyProfile] = {
    Difficulty.EASY: DifficultyProfile(skill_level=2, depth=4, move_time_ms=100),
    Difficulty.MEDIUM: DifficultyProfile(skill_level=8, depth=8, move_time_ms=300),
    Difficulty.HARD: DifficultyProfile(skill_level=18, depth=14, move_time_ms=1200),
}


def profile_for(difficulty: Difficulty) -> DifficultyProfile:
    return DIFFICULTY_PROFILES.get(difficulty, DIFFICULTY_PROFILES[Difficulty.MEDIUM])
