# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 15:03:37 2016

@author: arewh
"""
from collections import deque
import operator
from itertools import combinations,product
from random import choice
from functools import reduce

def getPlot(statementString):
    if statementString[0] == '-':
        return eval(statementString[1:])
    else:
        return eval(statementString)
        
def ncr(n,r):
    r = min(r,n-r)
    if r == 0:
        return 1
    numerator = reduce(operator.mul,range(n,n-r,-1))
    denominator = reduce(operator.mul,range(1,r+1))
    return numerator // denominator
def neg(statementString):
    if statementString[0] == '-':
        return statementString[1:]
    else:
        return '-' + statementString

def resolve(statementsOne,statementsTwo):
    new = set()
    for statement in statementsOne:
        if neg(statement) in statementsTwo:
            newSet = set(statementsOne.union(statementsTwo))
            newSet.remove(statement)
            newSet.remove(neg(statement))
            toggle = True
            for statement in newSet:
                if neg(statement) in newSet:
                    toggle = False
                    continue
            if toggle:
                new.add(frozenset(newSet))
    return new

def makeBall(i):
    if i == 1:
        ball = set(product(range(-1,2),range(-1,2)))
        return ball
    bigBall = set(product(range(-i,i+1),range(-i,i+1)))
    littleBall = set(product(range(-i+1,i),range(-i+1,i)))
    return bigBall.difference(littleBall)
#------------------------------------------------------------------------------
class LocalFoLPlayer(object):
    def __init__ (self):
        self.game = None
        self.frontier = set()
        self.moves = deque()
        self.resolved = 0
        self.guessed = 0
        self.flagged = 0
        self.recentResolutions = set()
        self.FPCount = 0
        self.DNF = set()
    def getPlay(self):
        if self.moves:
            move = self.moves.pop()
            self.game.lastmove = move[1]
            return move
        self.populate()
        if self.moves:
            move = self.moves.pop()
            self.game.lastmove = move[1]
            return move
        print('Forward Chaining...')
        self.forwardProp()
        if self.moves:
            move = self.moves.pop()
            self.game.lastmove = move[1]
            return move
        checked = set()
        if self.recentResolutions.issuperset(self.frontier):
            self.recentResolutions = set()
        print('Resolving...')
        for plot in self.frontier:
            if not plot in self.recentResolutions:
                checked.add(plot)
                self.recentResolutions.add(plot)
                test = self.resolution(plot)
                if test:
                    self.resolved += 1
                    self.flagged += 1
                    self.game.lastmove = eval(plot)
                    return ['flag',eval(plot)]
                test = self.resolution(neg(plot))
                if test:
                    self.resolved += 1
                    self.game.lastmove = eval(plot)
                    return ['dig',eval(plot)]
        unchecked = self.frontier.difference(checked)
        for plot in unchecked:
            self.recentResolutions.add(plot)
            test = self.resolution(plot)
            if test:
                self.resolved += 1
                self.flagged += 1
                self.game.lastmove = eval(plot)
                return ['flag',eval(plot)]
            test = self.resolution(neg(plot))
            if test:
                self.resolved += 1
                self.game.lastmove = eval(plot)
                return ['dig',eval(plot)]
        print('I have to guess...')
        self.guessed += 1
        if self.frontier:
            plot = choice(list(self.frontier))
        else:
            plot = choice(list(self.game.unmined))
        self.game.lastmove = eval(plot)
        return ['dig',eval(plot)]
    def adj(self,plot): #returns adjacent uncleared plots
        vectors = [(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1)]
        adjacent = set()
        for vector in vectors:
            a = tuple(map(operator.add,plot,vector))
            if a in self.game.plots and not a in self.game.cleared:
                adjacent.add(str(a))
        return adjacent
    def populate(self):
        self.frontier = set()
        for plot in self.game.cleared:
            adjacent = self.adj(plot)
            mineCount = self.game.values[plot]
            removals = set()
            for otherPlot in adjacent:
                if eval(otherPlot) in self.game.flagged:
                    removals.add(otherPlot)
                    mineCount -= 1
                else:
                    self.frontier.add(otherPlot)
            adjacent = adjacent.difference(removals)
            plotCount = len(adjacent)
            safeCount = plotCount - mineCount
            if plotCount:
                if safeCount == plotCount:
                    for string in adjacent:
                        move = ['dig',eval(string)]
                        if not move in self.moves and not eval(string) in self.game.cleared:
                            self.moves.append(move)
                            #self.frontier.remove(string)
                elif mineCount == plotCount:
                    for string in adjacent:
                        move = ['flag',eval(string)]
                        if not move in self.moves and not eval(string) in self.game.flagged:
                            self.moves.append(move)
                            self.flagged += 1
                            #self.frontier.remove(string)
    def forwardProp(self):
        remainingPlotCount = len(self.game.plots) - self.flagged - len(self.game.cleared)
        remainingMineCount = self.game.mineCount - self.flagged
        remainingSafeCount = remainingPlotCount - remainingMineCount
        preclauses = set()
        if ncr(remainingPlotCount,remainingMineCount) < 40:
            remainingPlots = set(self.game.plots).difference(set(self.game.cleared))
            remainingPlots = remainingPlots.difference(set(self.game.flagged))
            if not remainingSafeCount == remainingPlotCount:
                positives = list(combinations(remainingPlots,remainingSafeCount+1))
                for combination in positives:
                    hold = set()
                    for plot in combination:
                        hold.add(str(plot))
                    hold = frozenset(hold)
                    preclauses.add(hold)
            if not remainingMineCount == remainingPlotCount:
                negatives = list(combinations(remainingPlots,remainingMineCount+1))
                for combination in negatives:
                    hold = set()
                    for plot in combination:
                        hold.add(neg(str(plot)))
                    hold = frozenset(hold)
                    preclauses.add(hold)
            print(preclauses)
        i = 2
        while i < self.game.height:
            j = 2
            while j < self.game.width:
                b = 1
                clauses = preclauses
                new = set()
                checked = set()
                center = (i,j)
                toggle = False
                if not center in self.DNF:
                    while b < 6 and len(clauses)<300:
                        ball = makeBall(b)
                        for vector in ball:
                            plot = tuple(map(operator.add,center,vector))
                            if plot in self.game.cleared:
                                remaining = self.game.values[plot]
                                adjacent = self.adj(plot)
                                removals = set()
                                for a in adjacent:
                                    if eval(a) in self.game.flagged or ['flag',eval(a)] in self.moves:
                                        remaining -= 1
                                        removals.add(a)
                                adjacent = adjacent.difference(removals)
                                plotCount = len(adjacent)
                                safeCount = plotCount - remaining
                                if not safeCount == plotCount:
                                    positives = list(combinations(adjacent,safeCount+1))
                                    for combination in positives:
                                        hold = set()
                                        for stringPlot in combination:
                                            hold.add(stringPlot)
                                        hold = frozenset(hold)
                                        clauses.add(hold)
                                if not remaining == plotCount:
                                    negatives = list(combinations(adjacent,remaining+1))
                                    for combination in negatives:
                                        hold = set()
                                        for stringPlot in combination:
                                            hold.add(neg(stringPlot))
                                        hold = frozenset(hold)
                                        clauses.add(hold)
                            elif not plot in self.game.flagged:
                                toggle = True
                        toggle1 = True
                        while toggle1 and len(clauses) < 300:
                            pairs = list(combinations(clauses,2))
                            for pair in pairs:
                                if not pair in checked:
                                    checked.add(pair)
                                    resolvents = resolve(pair[0],pair[1])
                                    resolvents = resolvents.difference(new)
                                    for clause in resolvents:
                                        if len(clause) == 1:
                                            for statement in clause:
                                                if statement[0] == '-':
                                                    plot = eval(statement[1:])
                                                    move = ['dig',plot]
                                                    if not plot in self.game.cleared and not move in self.moves:
                                                        self.moves.append(move)
                                                        self.FPCount += 1
                                                else:
                                                    plot = eval(statement)
                                                    move = ['flag',plot]
                                                    if not plot in self.game.flagged and not move in self.moves:
                                                        self.moves.append(move)
                                                        self.flagged += 1
                                                        self.FPCount += 1
                                    new = new.union(resolvents)
                            if new.issubset(clauses):
                                toggle1 = False
                            else:
                                clauses = clauses.union(new)
                        b += 1
                if not toggle:
                    self.DNF.add(center)
                j += 3
            i += 3
    def resolution(self,plotString):
        clauses = set()
        negatedGoal = frozenset({neg(plotString)})
        clauses.add(negatedGoal)
        i = 1
        new = set()
        checked = set()
        toggle = True
        plots = set()
        while i<15 and len(clauses)<400 and toggle:
            ball = makeBall(i)
            for vector in ball:
                plot = tuple(map(operator.add,getPlot(plotString),vector))
                if plot in self.game.cleared:
                    plots.add(plot)
                    remaining = self.game.values[plot]
                    adjacent = self.adj(plot)
                    removals = set()
                    for a in adjacent:
                        if eval(a) in self.game.flagged or ['flag',eval(a)] in self.moves:
                            remaining -= 1
                            removals.add(a)
                    adjacent = adjacent.difference(removals)
                    plotCount = len(adjacent)
                    safeCount = plotCount - remaining
                    if not safeCount == plotCount:
                        positives = list(combinations(adjacent,safeCount+1))
                        for combination in positives:
                            hold = set()
                            for stringPlot in combination:
                                hold.add(stringPlot)
                            hold = frozenset(hold)
                            clauses.add(hold)
                    if not remaining == plotCount:
                        negatives = list(combinations(adjacent,remaining+1))
                        for combination in negatives:
                            hold = set()
                            for stringPlot in combination:
                                hold.add(neg(stringPlot))
                            hold = frozenset(hold)
                            clauses.add(hold)
            if plots.issuperset(set(self.game.cleared)):
                toggle = False
            toggle1 = True
            while toggle1 and len(clauses) < 400:
                pairs = list(combinations(clauses,2))
                for pair in pairs:
                    if not pair in checked:
                        checked.add(pair)
                        resolvents = resolve(pair[0],pair[1])
                        if frozenset() in resolvents:
                            return True
                        new = new.union(resolvents)
                if new.issubset(clauses):
                    toggle1 = False
                else:
                    clauses = clauses.union(new)
            i += 1
        return False