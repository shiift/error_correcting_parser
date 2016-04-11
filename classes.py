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
    TOP_SYMBOL = 'S'

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
            symbol = production.lhs
            self.data[symbol] = []
            for _ in range(0, size):
                self.data[symbol].append({})

    def insert(self, symbol, i, j, errors):
        tup_hash = self.data[symbol][i-1]
        if j in tup_hash:
            if tup_hash[j][2] <= errors:
                return
        tup_hash[j] = (i, j, errors)

    def get_all(self, symbol, s_var, input_boundry):
        newlist = []
        for i, tup_hash in enumerate(self.data[symbol]):
            if i + 1 + s_var <= input_boundry:
                newlist.extend([
                    x for j, x in tup_hash.items()
                    if j < i + 1 + s_var
                ])
        return newlist

    def get(self, symbol, i):
        return self.data[symbol][i-1]

    def __repr__(self):
        return str(self.data.keys())


class Matrix:
    def __init__(self, size):
        self.size = size
        self.data = [None] * size
        for i in range(0, size):
            self.data[i] = [{} for _ in range(size-i)]

    def insert(self, symbol, i, j, errors):
        tup_hash = self.data[i-1][j-i-1]
        if symbol in tup_hash:
            if tup_hash[symbol][1] <= errors:
                return
        tup_hash[symbol] = (symbol, errors)

    def get(self, i, j):
        return self.data[i-1][j-i-1]

    def __repr__(self):
        str_list = []
        for j in range(2, self.size+2):
            for i in range(1, j):
                str_list.append("%s|" % self.get(i, j))
            str_list.append("\n")
        return "".join(str_list)


class Node:
    def __init__(self, i, j, production):
        self.i = i
        self.j = j
        self.production = production
        self.left = None
        self.right = None

    def print_node(self, i, accumulator):
        str_list = []
        for _ in range(i):
            str_list.append(" ")
        str_list.append(str(self.production) + "\n")
        if self.left is not None:
            str_list.append(self.left.print_node(i+1, accumulator))
        if self.right is not None:
            str_list.append(self.right.print_node(i+1, accumulator))
        return "".join(str_list)

    def __repr__(self):
        return self.print_node(0, "")
