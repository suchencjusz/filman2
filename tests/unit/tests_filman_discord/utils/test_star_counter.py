import pytest

from filman_discord.utils.star_counter import star_emoji_counter


def test_star_emoji_counter_ones():
    assert star_emoji_counter(0.0) == "🌑🌑🌑🌑🌑🌑🌑🌑🌑🌑"

    assert star_emoji_counter(0.1) == "🌘🌑🌑🌑🌑🌑🌑🌑🌑🌑"
    assert star_emoji_counter(0.2) == "🌘🌑🌑🌑🌑🌑🌑🌑🌑🌑"

    assert star_emoji_counter(0.3) == "🌗🌑🌑🌑🌑🌑🌑🌑🌑🌑"
    assert star_emoji_counter(0.4) == "🌗🌑🌑🌑🌑🌑🌑🌑🌑🌑"
    assert star_emoji_counter(0.5) == "🌗🌑🌑🌑🌑🌑🌑🌑🌑🌑"
    assert star_emoji_counter(0.6) == "🌗🌑🌑🌑🌑🌑🌑🌑🌑🌑"
    assert star_emoji_counter(0.7) == "🌗🌑🌑🌑🌑🌑🌑🌑🌑🌑"

    assert star_emoji_counter(0.8) == "🌖🌑🌑🌑🌑🌑🌑🌑🌑🌑"
    assert star_emoji_counter(0.9) == "🌖🌑🌑🌑🌑🌑🌑🌑🌑🌑"

    assert star_emoji_counter(1.0) == "🌕🌑🌑🌑🌑🌑🌑🌑🌑🌑"


def test_star_emoji_counter_tens():
    assert star_emoji_counter(9.0) ==  "🌕🌕🌕🌕🌕🌕🌕🌕🌕🌑"
 
    assert star_emoji_counter(9.1) ==  "🌕🌕🌕🌕🌕🌕🌕🌕🌕🌘"
    assert star_emoji_counter(9.2) ==  "🌕🌕🌕🌕🌕🌕🌕🌕🌕🌘"
 
    assert star_emoji_counter(9.3) ==  "🌕🌕🌕🌕🌕🌕🌕🌕🌕🌗"
    assert star_emoji_counter(9.4) ==  "🌕🌕🌕🌕🌕🌕🌕🌕🌕🌗"
    assert star_emoji_counter(9.5) ==  "🌕🌕🌕🌕🌕🌕🌕🌕🌕🌗"
    assert star_emoji_counter(9.6) ==  "🌕🌕🌕🌕🌕🌕🌕🌕🌕🌗"
    assert star_emoji_counter(9.7) ==  "🌕🌕🌕🌕🌕🌕🌕🌕🌕🌗"
 
    assert star_emoji_counter(9.8) ==  "🌕🌕🌕🌕🌕🌕🌕🌕🌕🌖"
    assert star_emoji_counter(9.9) ==  "🌕🌕🌕🌕🌕🌕🌕🌕🌕🌖"

    assert star_emoji_counter(10.0) == "🌕🌕🌕🌕🌕🌕🌕🌕🌕🌕"

def test_star_emoji_from_0_to_10():
    assert star_emoji_counter(0.0) ==  "🌑🌑🌑🌑🌑🌑🌑🌑🌑🌑"
    assert star_emoji_counter(1.0) ==  "🌕🌑🌑🌑🌑🌑🌑🌑🌑🌑"
    assert star_emoji_counter(2.0) ==  "🌕🌕🌑🌑🌑🌑🌑🌑🌑🌑"
    assert star_emoji_counter(3.0) ==  "🌕🌕🌕🌑🌑🌑🌑🌑🌑🌑"
    assert star_emoji_counter(4.0) ==  "🌕🌕🌕🌕🌑🌑🌑🌑🌑🌑"
    assert star_emoji_counter(5.0) ==  "🌕🌕🌕🌕🌕🌑🌑🌑🌑🌑"
    assert star_emoji_counter(6.0) ==  "🌕🌕🌕🌕🌕🌕🌑🌑🌑🌑"
    assert star_emoji_counter(7.0) ==  "🌕🌕🌕🌕🌕🌕🌕🌑🌑🌑"
    assert star_emoji_counter(8.0) ==  "🌕🌕🌕🌕🌕🌕🌕🌕🌑🌑"
    assert star_emoji_counter(9.0) ==  "🌕🌕🌕🌕🌕🌕🌕🌕🌕🌑"
    assert star_emoji_counter(10.0) == "🌕🌕🌕🌕🌕🌕🌕🌕🌕🌕"

def test_star_emoji_rounding():
    assert star_emoji_counter(1.00001) == "🌕🌑🌑🌑🌑🌑🌑🌑🌑🌑"
    assert star_emoji_counter(1.99999) == "🌕🌕🌑🌑🌑🌑🌑🌑🌑🌑"

    assert star_emoji_counter(2.00001) == "🌕🌕🌑🌑🌑🌑🌑🌑🌑🌑"
    assert star_emoji_counter(2.99999) == "🌕🌕🌕🌑🌑🌑🌑🌑🌑🌑"

    assert star_emoji_counter(7.95410) == "🌕🌕🌕🌕🌕🌕🌕🌕🌑🌑"
    assert star_emoji_counter(8.04075) == "🌕🌕🌕🌕🌕🌕🌕🌕🌑🌑"

    assert star_emoji_counter(9.99999) == "🌕🌕🌕🌕🌕🌕🌕🌕🌕🌕"

def test_star_emoji_counter_invalid():
    with pytest.raises(ValueError):
        star_emoji_counter(-1.0)

    with pytest.raises(ValueError):
        star_emoji_counter(10.1)

import logging

LOGGER = logging.getLogger(__name__)


def printx():
    for i in range(0, 10, 0.1):
        LOGGER.critical(f"i: {i}")