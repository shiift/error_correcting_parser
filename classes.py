import re


class Production:
    """Production conatins a left hand side, right hand side and number of
    errors for the production."""
    REGEX = r'->([0-9]+)?'
    NONE = 'N'
    INSERTED = 'INS'
    REPLACED = 'REP'
    DELETED = 'DEL'

    def __init__(self, arg0, arg1=None, arg2=None):
        self._type = Production.NONE
        self._correction = None
        self._prefix = ""
        self._suffix = ""
        if arg1 is None:
            self.__set_str(arg0)
        else:
            self.__set_vars(arg0, arg1, arg2)

    def __set_str(self, string):
        if not string:
            return
        match = re.search(self.REGEX, string)
        if match:
            try:
                self.errors = int(re.sub(r'->', '', match.group(0)))
            except ValueError:
                self.errors = 0
        else:
            raise ValueError("Productions must be in the form: S ->0 A B\n" +
                             "Cannot use {}".format(string))
        lhs_rhs = re.split(self.REGEX, string)
        self.lhs = lhs_rhs[0].strip()
        self.rhs = lhs_rhs[2].strip()

    def __set_vars(self, lhs, errors, rhs):
        self.lhs = lhs
        self.errors = errors
        self.rhs = rhs
        return self

    def to_tuple(self):
        return self.lhs, self.rhs, self.errors

    def set_inserted(self):
        self._type = Production.INSERTED
        self._correction = True

    def set_replaced(self, replacement_value):
        self._type = Production.REPLACED
        self._correction = replacement_value

    def set_deleted(self, deleted_values):
        self._type = Production.DELETED
        self._correction = deleted_values

    def inserted(self):
        if self._type == Production.INSERTED:
            return self._correction
        return False

    def replaced(self):
        if self._type == Production.REPLACED:
            return self._correction
        return ""

    def deleted(self):
        if self._type == Production.DELETED:
            return self._correction
        return ""

    def set_prefix(self, prefix_values):
        self._prefix = prefix_values

    def set_suffix(self, suffix_values):
        self._suffix = suffix_values

    def prefix(self):
        return self._prefix

    def suffix(self):
        return self._suffix

    def is_T(self):
        return len(self.rhs.split()) == 1 and self.rhs.islower()

    def is_NT(self):
        return not self.is_T()

    def __str__(self):
        return "{0:>8} ->{1:>2} {2:>8}::{3:>10}:{4}::{5}::{6}".format(
            self.lhs, self.errors, self.rhs,
            self._type, self._correction, self.prefix(), self.suffix())

    def __repr__(self):
        return "{0} ->{1} {2}::{3}:{4}::{5}::{6}".format(
            self.lhs, self.errors, self.rhs,
            self._type, self._correction, self.prefix(), self.suffix())


class Grammar:
    """Grammar conatins a list of productions, a list of terminals, a list of
    non-terminals, and the top level symbol character ('S' by default)"""
    TOP_SYMBOL = 'S'

    def __init__(self):
        self.productions = {}
        self.terminals = {}
        self.nonterminals = {}

    def add_production(self, string):
        new_production = Production(string)
        self.__add_to(self.productions, new_production)
        if new_production.is_T():
            self.__add_to(self.terminals, new_production)
        else:
            self.__add_to(self.nonterminals, new_production)
        return new_production

    def __add_to(self, group, production):
        if production.lhs not in group:
            group[production.lhs] = {}
        group[production.lhs][production.rhs] = production


class Lookup:
    def __init__(self, productions, size):
        self.data = {}
        for key in productions:
            self.data[key] = []
            for _ in range(0, size):
                self.data[key].append({})

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
