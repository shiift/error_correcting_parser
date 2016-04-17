import argparse
import copy
from classes import Node, Grammar, Lookup, Matrix


class BreakIt(Exception):
    pass


def error_correcting_parser(grammar, input_string):  # pylint: disable=R0914
    """Takes a grammar and an input string and returns a tuple of the closest
    string in the grammar for that input string and the distance of the input
    string to the grammar (number of errors).
    """
    input_size = len(input_string)
    input_string = " " + input_string
    list_x = Lookup(grammar.productions, input_size)
    cyk_matrix = Matrix(input_size)
    input_boundry = input_size + 1
    for i in range(1, input_boundry):
        for A, productions in grammar.terminals.items():
            if input_string[i:i+1] in productions:
                errors = productions[input_string[i:i+1]].errors
                cyk_matrix.insert(A, i, i+1, errors,
                                  productions[input_string[i:i+1]])
                list_x.insert(A, i, i+1, errors)
    for s_var in range(2, input_boundry):
        for A, productions in grammar.nonterminals.items():
            for rhs, production in productions.items():
                l_3 = production.errors
                B, C = rhs.split()
                for i, k, l_1 in list_x.get_all(B, s_var, input_boundry):
                    is_boundry = i + s_var
                    cyk_cell = cyk_matrix.get(k, is_boundry)
                    if C in cyk_cell:
                        l_total = l_1 + cyk_cell[C][1] + l_3
                        new_production = copy.deepcopy(production)
                        new_production.errors = l_total
                        cyk_matrix.insert(
                            A, i, is_boundry, l_total, new_production)
                        list_x.insert(A, i, is_boundry, l_total)
    best = None
    for (_, k, errors) in list_x.get(Grammar.TOP_SYMBOL, 1).values():
        if (k == input_boundry) and (not best or errors < best):
            best = errors
    if best is None:
        raise ValueError('Could not find a correction. Bad input grammar.')
    tree = parse_tree(cyk_matrix, Grammar.TOP_SYMBOL, 1, input_boundry, best,
                      input_string, grammar.nonterminals)
    return (best, tree)


def parse_tree(cyk_matrix, current_symbol, i, j, errors,
               input_string, nonterminals):
    """Takes a Matrix, a symbol, a start location, an end location, the best
    error distance for the string, and a list of nonterminals and returns a
    parse tree for the individual characters in the string. This can be used
    to find I'.
    """
    if i == j - 1:
        tup = cyk_matrix.get(i, j)
        if current_symbol in tup:
            if tup[current_symbol][1] == errors:
                return Node(i, j, tup[current_symbol][2])
        raise ValueError('Could not find Matching {} in cyk_matrix at {}'
                         .format(current_symbol, (i, j)))
    A, B, q_1, q_2, dab, k = [None] * 6
    try:
        for k in range(i+1, j):
            for rhs, dab in nonterminals[current_symbol].items():
                A, B = rhs.split()
                if A in cyk_matrix.get(i, k) and B in cyk_matrix.get(k, j):
                    q_1 = cyk_matrix.get(i, k)[A][1]
                    q_2 = cyk_matrix.get(k, j)[B][1]
                    if dab.errors + q_1 + q_2 == errors:
                        raise BreakIt
        raise ValueError('Could not match in Deep Loop in parse_tree')
    except BreakIt:
        pass
    left = parse_tree(cyk_matrix, A, i, k, q_1, input_string, nonterminals)
    right = parse_tree(cyk_matrix, B, k, j, q_2, input_string, nonterminals)
    root = Node(i, j, dab)
    root.left = left
    root.right = right
    return root


def correct_string(node):
    res = ""
    production = node.production
    if production.is_T():
        if production.inserted():
            res = ""
        elif production.replaced() != "":
            res = production.replaced()
        else:
            res = production.rhs
    elif production.is_NT():
        res = correct_string(node.left) + correct_string(node.right)
    res = production.prefix() + res + production.suffix()
    return res


def run_parser(grammar, input_string):
    """Takes a grammar and an input string and runs the parser. This function
    prints out the Input string, the closest string in the grammar (I') and
    the number of errors between them
    """
    e, tree = error_correcting_parser(grammar, input_string)
    corrected_string = correct_string(tree)
    print(tree)
    print("I : " + input_string)
    print("I': " + corrected_string)
    print("E : " + str(e))


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', '--string', help="string to test")
    group.add_argument('-i', '--infile',
                       type=argparse.FileType('r'),
                       help="file of strings to be tested")
    parser.add_argument('-g', '--grammar_file', default='grammar.txt',
                        type=argparse.FileType('r'),
                        help="grammar file of rule to use")
    args = parser.parse_args()

    grammar = Grammar()
    for line in args.grammar_file:
        grammar.add_production(line)
    if args.string:
        run_parser(grammar, args.string)
    if args.infile:
        for line in args.infile:
            run_parser(grammar, line.strip())

if __name__ == '__main__':
    main()
