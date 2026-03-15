from logic_utils import check_guess, get_range_for_difficulty, parse_guess, update_score


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
