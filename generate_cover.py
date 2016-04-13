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
        self.exclude = False  # TODO: Delete

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

    def remove_production(self, production):
        self.productions[production.lhs].pop(production.rhs)
        if production.is_NT():
            self.nonterminals[production.lhs].pop(production.rhs)
        elif production.is_T():
            self.terminals[production.lhs].pop(production.rhs)

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


def eliminate_epsilon_productions(grammar):
    add_all_nullable(grammar)
    old_grammar = copy.deepcopy(grammar)
    for top_lhs in old_grammar.terminals:
        if Production.EPSILON not in old_grammar.terminals[top_lhs]:
            continue
        top_production = old_grammar.terminals[top_lhs][Production.EPSILON]
        for lhs in old_grammar.nonterminals:
            for nonterminal in old_grammar.nonterminals[lhs].values():
                if nonterminal.is_Unit():
                    continue
                rhs_l = nonterminal.rhs.split()[0]
                rhs_r = nonterminal.rhs.split()[1]
                if rhs_l == top_lhs:
                    grammar.try_add(
                        Production(
                            '{0} ->{1} {2}'.format(
                                lhs, top_production.errors, rhs_r
                            )
                        ).set_prefix(top_production.deleted())
                    )
                if rhs_r == top_lhs:
                    grammar.try_add(
                        Production(
                            '{0} ->{1} {2}'.format(
                                lhs, top_production.errors, rhs_l
                            )
                        ).set_prefix(top_production.deleted())
                    )
        grammar.remove_production(
            Production('{0} -> {1}'.format(top_lhs, Production.EPSILON))
        )


def add_all_nullable(grammar):
    old_grammar = copy.deepcopy(grammar)
    epsi = Production.EPSILON
    more = True
    while more:
        more = False
        for lhs in old_grammar.nonterminals:
            for rhs, production in old_grammar.nonterminals[lhs].items():
                if production.is_Unit():
                    continue
                sym_b, sym_c = rhs.split()
                if (sym_b not in old_grammar.terminals or
                        sym_c not in old_grammar.terminals or
                        epsi not in old_grammar.terminals[sym_b] or
                        epsi not in old_grammar.terminals[sym_c]):
                    continue
                b_production = old_grammar.terminals[sym_b][epsi]
                c_production = old_grammar.terminals[sym_c][epsi]
                if grammar.try_add(Production(
                        '{0} ->{1} {2}'.format(
                            lhs,
                            b_production.errors + c_production.errors,
                            epsi
                        )
                    ).set_type(
                        Production.DELETED,
                        b_production.deleted() + c_production.deleted(),
                        )):
                    more = True


def eliminate_unit_productions(grammar):
    add_all_unit(grammar)
    old_grammar = copy.deepcopy(grammar)
    for lhs in old_grammar.nonterminals:
        for mid, production_top in old_grammar.nonterminals[lhs].items():
            if not production_top.is_Unit():
                continue
            if mid in old_grammar.terminals:
                for rhs, production in old_grammar.terminals[mid].items():
                    grammar.try_add(Production(
                        '{0} ->{1} {2}'.format(
                            lhs,
                            production_top.errors + production.errors,
                            rhs
                        )
                    ).set_prefix(
                        production_top.prefix()
                    ).set_suffix(
                        production_top.suffix()
                    ).set_type(
                        Production.REPLACED, production.replaced()
                    ).set_type(
                        Production.INSERTED, production.inserted()
                    ))
            if mid in old_grammar.nonterminals:
                for rhs, production in old_grammar.nonterminals[mid].items():
                    if production.is_Unit():
                        continue
                    grammar.try_add(Production(
                        '{0} ->{1} {2}'.format(
                            lhs,
                            production_top.errors + production.errors,
                            rhs
                        )
                    ).set_prefix(
                        production_top.prefix() + production.prefix()
                    ).set_suffix(
                        production.suffix() + production_top.suffix()
                    ))
            grammar.remove_production(
                Production('{0} -> {1}'.format(lhs, mid))
            )


def add_all_unit(grammar):
    old_grammar = copy.deepcopy(grammar)
    more = True
    while more:
        more = False
        for lhs in old_grammar.nonterminals:
            for mid, production_top in old_grammar.nonterminals[lhs].items():
                if (not production_top.is_Unit() or
                        mid not in old_grammar.nonterminals):
                    continue
                for rhs, production in old_grammar.nonterminals[mid].items():
                    if grammar.try_add(Production(
                            '{0} ->{1} {2}'.format(
                                lhs,
                                production_top.errors + production.errors,
                                rhs
                            )
                        ).set_prefix(
                            production_top.prefix() + production.prefix()
                        ).set_suffix(
                            production_top.suffix() + production.suffix()
                            )):
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
    grammar_p = construct_covering(grammar)
    eliminate_epsilon_productions(grammar_p)
    eliminate_unit_productions(grammar_p)
    print(grammar_p)

if __name__ == '__main__':
    main()
