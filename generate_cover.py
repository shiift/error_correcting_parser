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


class Grammar(object):
    """Grammar conatins a list of productions, a list of terminals, a list of
    non-terminals, and the top level symbol character ('S' by default)
    """
    def __init__(self):
        self.productions = {}
        self.terminals = {}
        self.nonterminals = {}
        self.chars = {}
        self.nullable = {}

    def add_production(self, string):
        new_production = Production(string)
        self.add_to_productions(new_production.lhs, new_production)

    def add_to_productions(self, symbol, new_production):
        self.add_to(self.productions, symbol, new_production)
        if new_production.is_T():
            self.add_to(self.terminals, symbol, new_production)
            if new_production.rhs == Production.EPSILON:
                self.nullable[symbol] = 1
            else:
                self.chars[new_production.rhs] = True
        else:
            self.add_to(self.nonterminals, symbol, new_production)

    def add_to(self, group, symbol, new_production):
        if symbol not in group:
            group[symbol] = []
        group[symbol].append(new_production)

    def insert_if_better(self, string):
        newp = Production(string)
        if newp.lhs not in self.productions:
            self.add_production(string)
            return
        productions = self.productions[newp.lhs]
        for i, production in enumerate(productions):
            if newp.rhs == production.rhs:
                if newp.errors < production.errors:
                    productions.pop(i)
                    break
                else:
                    return
        if newp.is_T():
            if newp.lhs in self.terminals:
                terminals = self.terminals[newp.lhs]
                for i, terminal in enumerate(terminals):
                    if newp.rhs == terminal.rhs and\
                            newp.errors < terminal.errors:
                        terminals.pop(i)
                        break
        else:
            if newp.lhs in self.nonterminals:
                nonterminals = self.nonterminals[newp.lhs]
                for i, nonterminal in enumerate(nonterminals):
                    nonterminal = nonterminals[i]
                    if newp.rhs == nonterminal.rhs and\
                            newp.errors < nonterminal.errors:
                        nonterminals.pop(i)
                        break
        self.add_production(string)

    def remove_epsilons(self):
        for symbol in self.productions:
            prods = self.productions[symbol]
            prods[:] = [x for x in prods if x.rhs != Production.EPSILON]
            if not prods:
                self.productions.pop(symbol)
        for symbol in self.terminals:
            terms = self.terminals[symbol]
            terms[:] = [x for x in terms if x.rhs != Production.EPSILON]
            if not terms:
                self.terminals.pop(symbol)

    def get_unit_productions(self):
        unit_list = []
        for symbol in self.nonterminals:
            for nonterminal in self.nonterminals[symbol]:
                if nonterminal.is_Unit():
                    unit_list.append(nonterminal)
        return unit_list

    def to_str_formatted(self):
        string = "nonterminals:\n"
        for nonterminal in self.nonterminals:
            string += "\t{0} => {1}\n".format(
                nonterminal,
                self.nonterminals[nonterminal])
        string += "terminals:\n"
        for terminal in self.terminals:
            string += "\t{0} => {1}\n".format(
                terminal,
                self.terminals[terminal])
        string += "chars: {0}\n".format(self.chars.keys())
        string += "nullable: {0}".format(self.nullable)
        return string

    def __repr__(self):
        string = ""
        for symbol in self.productions:
            for production in self.productions[symbol]:
                string += str(production) + "\n"
        return string[:-1]


def generate_cover(grammar):
    grammar_prime = Grammar()
    grammar_prime = copy.deepcopy(grammar)
    grammar_prime.add_production('{0} -> {0} {1}'
                                 .format(Production.H_SYM, Production.I_SYM))
    grammar_prime.add_production('{0} -> {1}'
                                 .format(Production.H_SYM, Production.I_SYM))
    for char in grammar.chars:
        grammar_prime.add_production('{0} ->1 {1}'
                                     .format(Production.I_SYM, char))
    for symbol, terminals in grammar.terminals.items():
        chars = grammar.chars.copy()
        for production in terminals:
            for char in chars:
                if production.rhs == char:
                    chars[char] = False
        for char in chars:
            if chars[char]:
                grammar_prime.add_production('{0} ->1 {1}'
                                             .format(symbol, char))
        grammar_prime.add_production('{0} ->1 {1}'
                                     .format(symbol, Production.EPSILON))
        grammar_prime.add_production('{0} ->0 {0} {1}'
                                     .format(symbol, Production.H_SYM))
        grammar_prime.add_production('{0} ->0 {1} {0}'
                                     .format(symbol, Production.H_SYM))
    # Elimination of __e productions
    for symbol in grammar_prime.productions:
        set_nullable(grammar_prime, symbol)
    for symbol in grammar_prime.nonterminals:
        add_nullable_productions(grammar_prime, symbol)
    grammar_prime.remove_epsilons()
    # Elimination of unit productions
    unit_productions = grammar_prime.get_unit_productions()
    for production in unit_productions:
        add_transition_productions(grammar_prime,
                                   unit_productions,
                                   production.lhs,
                                   production.rhs,
                                   production.errors)
    remove_unit_productions(grammar_prime)
    print(grammar_prime)
    return grammar_prime


def remove_unit_productions(grammar):
    for symbol in grammar.productions:
        prod_locations = []
        productions = grammar.productions[symbol]
        for i, production in enumerate(productions):
            if production.is_Unit() and production.is_NT():
                prod_locations.insert(0, i)
        for i in prod_locations:
            productions.pop(i)
    for symbol in grammar.nonterminals:
        nt_locations = []
        nonterminals = grammar.nonterminals[symbol]
        for i, nonterminal in enumerate(nonterminals):
            if nonterminal.is_Unit():
                nt_locations.insert(0, i)
        for i in nt_locations:
            nonterminals.pop(i)


def add_transition_productions(grammar, unit_productions, symbol_top,
                               symbol_current, errors):
    if symbol_current in grammar.productions:
        for production in grammar.productions[symbol_current]:
            # if not production.is_Unit:
            grammar.insert_if_better(
                '{} ->{} {}'.format(
                    symbol_top,
                    errors+production.errors,
                    production.rhs))
    for unit_production in unit_productions:
        if unit_production.lhs == symbol_current:
            new_unit_productions = [u for u in unit_productions
                                    if u != unit_production]
            add_transition_productions(
                grammar,
                new_unit_productions,
                symbol_top,
                unit_production.rhs,
                errors+unit_production.errors)


def add_nullable_productions(grammar, symbol):
    productions = grammar.nonterminals[symbol]
    for production in productions:
        if len(production.rhs.split()) == 2:
            rhs_b, rhs_c = production.rhs.split()
            if rhs_b in grammar.nullable:
                grammar.insert_if_better('{} ->{} {}'.format(
                    symbol,
                    production.errors+grammar.nullable[rhs_b],
                    rhs_c))
            if rhs_c in grammar.nullable:
                grammar.insert_if_better('{} ->{} {}'.format(
                    symbol,
                    production.errors+grammar.nullable[rhs_c],
                    rhs_b))


def set_nullable(grammar, symbol):
    if symbol not in grammar.productions:
        return False
    for production in grammar.productions[symbol]:
        if not production.marked:
            production.marked = True
            if len(production.rhs.split()) == 2:
                rhs_b, rhs_c = production.rhs.split()
                if rhs_b == symbol or rhs_c == symbol:
                    production.marked = False
                    continue
                if (rhs_b not in grammar.nullable and
                        not set_nullable(grammar, rhs_b)):
                    production.marked = False
                    return False
                if (rhs_c not in grammar.nullable and
                        not set_nullable(grammar, rhs_c)):
                    production.marked = False
                    return False
                sum_null = grammar.nullable[rhs_b] + grammar.nullable[rhs_c]
                if (symbol not in grammar.nullable or
                        sum_null < grammar.nullable[symbol]):
                    grammar.nullable[symbol] = sum_null
                    production.marked = False
                    return True
            else:
                rhs_b = production.rhs
                if (rhs_b not in grammar.nullable and
                        not set_nullable(grammar, rhs_b)):
                    production.marked = False
                    return False
                if (symbol not in grammar.nullable or
                        grammar.nullable[rhs_b] < grammar.nullable[symbol]):
                    grammar.nullable[symbol] = grammar.nullable[rhs_b]
                    production.marked = False
                    return True
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('grammar_file',
                        type=argparse.FileType('r'),
                        help="grammar file of rule to use")
    args = parser.parse_args()

    grammar = Grammar()
    for line in args.grammar_file:
        grammar.add_production(line)
    generate_cover(grammar)

if __name__ == '__main__':
    main()
