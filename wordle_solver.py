"""
Author: Shelby Ferrier
This is an algorithmic Wordle solver! The strategy is to look for the guess that minimizes the number of possible words
remaining after guessing it (averaged over every possible answer). 

It's likely this could be improved by minimizing the average length of game instead. 

It should be noted that we are using the wordle answer bank for the possible guesses, for simplicity. In reality 
there are about 10,000 more possible guesses.
"""
from logging import exception
import numpy as np
import random
import string

word_list = np.loadtxt("wordle-answers.txt", dtype=str)

class Game:
    def __init__(self, answer, guessed, pos_guesses = word_list, status_updates = True):
        self.answer = answer
        self.status_updates = status_updates # prints the progress of the game through the time intensive method update_best_guess()
        self.guessed = guessed
        self.k_guessed  = 0
        self.pos_guesses = pos_guesses
        self.yellows = set()
        self.pos_letters = [list(string.ascii_lowercase)]* 5
        self.best_guess = ""
    """ 
    returns the guess that minimizes the average number of guesses remaining, 
    as well as a list of all possible guess with their averages
    """
    def update_best_guess(self):
        avgs = []
        best_avg = np.inf
        i = 0
        # iterate over possible guesses
        for g in self.pos_guesses:
            i += 1 
            # get average number of guesses to finish the game
            current_avg = self.test_guess(g)
            avgs.append([g, current_avg])
            if self.status_updates and i % 10 == 0: print("progress: ", i , "/ ", len(self.pos_guesses))
            # check if this is the best guess so far
            if current_avg < best_avg:
                best_avg = current_avg
                self.best_guess = g
        if self.status_updates: print("Next guess: ", self.best_guess, "- avg:", best_avg)
        return (self.best_guess, avgs)

    """
    updates pos_letters and pos_guesses based on the words in guessed
    """
    def update(self):
        # update pos_letters
        for guess in self.guessed[self.k_guessed: len(self.guessed)]:
            for i in range(5):
                if guess[i] is self.answer[i]: # green
                    self.pos_letters[i] = list(guess[i])
                elif(guess[i] in self.answer):   
                    self.yellows.add(guess[i]) # update yellow word bank
                    # remove yellow
                    if guess[i] in self.pos_letters[i]:
                        self.pos_letters[i] = [letter for letter in self.pos_letters[i] if letter != guess[i]]
                else:
                    # remove grays
                    for j in range(5):         
                        if guess[i] in self.pos_letters[j]:
                            self.pos_letters[j].remove(guess[i])
        # update pos_guesses
        newWordBank = set()
        for pos_guess in self.pos_guesses:
            # add g to pos_guesses if it meets the conditions in pos_letters and yellows
            valid_guess = True
            for i in range(5):
                if pos_guess[i] not in self.pos_letters[i]:
                    valid_guess = False
            for yellow in self.yellows:
                if yellow not in pos_guess:
                    valid_guess = False
            if valid_guess:
                newWordBank.add(pos_guess)
        self.pos_guesses = list(newWordBank)
        self.k_guessed = len(self.guessed)
        if len(self.pos_guesses == 0):
            raise Exception("There are no valid guesses remaining")
    
    """
    tests the eficacy of a new guess in this game
    returns the average number of possible guess remaining
    """
    def test_guess(self, guess):
        avgGuesses = 0
        newGuesses = self.guessed.copy()
        newGuesses.append(guess) # a list of all guesses made, including the one we're testing
        for possible_answer in self.pos_guesses: # iterate over possible winning words
            # creates a mini game with guess included as the next guess
            pretend_game = Game(possible_answer, newGuesses)
            pretend_game.update()
            avgGuesses += len(pretend_game.pos_guesses) / len(self.pos_guesses)
        return avgGuesses

    def guess_new_word(self, guess):
        self.guessed.append(guess)
        self.update()
    
    """
    gets number of guesses taken by the program to get the answer
    """
    def play_ball(self):
        self.update()
        # until the answer is guessed, keep guessing things
        while self.best_guess != self.answer:
            self.update_best_guess()
            self.guess_new_word(self.best_guess)
        if self.status_updates:
            print(len(self.guessed), " tries to guess ", self.answer)
        return len(self.guessed)

""""
evaluates the average game length based on a list of initial guesses
""""
def self_eval(init_guesses):
    avg_game_length = 0
    word_listSample = random.sample(list(word_list), 100)
    i = 0
    for word in word_listSample:
        i += 1
        game = Game(word, init_guesses)
        avg_game_length += game.play_ball()
        print("AVG: ", avg_game_length/ i)
    print("FINAL AVG: ", avg_game_length / 100)

# uncomment this to run the program on the best starting word "raise"
#self_eval(["raise"])

# play ball example
#game = Game("abase", ["house"])
#game.play_ball()