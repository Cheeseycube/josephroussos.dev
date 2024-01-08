import pandas as pd
from WordleApp.Mongodb import Wordle_db
from enum import Enum
class WordleCategory(Enum):
    HERE = 1
    NOT_HERE = 2
    NOT_ANYWHERE = 3


def wordle_feedback(proposed_word, real_word):
    feedback = [WordleCategory.NOT_ANYWHERE, WordleCategory.NOT_ANYWHERE, WordleCategory.NOT_ANYWHERE,
                WordleCategory.NOT_ANYWHERE, WordleCategory.NOT_ANYWHERE]
    available_matches_dict = {}
    for char in proposed_word:
        available_matches_dict[char] = real_word.count(char)

    # {'p': 3, 'o': 0, 'y': 0}

    # checking for exact matches first
    for i in range(5):
        if (proposed_word[i] == real_word[i]):
            feedback[i] = WordleCategory.HERE
            available_matches_dict[proposed_word[i]] -= 1

    # checking for yellows and grays
    for i in range(5):
        if (feedback[i] != WordleCategory.HERE) and (available_matches_dict[proposed_word[i]] > 0):
            feedback[i] = WordleCategory.NOT_HERE
            available_matches_dict[proposed_word[i]] -= 1
    return str(feedback)


class wordle_helper:
    def __init__(self):
        # getting data
        wordle_db = Wordle_db()
        used_words_full = wordle_db.get_used_words()
        used_words_stripped = [word_obj['word'] for word_obj in used_words_full]

        all_wordle_words = wordle_db.get_wordle_words()
        all_wordle_words_stripped = [word_obj['word'] for word_obj in all_wordle_words]

        # filtering out used words from the wordle list
        used_words = set(used_words_stripped)
        wordle_words = set(all_wordle_words_stripped)
        self.filtered_words = wordle_words - used_words

    def find_feedback_matches(self, proposed_word, given_feedback, remaining_words):
        matches = []
        if (len(remaining_words) > 0):
            self.filtered_words = remaining_words
        for filtered_word in self.filtered_words:
            if wordle_feedback(proposed_word, filtered_word) == str(given_feedback):
                matches.append(filtered_word)
        matches = sorted(matches)
        return matches





if __name__ == "__main__":
    pass


