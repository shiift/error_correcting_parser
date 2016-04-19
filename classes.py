import re


class BreakIt(Exception):
    """Exception used as a nested break"""
    pass


class Production(object):
    """Production conatins a left hand side, right hand side and number of
    errors for the production as well as tagging information for inserted,
    deleted, replaced, prefix and suffix characters for errors productions."""
    REGEX = r'->([0-9]+)?'
    EPSILON = '__e'
    H_SYM = '__H'
    I_SYM = '__I'

    def __init__(self, arg0, arg1=None, arg2=None):
        self.exclude_nullable = False
        self.exclude_units = False
        self.inserted = False
        self.deleted = ""
        self.replaced = ""
        self.prefix = ""
        self.suffix = ""
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
        self.inserted = True if pieces[0].strip() == 'True' else False
        self.replaced = pieces[1].strip()
        self.deleted = pieces[2].strip()
        self.prefix = pieces[3].strip()
        self.suffix = pieces[4].strip()

    def to_tuple(self):
        return self.lhs, self.rhs, self.errors

    def set_deleted(self, value):
        self.deleted = value
        return self

    def set_replaced(self, value):
        self.replaced = value
        return self

    def set_inserted(self, value=True):
        self.inserted = value
        return self

    def set_prefix(self, prefix_values):
        self.prefix = prefix_values
        return self

    def set_suffix(self, suffix_values):
        self.suffix = suffix_values
        return self

    def is_T(self):
        return len(self.rhs.split()) == 1 and self.rhs.islower()

    def is_NT(self):
        return not self.is_T()

    def is_Unit(self):
        return len(self.rhs.split()) == 1

    def __repr__(self):
        return "{0} ->{1} {2}:{3}:{4}:{5}:{6}:{7}".format(
            self.lhs, self.errors, self.rhs,
            self.inserted, self.replaced, self.deleted,
            self.prefix, self.suffix)


class Grammar(object):
    """Grammar conatins a list of productions, a list of terminals, a list of
    non-terminals, and the top level symbol character ('S' by default)"""
    TOP_SYMBOL = 'S'

    def __init__(self):
        self.productions = {}
        self.terminals = {}
        self.nonterminals = {}

    def add_production(self, new_production):
        if isinstance(new_production, str):
            new_production = Production(new_production)
        self.__add_to(self.productions, new_production)
        if new_production.is_T():
            self.__add_to(self.terminals, new_production)
        else:
            self.__add_to(self.nonterminals, new_production)
        return new_production

    def get_all(self, group):
        for lhs, nts in group.items():
            for rhs, nonterminal in nts.items():
                yield lhs, rhs, nonterminal

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

    def get_all(self, symbol, depth, input_size):
        j_boundry = None
        for i, tup_hash in enumerate(self.data[symbol]):
            j_boundry = i + 1 + depth
            if j_boundry <= input_size + 1:
                for j, tup in list(tup_hash.items()):
                    if j < j_boundry:
                        yield tup

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
                for _, tup in self.get(i, j).items():
                    str_list.append("({0}, {1}) ".format(tup[0], tup[1]))
                str_list.append("|")
            str_list.append("\n")
        return "".join(str_list)


class Node(object):
    def __init__(self, i, j, production):
        self.i = i
        self.j = j
        self.production = production
        self.left = None
        self.right = None

    def print_tree(self, i, accumulator):
        str_list = []
        for _ in range(i):
            str_list.append(" ")
        str_list.append(str(self.production) + "\n")
        if self.left is not None:
            str_list.append(self.left.print_tree(i+1, accumulator))
        if self.right is not None:
            str_list.append(self.right.print_tree(i+1, accumulator))
        return "".join(str_list)

    def __repr__(self):
        return self.print_tree(0, "")
