def star_emoji_counter(stars: float) -> str:
    """
    Convert float rating to emoji string using moon phases.

    :param stars: float rating between 0.0 and 10.0
    :return: str with 10 moon emoji representing the rating
    """

    if stars < 0.0 or stars > 10.0:
        raise ValueError("Rating must be between 0.0 and 10.0")

    stars = round(stars, 1)
    stars_full = int(stars)
    decimal_part = round(stars - stars_full, 1)

    full = "🌕"
    near_full = "🌖"
    half = "🌗"
    near_zero = "🌘"
    zero = "🌑"

    result = ""

    result += full * stars_full

    if decimal_part > 0:
        if decimal_part >= 0.75:
            result += near_full
        elif decimal_part >= 0.3:
            result += half
        elif decimal_part > 0:
            result += near_zero

    remaining = 10 - len(result)
    result += zero * remaining

    return result
