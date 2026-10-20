"""Episode v2 recap lullaby: one moral per story, in episode order (el_song2.py reads it like a fable)."""
STYLE_EXTRA = ["soft bedtime lullaby", "music box", "gentle and sleepy", "quiet"]
ORDER = [1, 2, 3, 4, 5, 6, 10, 9, 7, 8]
MORAL = {1: "Tiny friends can be big helpers!", 2: "Don't say sour, ask a friend!", 3: "Think it through, try something new!",
         4: "Slow and steady gets there too!", 5: "Love what you've got, and share it!", 6: "Help a little every day!",
         7: "Gentle and kind works best!", 8: "Tell the truth, so friends know!", 9: "Together we're strong!",
         10: "Help a friend, and a friend helps you!"}
WHO = ["tumble", "pip"]
PLAN_SECTIONS = [("Intro", 0, 1.5, "verse")]
PLAN_LINES = []
for k, n in enumerate(ORDER):
    PLAN_SECTIONS.append((f"Moral {n}", 1.5 + 2 * k, 3.5 + 2 * k, "verse"))
    PLAN_LINES.append((f"Moral {n}", WHO[k % 2], MORAL[n]))
PLAN_SECTIONS += [("Chorus", 21.5, 24.5, "chorus"), ("Button", 24.5, 26.5, "verse")]
PLAN_LINES += [("Chorus", "both", "Big or small, short or tall,"), ("Chorus", "both", "friends help friends, that's best of all.")]
