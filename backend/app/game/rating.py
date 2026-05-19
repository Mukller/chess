DIFFICULTY_ENGINE_RATINGS: dict[str, int] = {
    "easy": 800,
    "medium": 1500,
    "hard": 2200,
}

DEFAULT_PLAYER_RATING = 1200


def calc_score(result: str, user_color_is_white: bool) -> float:
    if result == "1/2-1/2":
        return 0.5
    if result == "1-0":
        return 1.0 if user_color_is_white else 0.0
    if result == "0-1":
        return 0.0 if user_color_is_white else 1.0
    return 0.5


def calc_elo_change(player_rating: int, engine_rating: int, score: float) -> int:
    expected = 1.0 / (1.0 + 10.0 ** ((engine_rating - player_rating) / 400.0))
    k = 32 if player_rating < 1600 else (16 if player_rating < 2400 else 10)
    return round(k * (score - expected))


def apply_result(
    player_rating: int,
    difficulty: str,
    result: str,
    user_color_is_white: bool,
) -> tuple[int, int]:
    engine_rating = DIFFICULTY_ENGINE_RATINGS.get(difficulty, DEFAULT_PLAYER_RATING)
    score = calc_score(result, user_color_is_white)
    delta = calc_elo_change(player_rating, engine_rating, score)
    new_rating = max(100, player_rating + delta)
    return new_rating, delta
