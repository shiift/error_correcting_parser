import sys
import re

class Production:
    regex = r'->[0-9]+'
    def __init__(self, string):
        m = re.search(self.regex, string)
        if(m):
            self.errors = int(re.sub(r'->', '', m.group(0)))
        else:
            raise ValueError("Productions must be in the form: S ->0 A B")
        lhs_rhs = re.split(self.regex, string)
        self.lhs = lhs_rhs[0].strip()
        self.rhs = lhs_rhs[1].strip()
    def __repr__(self):
        return self.lhs + " ->" + str(self.errors) + " " + self.rhs

class Grammar:
    productions = []
    terminals = []
    nonterminals = []
    def add_production(self, string):
        p = Production(string)
        self.productions.append(p)
        if len(p.rhs.split()) == 1:
            self.terminals.append(p)
        else:
            self.nonterminals.append(p)
    def __repr__(self):
        string = ""
        for prod in self.productions:
            string += str(prod) + "\n"
        return string

class Lookup:
    data = {}
    def __init__(self, productions, size):
        self.size = size
        for production in productions:
            lhs = production.lhs
            self.data[lhs] = {}
            for i in range(1, size + 1):
                self.data[lhs][i] = None
    def get_all(self, lhs):
        newlist = []
        for i in range(1, self.size + 1):
            data = self.data[lhs][i]
            if data != None:
                newlist.append(data)
        return newlist
    def __repr__(self):
        return str(self.data.keys());

class Matrix:
    def __init__(self, size):
        self.data = [None] * (size + 1)
        for i in range(1, size + 1):
            self.data[i] = [[]] * (size + 2)
    def __repr__(self):
        return str(self.data)

"""Takes a grammar and an input string and returns a tuple of the closest string
in the grammar for that input string and the distance of the input string to the
grammar (number of errors).
"""
def error_correcting_parser(g, input_string):
    n = len(input_string)
    X = Lookup(g.productions, n)
    M = Matrix(n)
    for i in range(1, n + 1):
        for production in g.terminals:
            if production.rhs == input_string[i:i+1]:
                A = production.lhs
                l = production.errors
                M.data[i][i+1].append((A, l))
                X.data[A][i] = (i, i+1, l)
    for s in range(2, n + 1):
        for production in g.nonterminals:
            A = production.lhs
            l3 = production.errors
            B,C = production.rhs.split()
            for (i, k, l1) in X.get_all(B):
                if (i + s < n + 2) and (k < n + 1):
                    for (Cp, l2) in M.data[k][i+s]:
                        if (Cp == C):
                            l = l1 + l2 + l3
                            M.data[i][i+s].append((A,l))
                            X.data[A][i] = (i,i+s,l)
    for (j, k, l) in X.get_all('S'):
        if (j == 1) and (k == n + 1):
            print l

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
