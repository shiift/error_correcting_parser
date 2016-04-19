import argparse

from classes import Node, Grammar, Lookup, Matrix, BreakIt


def error_correcting_parser(grammar, input_string):  # pylint: disable=R0914
    """Takes a grammar and an input string and returns a tuple of the closest
    string in the grammar for that input string and the distance of the input
    string to the grammar (number of errors).
    """
    input_size = len(input_string)
    list_x = Lookup(grammar.productions, input_size)
    cky_matrix = Matrix(input_size)
    for i in range(1, input_size + 1):
        input_char = input_string[i-1:i]
        for A, productions in grammar.terminals.items():
            if input_char in productions:
                errors = productions[input_char].errors
                cky_matrix.insert(A, i, i+1, errors, productions[input_char])
                list_x.insert(A, i, i+1, errors)
    for depth in range(2, input_size + 1):
        for lhs, rhs, production in grammar.get_all(grammar.nonterminals):
            l_3 = production.errors
            B, C = rhs.split()
            for i, k, l_1 in list_x.get_all(B, depth, input_size):
                j_offset = i + depth
                cky_cell = cky_matrix.get(k, j_offset)
                if C in cky_cell:
                    l_total = l_1 + cky_cell[C][1] + l_3
                    cky_matrix.insert(lhs, i, j_offset, l_total, production)
                    list_x.insert(lhs, i, j_offset, l_total)
    least_err = None
    for (_, k, errors) in list_x.get(Grammar.TOP_SYMBOL, 1).values():
        if (k == input_size + 1) and (not least_err or errors < least_err):
            least_err = errors
    if least_err is None:
        raise LookupError('Correction not found. Incomplete input grammar.')
    tree = parse_tree(cky_matrix, Grammar.TOP_SYMBOL, 1, input_size + 1,
                      least_err, grammar.nonterminals)
    return least_err, tree


def parse_tree(cky_matrix, current_symbol, i, j, errors, nonterminals):
    """Takes a Matrix, a symbol, a start location, an end location, the best
    error distance for the string, and a list of nonterminals and returns a
    parse tree for the individual characters in the string. This can be used
    to find I'.
    """
    if i == j - 1:
        tups = cky_matrix.get(i, j)
        if current_symbol in tups:
            tup = tups[current_symbol]
            if tup[1] == errors:
                return Node(i, j, tup[2])
        raise LookupError('Could not find {} in cky_matrix at {}'.format(
            current_symbol, (i, j)))
    A, B, q_1, q_2, dab, k = [None] * 6
    try:
        for k in range(i+1, j):
            for rhs, dab in nonterminals[current_symbol].items():
                A, B = rhs.split()
                if A in cky_matrix.get(i, k) and B in cky_matrix.get(k, j):
                    q_1 = cky_matrix.get(i, k)[A][1]
                    q_2 = cky_matrix.get(k, j)[B][1]
                    if dab.errors + q_1 + q_2 == errors:
                        raise BreakIt
        raise LookupError((
            'Could not find match for right hand side of any '
            'production of {} in cyk_matrix at {}').format(
                current_symbol, (i, j)))
    except BreakIt:
        pass
    left = parse_tree(cky_matrix, A, i, k, q_1, nonterminals)
    right = parse_tree(cky_matrix, B, k, j, q_2, nonterminals)
    root = Node(i, j, dab)
    root.left = left
    root.right = right
    return root


def correct_string(node):
    production = node.production
    if production.is_T():
        if production.inserted:
            res = ""
        elif production.replaced != "":
            res = production.replaced
        else:
            res = production.rhs
    else:
        res = correct_string(node.left) + correct_string(node.right)
    return production.prefix + res + production.suffix


def run_parser(grammar, input_string):
    """Takes a grammar and an input string and runs the parser. This function
    prints out the Input string, the closest string in the grammar (I') and
    the number of errors between them
    """
    errors, tree = error_correcting_parser(grammar, input_string)
    corrected_string = correct_string(tree)
    print("I : %s" % input_string)
    print("I': %s" % corrected_string)
    print("E : %d" % errors)


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
