import sys
from errorclasses import *

"""Takes a grammar and an input string and returns a tuple of the closest string
in the grammar for that input string and the distance of the input string to the
grammar (number of errors).
"""
def error_correcting_parser(g, input_string):
    n = len(input_string)
    lookup = Lookup(g.productions, n)

def main(argv):
    try:
        if (len(argv) == 0):
            grammar_file = open('grammar.txt')
            input_string = "tactagcaatacgcttgcgttcggtggttaagtatgtataatgcgcgggcttgtcgt"
        elif (len(argv) == 1):
            grammar_file = open('grammar.txt')
            input_string = argv[0]
        elif (len(argv) == 2):
            input_string = argv[0]
            grammar_file = open(argv[1])
    except:
        print "Must use format: python errorparser.py <input_string>\
        <grammar_file>"

    g = Grammar()
    for line in grammar_file:
        g.add_production(line)
    error_correcting_parser(g, input_string)

if __name__ == '__main__':
    main(sys.argv[1:])
