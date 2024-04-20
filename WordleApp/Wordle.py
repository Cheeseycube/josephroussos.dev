import pandas as pd
from WordleApp.Mongodb import Wordle_db
from enum import Enum
class WordleCategory(Enum):
    HERE = 1
    NOT_HERE = 2
    NOT_ANYWHERE = 3


def wordle_feedback(proposed_word, real_word):
    proposed_word = proposed_word.upper()
    real_word = real_word.upper()
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
    return feedback


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

        # getting all 5 letter words
        self.all_words = [ word_dict['word'] for word_dict in wordle_db.get_all_words()]


    def find_feedback_matches(self, proposed_word, given_feedback, remaining_words):
        matches = []
        if (len(remaining_words) > 0):
            self.filtered_words = remaining_words
        for filtered_word in self.filtered_words:
            if str(wordle_feedback(proposed_word, filtered_word)) == str(given_feedback):
                matches.append(filtered_word)
        matches = sorted(matches)
        if len(matches) > 0:
            self.filtered_words = matches
        return matches

    def evaluate_potential_guesses(self):
        # for each word in all 5 letter words:
        #   compute wordle output assuming each remaining wordle word is the correct answer
        #   store information somewhere
        guess_feedback = {}
        # for each word in all 5 letter words:
        for proposed_word in self.all_words:
            print(f"proposed word: {proposed_word}")
            guess_feedback[proposed_word] = []
            # compute resulting wordle output if this word is guessed--for each remaining wordle word
            # then compute remaining words
            # finally store the remaining words
            for wordle_word in self.filtered_words:
                print(f"remaining word: {wordle_word}")
                wordle_output = wordle_feedback(proposed_word=proposed_word, real_word=wordle_word)
                guess_feedback[proposed_word].append(str(wordle_output))
        # for each word in all 5 letter words:
        #   group wordle words with identical outputs
        #   ex: print(number of group 1:) print(number of group 2:)
        #   see line 1037 in dad's Fortran program
        group_distribution = {}
        for proposed_word in guess_feedback:
            group_distribution[proposed_word] = {}
            # for each set of remaining words for a given 5 letter word
            for feedback_list in guess_feedback[proposed_word]:
                groups = []
                counted_feedback = []
                for feedback in feedback_list:
                    # find matches for each feedback
                    if feedback not in counted_feedback:
                        groups.append(feedback_list.count(feedback))
                        counted_feedback.append(feedback)
                curr_group_distribution = [0 for _ in range(len(groups)+1)]
                for group_num in groups:
                    curr_group_distribution[group_num] += 1
                group_distribution[proposed_word] = curr_group_distribution
        return group_distribution

    def simple_evaluate_potential_guesses(self):
        group_distributions = {}
        for proposed_word in self.all_words:
            print(f"evaluating {proposed_word}")
            group_distributions[proposed_word] = self.evaluate_single_guess(proposed_word)
        return group_distributions

    def evaluate_single_guess(self, given_word):
        guess_feedback = []
        for wordle_word in self.filtered_words:
            #print(f"testing {wordle_word}")
            wordle_output = wordle_feedback(proposed_word=given_word, real_word=wordle_word)
            guess_feedback.append(str(wordle_output))
        groups = []
        counted = []
        for feedback in guess_feedback:
            if feedback not in counted:
                groups.append(guess_feedback.count(feedback))
                counted.append(feedback)
        group_distribution = [0 for _ in range(len(guess_feedback)+1)]
        for group_num in groups:
            group_distribution[group_num] += 1
        return group_distribution





if __name__ == "__main__":
    wordle_obj = wordle_helper()
    matches = wordle_obj.find_feedback_matches('CRAFT',
                                           [WordleCategory.NOT_ANYWHERE, WordleCategory.NOT_ANYWHERE, WordleCategory.HERE,
                                            WordleCategory.NOT_ANYWHERE, WordleCategory.NOT_ANYWHERE],
                                           [])
    '''new_matches = wordle_obj.find_feedback_matches('PLAID',
                                     [WordleCategory.NOT_ANYWHERE, WordleCategory.NOT_ANYWHERE, WordleCategory.HERE,
                                      WordleCategory.NOT_ANYWHERE, WordleCategory.NOT_HERE],
                                     matches)'''
    print(sorted(wordle_obj.filtered_words))
    print(len(wordle_obj.filtered_words))




    res = wordle_obj.simple_evaluate_potential_guesses()
    for word in res:
        if word[0] == 's':
            print(word.upper())
            curr_distribution = res[word]
            for i in range(1,5):
                print(f"Group {i} Count: {curr_distribution[i]}")
            print()
            print()

    '''res = wordle_obj.evaluate_single_guess('SPEND')
    print('SPEND')
    for i in range(len(res)):
        if res[i] > 0:
            print(f"Group {i} Count: {res[i]}")'''



