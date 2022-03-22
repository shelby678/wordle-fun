"""
Author: Shelby Ferrier
This is an algorithmic Wordle solver! The strategy is to look for the guess that minimizes the number of possible words
remaining after guessing it (averaged over every possible answer). 

It's likely this could be improved by minimizing the average length of game instead. 

It should be noted that we are using the wordle answer bank for the possible guesses, for simplicity. In reality 
there are about 10,000 more possible guesses.
"""
import numpy as np
import random
import string
import csv

wordList = np.loadtxt("wordle-answers.txt", dtype=str)

class Game:
    def __init__(self, answer, guessed, posGuesses = wordList, statusUpdates = True):
        self.answer = answer
        self.statusUpdates = statusUpdates
        self.guessed = guessed
        self.posGuesses = posGuesses
        self.yellows = set()
        self.posLetters = []
        self.bestGuess = ""
        for i in range(5):
            self.posLetters.append(list(string.ascii_lowercase))
        
    """ 
    A method that returns the best guess
    """
    def updateBestGuess(self):
        avgs = []
        if len(self.guessed) > 0:
            self.update()
        bestAvg = np.inf
        i = 0
        for g in self.posGuesses:
            i += 1 
            currentAvg = 0
            currentAvg = self.testGuess(g)
            avgs.append([g, currentAvg])
            if self.statusUpdates and i % 10 == 0: print("progress: ", i , "/ ", len(self.posGuesses))
            if currentAvg < bestAvg:
                bestAvg = currentAvg
                self.bestGuess = g
        if self.statusUpdates: print("Best guess: ", self.bestGuess, "- avg:", bestAvg)
        return (self.bestGuess, avgs)

    """
    updates posLetters and posGuesses
    """
    def update(self):
        # update posLetters based off of changes in guessed
        for guess in self.guessed:
            for i in range(5):
                if guess[i] is self.answer[i]: # green
                    self.posLetters[i] = list(guess[i])
                elif(guess[i] in self.answer): # yellow
                    self.yellows.add(guess[i])
                else:                          # gray
                    for j in range(5): 
                        if guess[i] in self.posLetters[j]:
                            self.posLetters[j].remove(guess[i])
        
        # update posGuesses off of changes in posLetters
        newWordBank = set()
        if len(self.posGuesses) == 0:
            return
        for posGuess in self.posGuesses:
            sheValid = True
            for i in range(5):
                if posGuess[i] not in self.posLetters[i]:
                    sheValid = False
            for yellow in self.yellows:
                if yellow not in posGuess:
                    sheValid = False
            if sheValid:
                newWordBank.add(posGuess)
        self.posGuesses = list(newWordBank)
    
    
    """
    returns an average number of possible guesses remaining after guessing this word
    """
    def testGuess(self, guess):
        avgGuesses = 0
        newGuesses = self.guessed.copy()
        newGuesses.append(guess)
        for pretendAnswer in self.posGuesses:
            pretendGame = Game(pretendAnswer, newGuesses, posGuesses = self.posGuesses)
            pretendGame.update()
            avgGuesses += len(pretendGame.posGuesses) / len(self.posGuesses)
        return avgGuesses
    
    def guessNewWord(self, guess):
        self.guessed.append(guess)
    
    def playBall(self):
        while self.bestGuess != self.answer:
            self.updateBestGuess()
            self.guessNewWord(self.bestGuess)
        if self.statusUpdates:
            print(len(self.guessed), " tries to guess ", self.answer)
        return len(self.guessed)

def selfEval():
    avgGameLength = 0
    wordListSample = random.sample(list(wordList), 100)
    i = 0
    for word in wordListSample:
        i += 1
        game = Game(word, ["raise"])
        avgGameLength += game.playBall()
        print("AVG: ", avgGameLength/ i)
    print("FINAL AVG: ", avgGameLength / 100)

selfEval()
