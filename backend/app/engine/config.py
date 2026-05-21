from dataclasses import dataclass

from app.game.models import Difficulty


@dataclass(frozen=True)
class DifficultyProfile:
    skill_level: int
    depth: int
    move_time_ms: int


DIFFICULTY_PROFILES: dict[Difficulty, DifficultyProfile] = {
    Difficulty.BEGINNER: DifficultyProfile(skill_level=0,  depth=2,  move_time_ms=80),
    Difficulty.EASY:     DifficultyProfile(skill_level=3,  depth=4,  move_time_ms=150),
    Difficulty.CASUAL:   DifficultyProfile(skill_level=6,  depth=6,  move_time_ms=250),
    Difficulty.MEDIUM:   DifficultyProfile(skill_level=10, depth=8,  move_time_ms=400),
    Difficulty.ADVANCED: DifficultyProfile(skill_level=14, depth=11, move_time_ms=700),
    Difficulty.HARD:     DifficultyProfile(skill_level=17, depth=14, move_time_ms=1200),
    Difficulty.EXPERT:   DifficultyProfile(skill_level=20, depth=18, move_time_ms=2500),
    Difficulty.MASTER:   DifficultyProfile(skill_level=20, depth=24, move_time_ms=5000),
}


def profile_for(difficulty: Difficulty) -> DifficultyProfile:
    return DIFFICULTY_PROFILES.get(difficulty, DIFFICULTY_PROFILES[Difficulty.MEDIUM])
