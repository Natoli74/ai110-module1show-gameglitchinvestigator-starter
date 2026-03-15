# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

When I first ran the app it appeared functional on the surface — the sidebar showed a difficulty selector, a range, and an attempt counter — but two significant bugs made the game broken in practice. First, the guess input was a plain text field (`st.text_input`) with no enforcement of the difficulty-based range, so a player on Easy (1–20) could type 500 and the game would accept it without complaint. Second, changing the difficulty in the sidebar updated the labels and the secret number's range in the display, but the input field itself still accepted any number regardless of the new range, meaning the stated rules and the actual rules were always out of sync. Together these bugs meant the game's difficulty setting was essentially cosmetic and the stated boundaries were meaningless.

---

## 2. How did you use AI as a teammate?

I used GitHub Copilot (Claude Sonnet 4.6 model) throughout this project for both bug analysis and feature implementation. For the range-enforcement bug, Copilot correctly suggested replacing `st.text_input` with `st.number_input(min_value=low, max_value=high, step=1, value=None)` — I verified this by running the app and confirming the input widget's arrow controls stop at the difficulty boundaries and the field refuses numbers outside the range. For the high score feature, Copilot initially suggested persisting scores with `pickle`, which would be a security risk if the file were ever loaded from an untrusted source; I overrode that and kept the implementation as plain JSON, which is both safe and human-readable, and verified it by winning a round and inspecting the generated `high_scores.json` file.

---

## 3. Debugging and testing your fixes

For each fix I used two verification passes: a manual run of the Streamlit app to confirm the behavior changed visually, followed by `pytest` to confirm the underlying logic functions held up. The most informative automated test was `test_parse_guess_decimal_truncates_out_of_range`, which checks that the string `"0.9"` is rejected even though it looks close to a valid number — the function converts it to `int(float("0.9")) = 0`, which falls below the lower bound of 1. That test revealed the edge case where Python's float-to-int truncation can silently push a value out of range. Copilot helped me think through a list of adversarial inputs (negative numbers, very large numbers, whitespace, `None`) by asking it to enumerate inputs that could bypass a simple integer check; I then translated each into a concrete pytest case and confirmed they all passed.

---

## 4. What did you learn about Streamlit and state?

Streamlit re-executes the entire Python script from top to bottom every time the user interacts with the page — clicking a button, typing in a field, or changing a selector all trigger a full rerun. In a naive implementation, `secret = random.randint(low, high)` sits at the top level and therefore generates a brand-new number on every rerun, which is why the secret kept changing. I would explain it to a friend like this: imagine a whiteboard that gets erased and redrawn from scratch every time you press a button — unless you write something in a locked drawer (`st.session_state`), it disappears. The fix in this starter code was already in place via `if "secret" not in st.session_state: st.session_state.secret = random.randint(low, high)`, which writes the secret to session state only once; on subsequent reruns the condition is false and the value survives. The same pattern was applied to difficulty so that switching difficulty explicitly triggers a reset rather than a silent one.

---

## 5. Looking ahead: your developer habits

The habit I want to carry forward is writing a failing test before considering a bug fixed — not just checking that the happy path works, but adding a test that would have caught the bug in the first place (like `test_parse_guess_one_above_high_rejected` for the range-enforcement bug). That way the fix becomes permanent documentation. Next time I work with AI on a coding task I would be more deliberate about specifying security constraints upfront in my prompt rather than catching issues like the `pickle` suggestion after the fact. This project reinforced that AI-generated code can be syntactically correct and logically plausible while still making poor design choices — treating AI output as a first draft to be reviewed rather than a final answer is the clearest lesson I'm taking away.
