import argparse
import classes
import copy

"""Production conatins a left hand side, right hand side and number of errors
for the production. Double underscore in front of the symbol is reserved and
__e can be used for epsilon transitions. Reserved: __H, __I"""
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
        p = Production(string);
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
    def __repr__(self):
        string = "nonterminals:\n"
        for nt in self.nonterminals:
            string += "\t{} => {}\n".format(nt, self.nonterminals[nt])
        string += "terminals:\n"
        for t in self.terminals:
            string += "\t{} => {}\n".format(t, self.terminals[t])
        string += "chars: {}\n".format(self.chars.keys())
        string += "nullable: {}".format(self.nullable)
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
    gp.remove_epsilons()
    print gp

def set_nullable(gp, A):
    if not A in gp.productions:
        return False
    for p in gp.productions[A]:
        if len(p.rhs.split()) == 2:
            C, D = p.rhs.split()
            if C == A or D == A:
                continue
            if not C in gp.nullable and not set_nullable(gp, C):
                return False
            if not D in gp.nullable and not set_nullable(gp, D):
                return False
            sum_null = gp.nullable[C] + gp.nullable[D]
            if not A in gp.nullable or sum_null < gp.nullable[A]:
                gp.nullable[A] = sum_null
                return True
        else:
            C = p.rhs
            if not C in gp.nullable and not set_nullable(gp, C):
                return False        
            if not A in gp.nullable or gp.nullable[C] < gp.nullable[A]:
                gp.nullable[A] = gp.nullable[C]
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
