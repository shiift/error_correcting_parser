import re


class Production(object):
    """Production conatins a left hand side, right hand side and number of
    errors for the production."""
    REGEX = r'->([0-9]+)?'
    H_SYM = '__H'
    I_SYM = '__I'
    INSERTED = 0
    REPLACED = 1
    DELETED = 2

    def __init__(self, arg0, arg1=None, arg2=None):
        self._insert = False
        self._delete = ""
        self._replace = ""
        self._prefix = ""
        self._suffix = ""
        if arg1 is None:
            self.__set_str(arg0)
        else:
            self.__set_vars(arg0, arg1, arg2)

    def __set_str(self, string):
        if not string:
            return
        string = string.strip()
        pieces = string.split(':')
        if len(pieces) > 1:
            self.__set_correction_vars(pieces[1:])
            string = pieces[0]
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

    def __set_correction_vars(self, pieces):
        self._insert = True if pieces[0].strip() == 'True' else False
        self._replace = pieces[1].strip()
        self._delete = pieces[2].strip()
        self._prefix = pieces[3].strip()
        self._suffix = pieces[4].strip()

    def to_tuple(self):
        return self.lhs, self.rhs, self.errors

    def set_type(self, new_type, value=True):
        if new_type == self.INSERTED:
            self._insert = value
        elif new_type == self.REPLACED:
            self._replace = value
        elif new_type == self.DELETED:
            self._delete = value
        return self

    def inserted(self):
        return self._insert

    def replaced(self):
        return self._replace

    def deleted(self):
        return self._delete

    def set_prefix(self, prefix_values):
        self._prefix = prefix_values
        return self

    def set_suffix(self, suffix_values):
        self._suffix = suffix_values
        return self

    def prefix(self):
        return self._prefix

    def suffix(self):
        return self._suffix

    def is_T(self):
        return len(self.rhs.split()) == 1 and self.rhs.islower()

    def is_NT(self):
        return not self.is_T()

    def is_Unit(self):
        if self.is_T() or (self.is_NT() and len(self.rhs.split()) == 1):
            return True
        return False

    # def __str__(self):
    #     return "{0:>5} ->{1:>3} {2:>8}:\t{3}:\t{4}:\t{5}:\t{6}:\t{7}".format(
    #         self.lhs, self.errors, self.rhs,
    #         self._insert, self._replace, self._delete,
    #         self.prefix(), self.suffix())

    def __repr__(self):
        return "{0} ->{1} {2}:{3}:{4}:{5}:{6}:{7}".format(
            self.lhs, self.errors, self.rhs,
            self._insert, self._replace, self._delete,
            self.prefix(), self.suffix())


class Grammar(object):
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

    def __repr__(self):
        string = ""
        for productions in self.productions.values():
            for production in productions.values():
                string += str(production) + "\n"
        return string[:-1]


class Lookup(object):
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


class Matrix(object):
    def __init__(self, size):
        self.size = size
        self.data = [None] * size
        for i in range(0, size):
            self.data[i] = [{} for _ in range(size-i)]

    def insert(self, symbol, i, j, errors, production):
        tup_hash = self.data[i-1][j-i-1]
        if symbol in tup_hash:
            if tup_hash[symbol][1] <= errors:
                return
        tup_hash[symbol] = (symbol, errors, production)

    def get(self, i, j):
        return self.data[i-1][j-i-1]

    def __repr__(self):
        str_list = []
        for j in range(2, self.size+2):
            for i in range(1, j):
                str_list.append("%s|" % self.get(i, j))
            str_list.append("\n")
        return "".join(str_list)


class Node(object):
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
