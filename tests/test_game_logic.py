from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    is_new_high_score,
    parse_guess,
    record_high_score,
    update_score,
)


def test_get_range_for_difficulty_values():
    assert get_range_for_difficulty("Easy") == (1, 20)
    assert get_range_for_difficulty("Normal") == (1, 100)
    assert get_range_for_difficulty("Hard") == (1, 50)


def test_parse_guess_accepts_in_range_value():
    ok, guess_int, err = parse_guess("19", low=1, high=20)
    assert ok is True
    assert guess_int == 19
    assert err is None


def test_parse_guess_rejects_out_of_range_value():
    ok, guess_int, err = parse_guess("25", low=1, high=20)
    assert ok is False
    assert guess_int is None
    assert err == "Guess must be between 1 and 20."


def test_parse_guess_rejects_non_numeric():
    ok, guess_int, err = parse_guess("abc", low=1, high=100)
    assert ok is False
    assert guess_int is None
    assert err == "That is not a number."


def test_check_guess_win():
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_check_guess_too_high():
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_check_guess_too_low():
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


def test_update_score_win_awards_points():
    assert update_score(0, "Win", 1) == 90


def test_update_score_non_win_penalty():
    assert update_score(10, "Too High", 3) == 5
    assert update_score(10, "Too Low", 3) == 5


# ---------------------------------------------------------------------------
# Challenge 1: Advanced edge-case tests
# ---------------------------------------------------------------------------

# --- parse_guess edge cases ---

def test_parse_guess_boundary_low():
    """Exactly the lower boundary value is accepted."""
    ok, val, err = parse_guess("1", low=1, high=20)
    assert ok is True
    assert val == 1
    assert err is None


def test_parse_guess_boundary_high():
    """Exactly the upper boundary value is accepted."""
    ok, val, err = parse_guess("20", low=1, high=20)
    assert ok is True
    assert val == 20
    assert err is None


def test_parse_guess_one_below_low_rejected():
    """One below the lower boundary is rejected."""
    ok, val, err = parse_guess("0", low=1, high=20)
    assert ok is False
    assert val is None


def test_parse_guess_one_above_high_rejected():
    """One above the upper boundary is rejected."""
    ok, val, err = parse_guess("21", low=1, high=20)
    assert ok is False
    assert val is None


def test_parse_guess_decimal_truncates_to_valid():
    """A decimal string truncates to an int; if in range, it is accepted."""
    ok, val, err = parse_guess("3.7", low=1, high=20)
    assert ok is True
    assert val == 3


def test_parse_guess_decimal_truncates_out_of_range():
    """A decimal that truncates below the lower bound is rejected (0.9 -> 0)."""
    ok, val, err = parse_guess("0.9", low=1, high=20)
    assert ok is False
    assert val is None


def test_parse_guess_negative_number_rejected():
    """A negative number below the lower bound is rejected."""
    ok, val, err = parse_guess("-5", low=1, high=20)
    assert ok is False
    assert val is None


def test_parse_guess_very_large_number_rejected():
    """An extremely large number above the upper bound is rejected."""
    ok, val, err = parse_guess("999999", low=1, high=100)
    assert ok is False
    assert val is None


def test_parse_guess_whitespace_rejected():
    """Whitespace-only input is not a valid number."""
    ok, val, err = parse_guess("   ", low=1, high=100)
    assert ok is False
    assert val is None


def test_parse_guess_empty_string_rejected():
    """Empty string returns an error, not a crash."""
    ok, val, err = parse_guess("", low=1, high=100)
    assert ok is False


def test_parse_guess_none_rejected():
    """None input returns an error, not a crash."""
    ok, val, err = parse_guess(None, low=1, high=100)
    assert ok is False


# --- update_score edge cases ---

def test_update_score_win_minimum_ten_points():
    """Score for a win can never award fewer than 10 points (high attempt count)."""
    result = update_score(0, "Win", 10)
    assert result == 10


def test_update_score_unknown_outcome_no_change():
    """An unknown outcome string should not alter the score."""
    assert update_score(50, "Unknown", 1) == 50


# --- check_guess boundary cases ---

def test_check_guess_secret_at_minimum():
    """Guessing the minimum possible secret value wins."""
    outcome, _ = check_guess(1, 1)
    assert outcome == "Win"


def test_check_guess_secret_at_maximum():
    """Guessing the maximum possible secret value wins."""
    outcome, _ = check_guess(100, 100)
    assert outcome == "Win"


# --- high score tracker ---

def test_is_new_high_score_no_existing_record():
    """Any win is a new record when no previous record exists."""
    scores = {"Easy": None, "Normal": None, "Hard": None}
    assert is_new_high_score(scores, "Easy", 3, 70) is True


def test_is_new_high_score_fewer_attempts_beats_record():
    """Winning in fewer guesses beats the existing record."""
    scores = record_high_score({}, "Normal", 5, 50)
    assert is_new_high_score(scores, "Normal", 3, 30) is True


def test_is_new_high_score_same_attempts_higher_score_beats_record():
    """Same guess count but higher score beats the existing record."""
    scores = record_high_score({}, "Normal", 3, 50)
    assert is_new_high_score(scores, "Normal", 3, 70) is True


def test_is_new_high_score_worse_result_not_new():
    """More guesses with a lower score does not beat the existing record."""
    scores = record_high_score({}, "Hard", 2, 80)
    assert is_new_high_score(scores, "Hard", 5, 50) is False


def test_record_high_score_stores_entry():
    """record_high_score writes the correct values for a difficulty."""
    scores = record_high_score({}, "Easy", 2, 90)
    assert scores["Easy"] == {"attempts": 2, "score": 90}


def test_record_high_score_overwrites_existing():
    """record_high_score replaces a previous entry for the same difficulty."""
    scores = record_high_score({}, "Easy", 4, 60)
    scores = record_high_score(scores, "Easy", 2, 80)
    assert scores["Easy"] == {"attempts": 2, "score": 80}
