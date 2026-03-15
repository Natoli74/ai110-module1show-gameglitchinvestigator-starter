import json
import os

HIGH_SCORES_FILE = "high_scores.json"


def load_high_scores() -> dict:
    """Load per-difficulty high scores from disk. Returns defaults when missing."""
    if os.path.exists(HIGH_SCORES_FILE):
        try:
            with open(HIGH_SCORES_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"Easy": None, "Normal": None, "Hard": None}


def save_high_scores(scores: dict) -> None:
    """Write high scores dict to disk."""
    with open(HIGH_SCORES_FILE, "w") as f:
        json.dump(scores, f)


def is_new_high_score(scores: dict, difficulty: str, attempts: int, score: int) -> bool:
    """Return True if this win beats the stored high score for the difficulty.

    Fewer guesses wins; ties broken by higher score.
    """
    current = scores.get(difficulty)
    if current is None:
        return True
    if attempts < current["attempts"]:
        return True
    if attempts == current["attempts"] and score > current["score"]:
        return True
    return False


def record_high_score(scores: dict, difficulty: str, attempts: int, score: int) -> dict:
    """Update scores dict with a new record and return it (caller must save)."""
    scores[difficulty] = {"attempts": attempts, "score": score}
    return scores


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 100
    if difficulty == "Hard":
        return 1, 50
    return 1, 100


def parse_guess(raw: str, low: int = None, high: int = None):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)

    If low/high are provided, validates the guess is within that inclusive range.
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    if low is not None and high is not None and not (low <= value <= high):
        return False, None, f"Guess must be between {low} and {high}."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    if guess == secret:
        return "Win", "Correct!"

    if guess > secret:
        return "Too High", "Go LOWER!"

    return "Too Low", "Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * attempt_number
        if points < 10:
            points = 10
        return current_score + points

    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
