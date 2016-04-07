import re


class Production:
    """Production conatins a left hand side, right hand side and number of
    errors for the production."""
    regex = r'->([0-9]+)?'

    def __init__(self, arg0, arg1=None, arg2=None):
        self.marked = False
        if arg1 is None:
            self.set_str(arg0)
        else:
            self.set_vars(arg0, arg1, arg2)

    def set_str(self, string):
        if not string:
            return
        match = re.search(self.regex, string)
        if match:
            try:
                self.errors = int(re.sub(r'->', '', match.group(0)))
            except ValueError:
                self.errors = 0
        else:
            raise ValueError("Productions must be in the form: S ->0 A B\n" +
                             "Cannot use {}".format(string))
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
        return "{0} ->{1} {2}".format(self.lhs, self.errors, self.rhs)


class Grammar:
    """Grammar conatins a list of productions, a list of terminals, a list of
    non-terminals, and the top level symbol character ('S' by default)"""
    S = 'S'

    def __init__(self):
        self.productions = []
        self.terminals = []
        self.nonterminals = []

    def add_production(self, string):
        production = Production(string)
        self.productions.append(production)
        if production.is_T():
            self.terminals.append(production)
        else:
            self.nonterminals.append(production)

    def __repr__(self):
        string = "nonterminals:\n"
        for nonterminal in self.nonterminals:
            string += "\t{}\n".format(nonterminal)
        string += "terminals:\n"
        for terminal in self.terminals:
            string += "\t{}\n".format(terminal)
        return string


class Lookup:
    def __init__(self, productions, size):
        self.data = {}
        for production in productions:
            lhs = production.lhs
            self.data[lhs] = []
            self.data[lhs].extend([[] for x in range(size)])

    def insert(self, lhs, new_tup):
        tups = self.get(lhs, new_tup[0])
        for i, old_tup in enumerate(tups):
            if old_tup[1] == new_tup[1]:
                if old_tup[2] > new_tup[2]:
                    tups.pop(i)
                    break
                else:
                    return
        self.get(lhs, new_tup[0]).append(new_tup)

    def get(self, lhs, i):
        return self.data[lhs][i-1]

    def get_all(self, lhs):
        newlist = []
        for sublist in self.data[lhs]:
            newlist.extend(sublist)
        return newlist

    def __repr__(self):
        return str(self.data.keys())


class Matrix:
    def __init__(self, size):
        self.size = size
        self.data = [None] * size
        for i in range(0, size):
            self.data[i] = [[] for x in range(size-i)]

    def insert(self, i, j, new_tup):
        tups = self.get(i, j)
        for k, old_tup in enumerate(tups):
            if old_tup[0] == new_tup[0]:
                if old_tup[1] > new_tup[1]:
                    tups.pop(k)
                    break
                else:
                    return
        self.get(i, j).append(new_tup)

    def get(self, i, j):
        if i >= j:
            raise IndexError((
                "Cannot get {} >= {} of M. "
                "Location outside of range.").format(i, j))
        return self.data[i-1][j-i-1]

    def __repr__(self):
        str_list = []
        for j in range(2, self.size+2):
            for i in range(1, j):
                str_list.append("%s|" % self.get(i, j))
            str_list.append("\n")
        return "".join(str_list)


class Node:
    def __init__(self, i, j, p):
        self.i = i
        self.j = j
        self.p = p
        self.left = None
        self.right = None

    def print_node(self, i, s):
        str_list = []
        for j in range(i):
            str_list.append(" ")
        str_list.append(str(self.p) + "\n")
        if self.left is not None:
            str_list.append(self.left.print_node(i+1, s))
        if self.right is not None:
            str_list.append(self.right.print_node(i+1, s))
        return "".join(str_list)

    def __repr__(self):
        return self.print_node(0, "")
