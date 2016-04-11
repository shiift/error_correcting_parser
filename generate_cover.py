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

    def add_production(self, string):
        new_production = Production(string)
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

    def try_add(self, string):
        new_production = Production(string)
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
        self.add_production(string)
        return True

    def __repr__(self):
        string = ""
        for productions in self.productions.values():
            for production in productions.values():
                string += str(production) + "\n"
        return string[:-1]


def construct_covering(grammar):
    grammar_prime = Grammar()
    grammar_prime = copy.deepcopy(grammar)
    grammar_prime.add_production(
        '{0} -> {0} {1}'.format(Production.H_SYM, Production.I_SYM))
    grammar_prime.add_production(
        '{0} -> {1}'.format(Production.H_SYM, Production.I_SYM))
    for char in grammar.chars:
        grammar_prime.add_production(
            '{0} ->1 {1}'.format(Production.I_SYM, char)).set_inserted()
    for lhs, terminals_lhs in grammar.terminals.items():
        for rhs in terminals_lhs:
            grammar_prime.try_add(
                '{0} -> {1} {2}'.format(
                    lhs, lhs, Production.H_SYM))
            grammar_prime.try_add(
                '{0} -> {1} {2}'.format(
                    lhs, Production.H_SYM, lhs))
            if grammar_prime.try_add(
                    '{0} ->{1} {2}'.format(lhs, 1, Production.EPSILON)):
                grammar_prime.productions[lhs][Production.EPSILON].set_deleted(
                    rhs)
            for char in [x for x in grammar.chars if x is not rhs]:
                if grammar_prime.try_add(
                        '{0} ->{1} {2}'.format(lhs, 1, char)):
                    grammar_prime.productions[lhs][char].set_replaced(rhs)
    return grammar_prime


def eliminate_epsilon_productions(grammar):
    add_all_nullable(grammar)
    print(grammar)
    return grammar


def add_all_nullable(grammar):
    epsi = Production.EPSILON
    more = True
    while more:
        more = False
        for lhs, nonterminals_lhs in grammar.nonterminals.items():
            for rhs in nonterminals_lhs:
                if len(rhs.split()) == 1:
                    continue
                sym_b, sym_c = rhs.split()
                if sym_b not in grammar.terminals or\
                        sym_c not in grammar.terminals:
                    continue
                if epsi in grammar.terminals[sym_b] and\
                        epsi in grammar.terminals[sym_c]:
                    errors = grammar.terminals[sym_b][epsi].errors +\
                        grammar.terminals[sym_c][epsi].errors
                    if grammar.try_add('{0} ->{1} {2}'.format(
                            lhs, errors, epsi)):
                        grammar.productions[lhs][epsi].set_deleted(
                            grammar.productions[sym_b][epsi].deleted() +
                            grammar.productions[sym_c][epsi].deleted()
                        )
                        more = True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('grammar_file',
                        type=argparse.FileType('r'),
                        help="grammar file of rule to use")
    args = parser.parse_args()

    grammar = Grammar()
    for line in args.grammar_file:
        grammar.add_production(line)
    grammar_prime = construct_covering(grammar)
    grammar_prime = eliminate_epsilon_productions(grammar_prime)

if __name__ == '__main__':
    main()
