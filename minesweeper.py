# -*- coding: utf-8 -*-
"""
Created on Mon Nov 14 14:33:14 2016

@author: arewh
"""
from random import shuffle,choice
from copy import deepcopy
import operator
from itertools import product
import MSFoL
from time import sleep

#--------------------------------------------------------------------------Game

class Minesweeper(object):
    def __init__(self,player,width=10,height=10,mineCount=10,safeStart=True):
        print('input, in one line:')
        print('action, followed by a space, and then the tuple (row,column) if applicable.')
        print('eg \"dig (0,0)\", or \"flag (1,2)\", or \"forfeit\".')
        self.width = width
        self.height = height
        self.wrong = 0
        self.player = player
        player.game = self
        self.lastmove = None
        self.mineCount = mineCount
        if mineCount <= width*height:
            self.width = width
            self.height = height
            X = list(range(0,height))
            Y = list(range(0,width))
            self.plots = list(product(X,Y))
            self.mines = list()
            self.unmined = deepcopy(self.plots)
            shuffle(self.unmined)
            i = 0
            while i < mineCount:
                self.mines.append(self.unmined.pop(0))
                i += 1
            self.values = dict()
            for plot in self.unmined:
                self.values[plot] = 0
            vectors = [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
            for mine in self.mines:
                self.values[mine] = 'x'
                adj = list()
                for vector in vectors:
                    adj.append(tuple(map(operator.add,mine,vector)))
                for plot in adj:
                    if plot in self.unmined:
                        self.values[plot] += 1
            self.cleared = list()
            self.flagged = list()
            self.gameOn = True
            self.winner = False
            
            if safeStart:
                zeroes = []
                for plot in self.unmined:
                    if self.values[plot] is 0:
                        zeroes.append(plot)
                self.dig(choice(zeroes))
                del zeroes
            self.display()
            
            while self.gameOn:
                play = self.player.getPlay()
                if play[0] == 'dig':
                    eval('self.dig')(play[1])
                elif play[0] == 'flag':
                    eval('self.flag')(play[1])
                elif play[0] == 'forfeit':
                    self.forfeit()
                if not play[0] == 'forfeit':
                    self.display()
                if self.unmined == []:
                    self.gameOn = False
                    self.winner = True
                sleep(.1)
            if self.winner:
                print('Winner!')
                print('Resolutions made: ',self.player.resolved)
                print('Chained answers: ',self.player.FPCount)
                print('Guesses made: ',self.player.guessed)
                print('Wrong choices made: ',self.wrong)
            else:
                self.reveal()
                print('Maybe next time...')
                print('Resolutions made: ',self.player.resolved)
                print('Chained answers: ',self.player.FPCount)
                print('Guesses made: ',self.player.guessed)
                print('Wrong choices made: ',self.wrong)
            
        else:
            print('More mines than plots.')
    
    def display(self):
        display = [' ']
        j = 1
        i = 1
        #line = '0> '
        line = ' '
        for plot in self.plots:
            if plot == self.lastmove:
                if plot in self.cleared:
                    char = self.values[plot]
                    if char is 0:
                        line += '\x1b[5;30;42m' + ' ' + '\x1b[0m' + ' '
                    elif char is 'x':
                        line += '\x1b[5;30;42m' + 'X' + '\x1b[0m' + ' '
                    else:
                        line += '\x1b[5;30;42m' + str(char) + '\x1b[0m' +' '
                elif plot in self.flagged:
                    line += '\x1b[5;30;42m' + '\u25B2' + '\x1b[0m' + ' '
                else:
                    line += '\u25A1 '
                if i%self.width == 0:
                    display.append(line)
                    #line = str(j)[-1:] + '> '
                    line = ' '
            else:
                if plot in self.cleared:
                    char = self.values[plot]
                    if char is 0:
                        line += '  '
                    elif char is 'x':
                        line += 'X '
                    else:
                        line += str(char) + ' '
                elif plot in self.flagged:
                    line += '\033[31m' + '\u25B2' + '\033[0m' + ' '
                else:
                    line += '\u25A1 '
                if i%self.width == 0:
                    display.append(line)
                    line = ' '
                j += 1
            i += 1
        display.append(' ')
        for line in display:
            print(line)
    
    def reveal(self):
        display = [' ']
        i = 1
        line = ' '
        for plot in self.plots:
            char = self.values[plot]
            if char is 0:
                line += '  '
            elif char is 'x':
                line += 'X '
            else:
                line += str(self.values[plot]) + ' '
            if i%self.width == 0:
                display.append(line)
                line = ' '
            i += 1
        i = 0
        for line in display:
            print(line)
            
    def dig(self,plot):
        if not plot in self.cleared and not plot in self.flagged and plot in self.plots:
            self.cleared.append(plot)
            if plot in self.unmined:
                while plot in self.unmined:
                    self.unmined.remove(plot)
            if self.values[plot] is 0:
                adjacent = self.adj(plot)
                for adjPlot in adjacent:
                    self.dig(adjPlot)
            elif self.values[plot] is 'x':
                self.wrong += 1
                print('Wrong choice...')
                self.gameOn = False
            elif self.cleared + self.mines == self.plots:
                self.winner = True
                self.gameOn = False
    
    def flag(self,plot):
        if plot in self.plots and plot not in self.cleared:
            if plot in self.flagged:
                self.flagged.remove(plot)
            else:
                self.flagged.append(plot)
        if not self.values[plot] == 'x':
            print('Wrong choice...')
            self.wrong += 1
    def forfeit(self,plot = 0):
        self.gameOn = False
        
    def adj(self,plot):
        vectors = [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
        adjacent = list()
        for vector in vectors:
            a = tuple(map(operator.add,plot,vector))
            if plot in self.cleared:
                if a not in self.cleared and a in self.plots:
                    adjacent.append(a)
            else:
                if a in self.cleared:
                    adjacent.append(a)
        return adjacent
    
    def getValue(self,plot):
        if plot in self.cleared:
            return self.values[plot]
        else:
            return None

#--------------------text-based human player; it was only used to test the game
    
class human(object):
    def __init__ (self): # 'human', ...
        self.game = None
        
    def getPlay(self):
        play = input('Next move? ').split()
        if play[0] == 'dig':
            if len(play)>1:
                if eval(play[1]) in self.game.plots:
                    play[1] = eval(play[1])
                    return play
                else:
                    print(str(play[1] + ' isn\'t on the board...'))
                    return self.getPlay()
            else:
                print('You forgot to say where to dig...')
                return self.getPlay()
        elif play[0] == 'flag':
            if len(play)>1:
                if eval(play[1]) in self.game.plots:
                    play[1] = eval(play[1])
                    return play
                else:
                    print(str(play[1] + ' isn\'t on the board...'))
                    return self.getPlay()
            else:
                print('You forgot to say where to flag...')
                return self.getPlay()
        elif play[0] == 'forfeit' or play[0] == 'quit' or play[0] == 'exit':
            return ['forfeit']
        else:
            print('"' + str(play[0]) + '"' + ' isn\'t a valid input.')
            return self.getPlay()
    def helpTheBot(self):
        return self.getPlay()
#--------------------------------------------------------------------------Main

Hal = MSFoL.LocalFoLPlayer()
test = Minesweeper(Hal,width=20,height=20,mineCount=100)
