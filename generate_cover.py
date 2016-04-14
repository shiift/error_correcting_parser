import argparse
import copy

import classes
from classes import Production


class Grammar(classes.Grammar):
    """Grammar conatins a list of productions, a list of terminals, a list of
    non-terminals, and the top level symbol character ('S' by default)
    """
    def __init__(self):
        classes.Grammar.__init__(self)
        self.chars = {}
        # Unlike terminals and nonterminals, nullables are not always
        # in productions.
        self.nullable = {}
        self.nonterminal_units = {}
        self.nonterminal_nonunits = {}

    def add_production(self, new_production):
        if isinstance(new_production, str):
            new_production = Production(new_production)
        self.__add_to(self.productions, new_production)
        if new_production.is_T():
            self.__add_to(self.terminals, new_production)
            if new_production.rhs == Production.EPSILON:
                self.add_nullable(new_production)
            else:
                self.chars[new_production.rhs] = True
        else:
            self.__add_to(self.nonterminals, new_production)
            if new_production.is_Unit():
                self.__add_to(self.nonterminal_units, new_production)
            else:
                self.__add_to(self.nonterminal_nonunits, new_production)
        return new_production

    def add_nullable(self, production):
        if isinstance(production, str):
            production = Production(production)
        self.nullable[production.lhs] = production
        return production

    def remove_production(self, production):
        self.productions[production.lhs].pop(production.rhs)
        if production.is_NT():
            self.nonterminals[production.lhs].pop(production.rhs)
            if production.is_Unit():
                self.nonterminal_units[production.lhs].pop(production.rhs)
            else:
                self.nonterminal_nonunits[production.lhs].pop(production.rhs)
        elif production.is_T():
            self.terminals[production.lhs].pop(production.rhs)
            if production.rhs == Production.EPSILON:
                self.nullable.pop(production.lhs)

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


def construct_covering(grammar):
    grammar_p = Grammar()
    grammar_p = copy.deepcopy(grammar)
    grammar_p.add_production(
        '{0} -> {0} {1}'.format(Production.H_SYM, Production.I_SYM))
    grammar_p.add_production(
        '{0} -> {1}'.format(Production.H_SYM, Production.I_SYM))
    for char in grammar.chars:
        grammar_p.add_production(
            Production(
                '{0} ->1 {1}'.format(Production.I_SYM, char)
            ).set_inserted()
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
                ).set_deleted(rhs)
            )
            for char in [x for x in grammar.chars if x is not rhs]:
                grammar_p.try_add(
                    Production(
                        '{0} ->{1} {2}'.format(lhs, 1, char)
                    ).set_replaced(rhs)
                )
    return grammar_p


def eliminate_epsilon_productions(grammar):
    for symbol in grammar.productions:
        add_nullable(grammar, symbol)
    convert_nullable(grammar)
    for production in list(grammar.nullable.values()):
        grammar.remove_production(production)
    grammar.nullable = None


def convert_nullable(grammar):
    for symbol, nonterminals in grammar.nonterminal_nonunits.items():
        for nonterminal in nonterminals.values():
            rhs_b, rhs_c = nonterminal.rhs.split()
            if rhs_b in grammar.nullable:
                grammar.try_add(Production(
                    '{} ->{} {}'.format(
                        symbol,
                        nonterminal.errors +
                        grammar.nullable[rhs_b].errors,
                        rhs_c)
                    ).set_prefix(grammar.nullable[rhs_b].deleted()))
            if rhs_c in grammar.nullable:
                grammar.try_add(Production(
                    '{} ->{} {}'.format(
                        symbol,
                        nonterminal.errors +
                        grammar.nullable[rhs_c].errors,
                        rhs_c)
                    ).set_suffix(grammar.nullable[rhs_c].deleted()))


def add_nullable(grammar, symbol):
    #TODO: Change this to use nonterminal_unit and nonterminal_nonunit
    if symbol in grammar.productions:
        for production in grammar.productions[symbol].values():
            if production.exclude:
                continue
            production.exclude = True
            if not production.is_Unit():
                rhs_b, rhs_c = production.rhs.split()
                if rhs_b == symbol or rhs_c == symbol:
                    continue
                if (rhs_b not in grammar.nullable and
                        not add_nullable(grammar, rhs_b)):
                    return False
                if (rhs_c not in grammar.nullable and
                        not add_nullable(grammar, rhs_c)):
                    return False
                sum_null = grammar.nullable[rhs_b].errors +\
                    grammar.nullable[rhs_c].errors
                if grammar.try_add(
                        Production(
                            '{0} ->{1} {2}'.format(
                                symbol, sum_null, Production.EPSILON)
                        ).set_deleted(
                            grammar.nullable[rhs_b].deleted() +
                            grammar.nullable[rhs_c].deleted()
                        )):
                    return True
            else:
                rhs_b = production.rhs
                if (rhs_b not in grammar.nullable and
                        not add_nullable(grammar, rhs_b)):
                    return False
                prod_rhs = grammar.nullable[rhs_b]
                if grammar.try_add(
                        Production(
                            '{0} ->{1} {2}'.format(
                                symbol, prod_rhs.errors, Production.EPSILON)
                        ).set_deleted(prod_rhs.deleted())):
                    return True
    return False


def eliminate_unit_productions(grammar):
    for lhs, production_hash in grammar.nonterminal_units.items():
        for rhs, production in production_hash:
            convert_units(
                grammar, grammar.nonterminal_units, lhs, rhs, production.errors
            )


def convert_units(grammar, nt_units, sym_top, sym_current, errors):
    # if sym_current in grammar.productions:
    #     for production in list(grammar.productions[sym_current].values()):
    #         grammar.try_add(
    #             '{} ->{} {}'.format(
    #                 sym_top,
    #                 errors + production.errors,
    #                 production.rhs))
    # if sym_current in nt_units:
    pass


def add_all_unit(grammar):
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('grammar_file',
                        type=argparse.FileType('r'),
                        help="grammar file of rule to use")
    args = parser.parse_args()

    grammar = Grammar()
    for line in args.grammar_file:
        grammar.add_production(line)
    grammar_p = construct_covering(grammar)
    eliminate_epsilon_productions(grammar_p)
    eliminate_unit_productions(grammar_p)
    print(grammar_p)

if __name__ == '__main__':
    main()
