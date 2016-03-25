import argparse
from classes import *

"""Takes a grammar and an input string and returns a tuple of the closest string
in the grammar for that input string and the distance of the input string to the
grammar (number of errors).
"""
def error_correcting_parser(g, input_string):
    n = len(input_string)
    input_string = " " + input_string
    X = Lookup(g.productions, n)
    M = Matrix(n)
    for i in range(1, n + 1):
        for production in g.terminals:
            if production.rhs == input_string[i:i+1]:
                A = production.lhs
                l = production.errors
                M.insert(i, i+1, (A, l))
                X.insert(A, (i, i+1, l))
    for s in range(2, n + 1):
        for production in g.nonterminals:
            A = production.lhs
            l3 = production.errors
            B,C = production.rhs.split()
            for i, k, l1 in X.get_all(B):
                if (k < i + s) and (i + s <= n + 1):
                    for Cp, l2 in M.get(k, i+s):
                        if (Cp == C):
                            l = l1 + l2 + l3
                            M.insert(i, i+s, (A,l))
                            X.insert(A, (i,i+s,l))
    best = None
    for (j, k, l) in X.get(g.S, 1):
        if (k == n + 1) and (not best or l < best):
            best = l
    tree = parse_tree(M, g.S, 1, n+1, best, input_string, g.nonterminals)
    return (best, tree)

"""Takes a Matrix, a symbol, a start location, an end location, the best error
distance for the string, and a list of nonterminals and returns a parse tree
for the individual characters in the string. This can be used to find I'.
"""
def parse_tree(M, D, i, j, l, a, NT):
    if i == j - 1:
        for (Dc, lc) in M.get(i, j):
            if Dc == D and lc == l:
                return Node(i, j, Production(D, l, a[i]))
        raise ValueError('Could not find Matching {} in M at {}'.format(D, (i,j)))
    A, B, q1, q2, dab, k = [None] * 6
    try:
        for k in range(i+1, j):
            for A, q1 in M.get(i, k):
                for B, q2 in M.get(k, j):
                    for dab in NT:
                        if (dab.lhs == D and
                            dab.rhs.split()[0] == A and
                            dab.rhs.split()[1] == B and
                            dab.errors + q1 + q2 == l):
                            raise BreakIt
        raise ValueError('Could not match in Deep Loop in parse_tree')
    except BreakIt: pass
    T1 = parse_tree(M, A, i, k, q1, a, NT)
    T2 = parse_tree(M, B, k, j, q2, a, NT)
    r = Node(i, j, dab)
    r.left = T1
    r.right = T2
    return r

"""This takes a parse tree, a list of terminals and an empty string, and returns
a string for the closest string in the list of terminals for the tree.
"""
def flatten_tree(tree, ts, s):
    if tree == None:
        return ""
    if tree.left == None and tree.right == None:
        return find_correction(tree.p, ts)
    c = flatten_tree(tree.left, ts, s)
    s += c + flatten_tree(tree.right, ts, s)
    return s

"""Takes a production and a list of terminals and returns the right hand side of
the production if has 0 errors, otherwise returns the rhs of a terminal that
matches the lhs of the production with 0 errors.
"""
def find_correction(p, ts):
    if p.errors == 0:
        return p.rhs
    for t in ts:
        if t.lhs == p.lhs and t.errors == 0:
            return t.rhs
    return "-"
    raise ValueError('Could not find an in-language symbol to map: ' + str(p) +
            '\nIs the grammar have a mapping from the lhs to a character with 0' +
            'errors?')

"""Takes a grammar and an input string and runs the parser. This function prints
out the Input string, the closest string in the grammar (I') and the number of
errors between them"""
def run_parser(g, input_string):
    e, tree = error_correcting_parser(g, input_string)
    flatten_string = flatten_tree(tree, g.terminals, "")
    print "I : " + input_string
    print "I': " + flatten_string
    print "I\": " + flatten_string.replace('-','')
    print "E : " + str(e)

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--string', help="string to test")
    group.add_argument('-i', '--infile',
        type=argparse.FileType('r'), help="file of strings to be tested")
    parser.add_argument('-g', '--grammar-file', default='grammar.txt',
        type=argparse.FileType('r'), help="grammar file of rule to use")
    args = parser.parse_args()

    g = Grammar()
    for line in args.grammar_file:
        g.add_production(line)
    if args.string:
        run_parser(g, args.string)
    if args.infile:
        for line in args.infile:
            run_parser(g, line.strip())

main()
