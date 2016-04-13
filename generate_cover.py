import argparse
import copy

import classes


class Production(classes.Production):
    """Production conatins a left hand side, right hand side and number of
    errors for the production. Double underscore in front of the symbol is
    reserved and __e can be used for epsilon transitions.
    Reserved: __H, __I
    """
    H_SYM = '__H'
    I_SYM = '__I'
    EPSILON = '__e'

    def __init__(self, arg0, arg1=None, arg2=None):
        classes.Production.__init__(self, arg0, arg1, arg2)
        self.exclude = False

    def is_Unit(self):
        if self.is_T() or (self.is_NT() and len(self.rhs.split()) == 1):
            return True
        return False


class Grammar(classes.Grammar):
    """Grammar conatins a list of productions, a list of terminals, a list of
    non-terminals, and the top level symbol character ('S' by default)
    """
    def __init__(self):
        classes.Grammar.__init__(self)
        self.chars = {}
        self.nullable = {}

    def add_production(self, new_production):
        if isinstance(new_production, str):
            new_production = Production(new_production)
        self.__add_to(self.productions, new_production)
        if new_production.is_T():
            self.__add_to(self.terminals, new_production)
            if new_production.rhs == Production.EPSILON:
                self.nullable[new_production.lhs] = 1
            else:
                self.chars[new_production.rhs] = True
        else:
            self.__add_to(self.nonterminals, new_production)
        return new_production

    def try_add(self, new_production):
        if isinstance(new_production, str):
            new_production = Production(new_production)
        lhs, rhs, errors = new_production.to_tuple()
        if lhs in self.productions:
            if rhs in self.productions[lhs]:
                if errors < self.productions[lhs][rhs].errors:
                    self.productions[lhs].pop(rhs)
                else:
                    return False
                if new_production.is_T():
                    if errors < self.terminals[lhs][rhs].errors:
                        self.terminals[lhs].pop(rhs)
                else:
                    if errors < self.nonterminals[lhs][rhs].errors:
                        self.nonterminals[lhs].pop(rhs)
        self.add_production(new_production)
        return True

    def __repr__(self):
        string = ""
        for productions in self.productions.values():
            for production in productions.values():
                string += str(production) + "\n"
        return string[:-1]


def construct_covering(grammar):
    grammar_p = Grammar()
    grammar_p = copy.deepcopy(grammar)
    grammar_p = simple_rules(grammar_p, grammar)
    for lhs in grammar_p.productions:
        compute_nullable(grammar_p, lhs)
    print(grammar_p)
    print()
    for symbol in grammar_p.nonterminals:
        add_nullable_productions(grammar_p, symbol)
    print(grammar_p)
    return grammar_p


def simple_rules(grammar_p, grammar):
    grammar_p.add_production(
        '{0} -> {0} {1}'.format(Production.H_SYM, Production.I_SYM))
    grammar_p.add_production(
        '{0} -> {1}'.format(Production.H_SYM, Production.I_SYM))
    for char in grammar.chars:
        grammar_p.add_production(
            Production(
                '{0} ->1 {1}'.format(Production.I_SYM, char)
            ).set_type(Production.INSERTED)
        )
    for lhs, terminals_lhs in grammar.terminals.items():
        for rhs in terminals_lhs:
            grammar_p.try_add(
                '{0} -> {1} {2}'.format(lhs, lhs, Production.H_SYM)
            )
            grammar_p.try_add(
                '{0} -> {1} {2}'.format(lhs, Production.H_SYM, lhs)
            )
            grammar_p.try_add(
                Production(
                    '{0} ->{1} {2}'.format(lhs, 1, Production.EPSILON)
                ).set_type(Production.DELETED, rhs)
            )
            for char in [x for x in grammar.chars if x is not rhs]:
                grammar_p.try_add(
                    Production(
                        '{0} ->{1} {2}'.format(lhs, 1, char)
                    ).set_type(Production.REPLACED, rhs)
                )
    return grammar_p


def compute_nullable(grammar, symbol):
    if symbol not in grammar.productions:
        return False
    for production in grammar.productions[symbol].values():
        if production.exclude:
            continue
        production.exclude = True
        if not production.is_Unit():
            rhs_b, rhs_c = production.rhs.split()
            if rhs_b == symbol or rhs_c == symbol:
                production.exclude = False
                continue
            if (rhs_b not in grammar.nullable and
                    not compute_nullable(grammar, rhs_b)):
                production.exclude = False
                return False
            if (rhs_c not in grammar.nullable and
                    not compute_nullable(grammar, rhs_c)):
                production.exclude = False
                return False
            sum_null = grammar.nullable[rhs_b] + grammar.nullable[rhs_c]
            if (symbol not in grammar.nullable or
                    sum_null < grammar.nullable[symbol]):
                grammar.nullable[symbol] = sum_null
                production.exclude = False
                return True
        else:
            rhs_b = production.rhs
            if (rhs_b not in grammar.nullable and
                    not compute_nullable(grammar, rhs_b)):
                production.exclude = False
                return False
            if (symbol not in grammar.nullable or
                    grammar.nullable[rhs_b] < grammar.nullable[symbol]):
                grammar.nullable[symbol] = grammar.nullable[rhs_b]
                production.exclude = False
                return True
        production.exclude = False
    return False


def add_nullable_productions(grammar, symbol):
    nonterminals = copy.deepcopy(grammar.nonterminals)
    for production in nonterminals[symbol].values():
        if not production.is_Unit():
            rhs_b, rhs_c = production.rhs.split()
            if rhs_b in grammar.nullable:
                grammar.try_add('{} ->{} {}'.format(
                    symbol,
                    production.errors+grammar.nullable[rhs_b],
                    rhs_c))
            if rhs_c in grammar.nullable:
                grammar.try_add('{} ->{} {}'.format(
                    symbol,
                    production.errors+grammar.nullable[rhs_c],
                    rhs_b))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('grammar_file',
                        type=argparse.FileType('r'),
                        help="grammar file of rule to use")
    args = parser.parse_args()

    grammar = Grammar()
    for line in args.grammar_file:
        grammar.add_production(line)
    construct_covering(grammar)

if __name__ == '__main__':
    main()
