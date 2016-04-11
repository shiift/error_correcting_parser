import argparse
from classes import Production, Node, Grammar, Lookup, Matrix


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
    for i in range(1, input_size + 1):
        for production in grammar.terminals:
            if production.rhs == input_string[i:i+1]:
                A = production.lhs
                errors = production.errors
                cyk_matrix.insert(i, i+1, (A, errors))
                list_x.insert(A, (i, i+1, errors))
    for s_var in range(2, input_size + 1):  # pylint: disable=R0101
        for production in grammar.nonterminals:
            A = production.lhs
            l_3 = production.errors
            B, C = production.rhs.split()
            for i, k, l_1 in list_x.get_all(B):
                if (k < i + s_var) and (i + s_var <= input_size + 1):
                    cyk_cell = cyk_matrix.get(k, i+s_var)
                    if C in cyk_cell:
                        _, l_2 = cyk_cell[C]
                        l_total = l_1 + l_2 + l_3
                        cyk_matrix.insert(i, i+s_var, (A, l_total))
                        list_x.insert(A, (i, i+s_var, l_total))
    best = None
    for (_, k, errors) in list_x.get(grammar.S, 1):
        if (k == input_size + 1) and (not best or errors < best):
            best = errors
    tree = None
    #tree = parse_tree(cyk_matrix, grammar.S, 1, input_size+1, best,
    #                  input_string, grammar.nonterminals)
    return (best, tree)


def parse_tree(cyk_matrix, current_symbol, i, j, errors,
               input_string, nonterminals):
    """Takes a Matrix, a symbol, a start location, an end location, the best
    error distance for the string, and a list of nonterminals and returns a
    parse tree for the individual characters in the string. This can be used
    to find I'.
    """
    if i == j - 1:
        for prod_symbol, prod_count in cyk_matrix.get(i, j):
            if prod_symbol == current_symbol and prod_count == errors:
                return Node(i, j, Production(
                    current_symbol, errors, input_string[i]))
        raise ValueError('Could not find Matching {} in cyk_matrix at {}'
                         .format(current_symbol, (i, j)))
    A, B, q_1, q_2, dab, k = [None] * 6
    try:
        for k in range(i+1, j):
            for A, q_1 in cyk_matrix.get(i, k):
                for B, q_2 in cyk_matrix.get(k, j):
                    for dab in nonterminals:
                        if (dab.lhs == current_symbol and
                                dab.rhs.split()[0] == A and
                                dab.rhs.split()[1] == B and
                                dab.errors + q_1 + q_2 == errors):
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


def flatten_tree(tree, terminals, accumulator):
    """This takes a parse tree, a list of terminals and an empty string, and
    returns a string for the closest string in the list of terminals for the
    tree.
    """
    if tree is None:
        return ""
    if tree.left is None and tree.right is None:
        return find_correction(tree.production, terminals)
    left_string = flatten_tree(tree.left, terminals, accumulator)
    accumulator += left_string +\
        flatten_tree(tree.right, terminals, accumulator)
    return accumulator


def find_correction(production, terminals):
    """Takes a production and a list of terminals and returns the right hand
    side of the production if has 0 errors, otherwise returns the rhs of a
    terminal that matches the lhs of the production with 0 errors.
    """
    if production.errors == 0:
        return production.rhs
    for terminal in terminals:
        if terminal.lhs == production.lhs and terminal.errors == 0:
            return terminal.rhs
    return '-'
    # TODO: Finish Error Correction
    # raise ValueError(('Could not find an in-language symbol to map: {0}\n'
    #                   'Is the grammar have a mapping from the lhs to a'
    #                   'character with 0 errors?').format(production))


def run_parser(grammar, input_string):
    """Takes a grammar and an input string and runs the parser. This function
    prints out the Input string, the closest string in the grammar (I') and
    the number of errors between them
    """
    e, tree = error_correcting_parser(grammar, input_string)
    #flatten_string = flatten_tree(tree, grammar.terminals, "")
    print("I : " + input_string)
    #print("I': " + flatten_string)
    #print("I\": " + flatten_string.replace('-', ''))
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
