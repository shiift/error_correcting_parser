import re

class BreakIt(Exception): pass

"""Production conatins a left hand side, right hand side and number of errors
for the production."""
class Production:
    regex = r'->([0-9]+)?'
    def __init__(self, arg0, arg1=None, arg2=None):
        if arg1 == None:
            self.set_str(arg0)
        else:
            self.set_vars(arg0, arg1, arg2)
    def set_str(self, string):
        if not string:
            return
        m = re.search(self.regex, string)
        if(m):
            try:
                self.errors = int(re.sub(r'->', '', m.group(0)))
            except ValueError:
                self.errors = 0
                pass
        else:
            raise ValueError("Productions must be in the form: S ->0 A B")
        lhs_rhs = re.split(self.regex, string)
        self.lhs = lhs_rhs[0].strip()
        self.rhs = lhs_rhs[2].strip()
    def set_vars(self, lhs, errors, rhs):
        self.lhs = lhs
        self.errors = errors
        self.rhs = rhs
        return self
    def is_T(self):
        return len(self.rhs.split()) == 1 and self.rhs.islower()
    def is_NT(self):
        return not self.is_T()
    def __repr__(self):
        return self.lhs + " ->" + str(self.errors) + " " + self.rhs

"""Grammar conatins a list of productions, a list of terminals, a list of
non-terminals, and the top level symbol character ('S' by default)"""
class Grammar:
    S = 'S'
    def __init__(self):
        self.productions = []
        self.terminals = []
        self.nonterminals = []
    def add_production(self, string):
        p = Production(string)
        self.productions.append(p)
        if p.is_T():
            self.terminals.append(p)
        else:
            self.nonterminals.append(p)
    def __repr__(self):
        string = "nonterminals:\n"
        for nt in self.nonterminals:
            string += "\t{}\n".format(nt)
        string += "terminals:\n"
        for t in self.terminals:
            string += "\t{}\n".format(t)
        return string

class Lookup:
    def __init__(self, productions, size):
        self.data = {}
        for production in productions:
            lhs = production.lhs
            self.data[lhs] = []
            for i in range(0, size):
                self.data[lhs].append([])
    def insert(self, lhs, tup):
        tups = self.get(lhs, tup[0])
        for i in range(len(tups)):
            if tups[i][1] == tup[1]:
                if tups[i][2] > tup[2]:
                    tups.pop(i)
                    break
                else:
                    return
        self.get(lhs, tup[0]).append(tup)
    def get(self, lhs, i):
        return self.data[lhs][i-1]
    def get_all(self, lhs):
        newlist = []
        for l in self.data[lhs]:
            newlist.extend(l)
        return newlist
    def __repr__(self):
        return str(self.data.keys());

class Matrix:
    def __init__(self, size):
        self.size = size
        self.data = [None] * size
        for i in range(0, size):
            self.data[i] = [[] for _dummy in xrange(size-i)]
    def insert(self, i, j, tup):
        tups = self.get(i, j)
        for k in range(len(tups)):
            if tups[k][0] == tup[0]:
                if tups[k][1] > tup[1]:
                    tups.pop(k)
                    break
                else:
                    return
        self.get(i,j).append(tup)
    def get(self, i, j):
        if i >= j:
            raise ValueError("Cannot get {} >= {}".format(i, j))
        return self.data[i-1][j-i-1]
    def __repr__(self):
        s = ""
        size = self.size
        for j in range(2, size+2):
            for i in range(1, j):
                s += str(self.get(i, j)) + "; "
            s += "\n"
        return s

class Node:
    def __init__(self, i, j, p):
        self.i = i
        self.j = j
        self.p = p
        self.left = None
        self.right = None
    def print_node(self, i, s):
        sp = ""
        for j in range(i):
            sp += " "
        sn = sp + str(self.p) + "\n"
        sl = ""
        sr = ""
        if self.left != None:
            sl = self.left.print_node(i+1, s)
        if self.right != None:
            sr = self.right.print_node(i+1, s)
        return sn + sl + sr
    def __repr__(self):
        return self.print_node(0, "")