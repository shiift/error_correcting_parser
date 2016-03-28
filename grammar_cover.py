import argparse
import classes
import copy

"""Production conatins a left hand side, right hand side and number of
errors for the production. Double underscore in front of the symbol is
reserved and __e can be used for epsilon transitions.
Reserved: __H, __I"""
class Production(classes.Production):
    H = '__H'
    I = '__I'
    epsilon = '__e'

"""Grammar conatins a list of productions, a list of terminals, a list of
non-terminals, and the top level symbol character ('S' by default)"""
class Grammar:
    S = 'S'
    def __init__(self):
        self.productions = {}
        self.terminals = {}
        self.nonterminals = {}
        self.chars = {}
        self.nullable = {}
    def add_production(self, string):
        p = Production(string)
        self.add_to_productions(p.lhs, p)
    def add_to_productions(self, A, p):
        self.add_to(self.productions, A, p)
        if p.is_T():
            self.add_to(self.terminals, A, p)
            if p.rhs == Production.epsilon:
                self.nullable[A] = 1
            else:
                self.chars[p.rhs] = True
        else:
            self.add_to(self.nonterminals, A, p)
    def add_to(self, group, A, p):
        if not A in group:
            group[A] = []
        group[A].append(p)
    def insert_if_better(self, string):
        newp = Production(string)
        if not newp.lhs in self.productions:
            self.add_production(string)
            return
        productions = self.productions[newp.lhs]
        for i in range(len(productions)):
            p = productions[i]
            if newp.rhs == p.rhs:
                if newp.errors < p.errors:
                    productions.pop(i)
                    break
                else:
                    return
        if newp.is_T():
            if newp.lhs in self.terminals:
                terminals = self.terminals[newp.lhs]
                for i in range(len(terminals)):
                    p = terminals[i]
                    if newp.rhs == p.rhs:
                        if newp.errors < p.errors:
                            terminals.pop(i)
                            break
                        else:
                            raise ValueError("Unmatching p/nt")
        else:
            if newp.lhs in self.nonterminals:
                nonterminals = self.nonterminals[newp.lhs]
                for i in range(len(nonterminals)):
                    p = nonterminals[i]
                    if newp.rhs == p.rhs:
                        if newp.errors < p.errors:
                            nonterminals.pop(i)
                            break
                        else:
                            raise ValueError("Unmatching p/nt")
        self.add_production(string)
    def remove_epsilons(self):
        for A in self.productions:
            prods = self.productions[A]
            prods[:] = [x for x in prods if x.rhs != Production.epsilon]
            if not prods:
                self.productions.pop(A)
        for A in self.terminals:
            terms = self.terminals[A]
            terms[:] = [x for x in terms if x.rhs != Production.epsilon]
            if not terms:
                self.terminals.pop(A)
    def get_unit_productions(self):
        l = []
        for A in self.nonterminals:
            nts = self.nonterminals[A]
            for nt in nts:
                if len(nt.rhs.split()) == 1:
                    l.append(nt)
        return l
    def to_str_formatted(self):
        string = "nonterminals:\n"
        for nt in self.nonterminals:
            string += "\t{} => {}\n".format(nt, self.nonterminals[nt])
        string += "terminals:\n"
        for t in self.terminals:
            string += "\t{} => {}\n".format(t, self.terminals[t])
        string += "chars: {}\n".format(self.chars.keys())
        string += "nullable: {}".format(self.nullable)
        return string
    def __repr__(self):
        string = ""
        for A in self.productions:
            for p in self.productions[A]:
                string += str(p) + "\n"
        return string

def generate_cover(g):
    gp = Grammar()
    gp = copy.deepcopy(g)
    gp.add_production('{0} -> {0} {1}'.format(Production.H, Production.I))
    gp.add_production('{0} -> {1}'.format(Production.H, Production.I))
    for c in g.chars:
        gp.add_production('{0} ->1 {1}'.format(Production.I, c))
    for A in g.terminals:
        terminals = g.terminals[A]
        chars = g.chars.copy()
        for production in terminals:
            for char in chars:
                if production.rhs == char:
                    chars[char] = False
        for char in chars:
            if chars[char]:
                gp.add_production('{0} ->1 {1}'.format(A, char))
        gp.add_production('{0} ->1 {1}'.format(A, Production.epsilon))
        gp.add_production('{0} ->0 {0} {1}'.format(A, Production.H))
        gp.add_production('{0} ->0 {1} {0}'.format(A, Production.H))
    # Elimination of __e productions
    for A in gp.productions:
        set_nullable(gp, A)
    for A in gp.nonterminals:
        add_nullable_productions(gp, A)
    gp.remove_epsilons()
    print gp.to_str_formatted()
    # # Elimination of unit productions
    # ups = gp.get_unit_productions()
    # for p in ups:
    #     add_transition_productions(gp, ups, p.lhs, p.lhs, p.errors)
    # remove_unit_productions(gp, ups)
    # return gp

def remove_unit_productions(gp, ups):
    for up in ups:
        if up.lhs in gp.productions:
            productions = gp.productions[up.lhs]
            for i in range(len(productions)):
                if productions[i].rhs == up.rhs:
                    productions.pop(i)
                    break
            nonterminals = gp.nonterminals[up.lhs]
            for i in range(len(nonterminals)):
                if nonterminals[i].rhs == up.rhs:
                    nonterminals.pop(i)
                    break

def add_transition_productions(gp, ups, A, C, errors):
    if C in gp.terminals:
        for t in gp.terminals[C]:
            gp.insert_if_better('{} ->{} {}'.format(A,
                errors + t.errors, t.rhs))
    for up in ups:
        if up.lhs == C:
            add_transition_productions(gp, ups, A, up.rhs,
                errors + up.errors)

def add_nullable_productions(gp, A):
    prods = gp.nonterminals[A]
    for p in prods:
        if len(p.rhs.split()) == 2:
            B, C = p.rhs.split()
            if B in gp.nullable and not C in gp.nullable:
                gp.insert_if_better('{} ->{} {}'.format(A,
                    p.errors + gp.nullable[B], C))
            elif not B in gp.nullable and C in gp.nullable:
                gp.insert_if_better('{} ->{} {}'.format(A,
                    p.errors + gp.nullable[C], B))

def set_nullable(gp, B):
    if not B in gp.productions:
        return False
    for p in gp.productions[B]:
        if not p.marked:
            p.marked = True
            if len(p.rhs.split()) == 2:
                C, D = p.rhs.split()
                if C == B or D == B:
                    p.marked = False
                    continue
                if not C in gp.nullable and not set_nullable(gp, C):
                    p.marked = False
                    return False
                if not D in gp.nullable and not set_nullable(gp, D):
                    p.marked = False
                    return False
                sum_null = gp.nullable[C] + gp.nullable[D]
                if not B in gp.nullable or sum_null < gp.nullable[B]:
                    gp.nullable[B] = sum_null
                    p.marked = False
                    return True
            else:
                C = p.rhs
                if not C in gp.nullable and not set_nullable(gp, C):
                    p.marked = False
                    return False        
                if not B in gp.nullable or gp.nullable[C] < gp.nullable[B]:
                    gp.nullable[B] = gp.nullable[C]
                    p.marked = False
                    return True
    return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--grammar-file', default='grammar_raw.txt',
        type=argparse.FileType('r'), help="grammar file of rule to use")
    args = parser.parse_args()

    g = Grammar()
    for line in args.grammar_file:
        g.add_production(line)
    generate_cover(g)

main()
