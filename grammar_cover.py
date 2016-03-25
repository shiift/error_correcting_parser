import argparse
from classes import *

def generate_cover(g):
    gp = Grammar()
    gp.import_productions(g)
    gp.add_production('{0} -> {0} {1}'.format(Production.H, Production.I))
    gp.add_production('{0} -> {1}'.format(Production.H, Production.I))
    for c in g.chars:
        gp.add_production('{0} ->1 {1}'.format(Production.I, c))
    done = {}
    for t in g.terminals:
        if t in done:
            continue
        done[t] = True
        for c in gp.chars:
            if (t.rhs != c):
                gp.add_production('{0} ->1 {1}'.format(t.lhs, c))    
        gp.add_production('{0} ->1 {1}'.format(t.lhs, Production.epsilon))
        gp.add_production('{0} ->0 {0} {1}'.format(t.lhs, Production.H))
        gp.add_production('{0} ->0 {1} {0}'.format(t.lhs, Production.H))
    # Elimination of __e productions
    for p in gp.productions:
        set_nullable(gp, p.lhs)
    gp.remove_epsilons()
    print gp

def set_nullable(gp, B):
    for p in gp.get_productions(B):
        if len(p.rhs.split()) == 2:
            C, D = p.rhs.split()
            if C == B or D == B:
                continue
            if not C in gp.nullable and not set_nullable(gp, C):
                return False
            if not D in gp.nullable and not set_nullable(gp, D):
                return False
            sum_null = gp.nullable[C] + gp.nullable[D]
            if not B in gp.nullable or sum_null < gp.nullable[B]:
                gp.nullable[B] = sum_null
                return True
        else:
            C = p.rhs
            if not C in gp.nullable and not set_nullable(gp, C):
                return False        
            if not B in gp.nullable or gp.nullable[C] < gp.nullable[B]:
                gp.nullable[B] = gp.nullable[C]
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
