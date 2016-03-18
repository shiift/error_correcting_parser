import sys
import re

class Production:
    regex = r'->[0-9]+'
    def __init__(self, arg0, arg1=None, arg2=None):
        if arg1 == None:
            self.set_str(arg0)
        else:
            self.set_vars(arg0, arg1, arg2)
    def set_str(self, string):
        m = re.search(self.regex, string)
        if(m):
            self.errors = int(re.sub(r'->', '', m.group(0)))
        else:
            raise ValueError("Productions must be in the form: S ->0 A B")
        lhs_rhs = re.split(self.regex, string)
        self.lhs = lhs_rhs[0].strip()
        self.rhs = lhs_rhs[1].strip()
    def set_vars(self, lhs, errors, rhs):
        self.lhs = lhs
        self.errors = errors
        self.rhs = rhs
        return self
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
        for production in productions:
            lhs = production.lhs
            self.data[lhs] = []
            for i in range(0, size):
                self.data[lhs].append([])
    def insert(self, lhs, tup):
        self.get(lhs, tup[0]).append(tup)
    def get(self, lhs, i):
        return self.data[lhs][i-1]
    def get_all(self, lhs):
        newlist = []
        for l in self.data[lhs]:
            newlist.extend(l)
        return newlist
    def __repr__(self):
        return str(self.data.keys());

class Matrix:
    def __init__(self, size):
        self.data = [None] * size
        for i in range(0, size):
            self.data[i] = [[] for _dummy in xrange(size-i)]
    def insert(self, i, j, tup):
        self.get(i,j).append(tup)
    def get(self, i, j):
        return self.data[i-1][j-i-1]
    def __repr__(self):
        s = ""
        for i in self.data:
            s += str(i) + ",\n"
        return s

class Node:
    def __init__(self, i, j, p):
        self.i = i
        self.j = j
        self.p = p
    def left(self, left):
        self.left = left
    def right(self, right):
        self.right = right

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
            for (i, k, l1) in X.get_all(B):
                if (k <= n) and (i + s <= n + 1):
                    for (Cp, l2) in M.get(k, i+s):
                        if (Cp == C):
                            l = l1 + l2 + l3
                            M.insert(i, i+s, (A,l))
                            X.insert(A, (i,i+s,l))
    best = None
    for (j, k, l) in X.get('S', 1):
        if (k == n + 1) and (not best or l < best):
            best = l
    print best
    return parse_tree(M, 'S', 1, n, best, input_string, g.nonterminals)

def parse_tree(M, D, i, j, l, a, NT):
    if i == j - 1:
        for (Dc, lc) in M.get(i, j):
            if Dc == D and lc == l:
                return Node(i, j, Production(D, l, a[i]))
        raise ValueError('Could not find Matching ' + str(D) +\
            ' in M at (' + str(i) + ',' + str(j) + ')')
    A, B, q1, q2, dab, k = [None] * 6
    for k in range(i+1, j):
        for A, q1 in M.get(i, k):
            for B, q2 in M.get(k, j):
                for dab in NT:
                    if dab.lhs == D and\
                        dab.rhs.split()[0] == A and\
                        dab.rhs.split()[1] == B and\
                        dab.errors + q1 + q2 == l:
                        break;
    T1 = parse_tree(M, A, i, k, q1, a, NT)
    T2 = parse_tree(M, B, k, j, q2, a, NT)
    r = Node(i, j, dab)
    r.left(T1)
    r.right(T2)
    return r

def main(argv):
    global strings
    DEBUG = 0
    try:
        if (len(argv) == 0):
            grammar_file = open('grammar.txt')
            DEBUG = 1
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

    if DEBUG:
        for string in strings:
            print error_correcting_parser(g, string)
    else:
        print error_correcting_parser(g, input_string)


strings = ["tactagcaatacgcttgcgttcggtggttaagtatgtataatgcgcgggcttgtcgt",
"tgctatcctgacagttgtcacgctgattggtgtcgttacaatctaacgcatcgccaa",
"gtactagagaactagtgcattagcttatttttttgttatcatgctaaccacccggcg",
"aattgtgatgtgtatcgaagtgtgttgcggagtagatgttagaatactaacaaactc",
"tcgataattaactattgacgaaaagctgaaaaccactagaatgcgcctccgtggtag",
"aggggcaaggaggatggaaagaggttgccgtataaagaaactagagtccgtttaggt",
"cagggggtggaggatttaagccatctcctgatgacgcatagtcagcccatcatgaat",
"tttctacaaaacacttgatactgtatgagcatacagtataattgcttcaacagaaca",
"cgacttaatatactgcgacaggacgtccgttctgtgtaaatcgcaatgaaatggttt",
"ttttaaatttcctcttgtcaggccggaataactccctataatgcgccaccactgaca",
"gcaaaaataaatgcttgactctgtagcgggaaggcgtattatgcacaccccgcgccg",
"cctgaaattcagggttgactctgaaagaggaaagcgtaatatacgccacctcgcgac",
"gatcaaaaaaatacttgtgcaaaaaattgggatccctataatgcgcctccgttgaga",
"ctgcaatttttctattgcggcctgcggagaactccctataatgcgcctccatcgaca",
"tttatatttttcgcttgtcaggccggaataactccctataatgcgccaccactgaca",
"aagcaaagaaatgcttgactctgtagcgggaaggcgtattatgcacaccgccgcgcc",
"atgcatttttccgcttgtcttcctgagccgactccctataatgcgcctccatcgaca",
"aaacaatttcagaatagacaaaaactctgagtgtaataatgtagcctcgtgtcttgc",
"tctcaacgtaacactttacagcggcgcgtcatttgatatgatgcgccccgcttcccg",
"gcaaataatcaatgtggacttttctgccgtgattatagacacttttgttacgcgttt",
"gacaccatcgaatggcgcaaaacctttcgcggtatggcatgatagcgcccggaagag",
"aaaaacgtcatcgcttgcattagaaaggtttctggccgaccttataaccattaatta",
"tctgaaatgagctgttgacaattaatcatcgaactagttaactagtacgcaagttca",
"accggaagaaaaccgtgacattttaacacgtttgttacaaggtaaaggcgacgccgc",
"aaattaaaattttattgacttaggtcactaaatactttaaccaatataggcatagcg",
"catcctcgcaccagtcgacgacggtttacgctttacgtatagtggcgacaatttttt",
"ttgtcataatcgacttgtaaaccaaattgaaaagatttaggtttacaagtctacacc",
"tccagtataatttgttggcataattaagtacgacgagtaaaattacatacctgcccg",
"acagttatccactattcctgtggataaccatgtgtattagagttagaaaacacgagg",
"tgtgcagtttatggttccaaaatcgccttttgctgtatatactcacagcataactgt",
"ctgttgttcagtttttgagttgtgtataacccctcattctgatcccagcttatacgg",
"attacaaaaagtgctttctgaactgaacaaaaaagagtaaagttagtcgcgtagggt",
"atgcgcaacgcggggtgacaagggcgcgcaaaccctctatactgcgcgccgaagctg",
"taaaaaactaacagttgtcagcctgtcccgcttataagatcatacgccgttatacgt",
"atgcaattttttagttgcatgaactcgcatgtctccatagaatgcgcgctacttgat",
"ccttgaaaaagaggttgacgctgcaaggctctatacgcataatgcgccccgcaacgc",
"tcgttgtatatttcttgacaccttttcggcatcgccctaaaattcggcgtcctcata",
"ccgtttattttttctacccatatccttgaagcggtgttataatgccgcgccctcgat",
"tgtaaactaatgcctttacgtgggcggtgattttgtctacaatcttacccccacgta",
"gatcgcacgatctgtatacttatttgagtaaattaacccacgatcccagccattctt",
"aacgcatacggtattttaccttcccagtcaagaaaacttatcttattcccacttttc",
"ttagcggatcctacctgacgctttttatcgcaactctctactgtttctccatacccg",
"gccttctccaaaacgtgttttttgttgttaattcggtgtagacttgtaaacctaaat",
"cagaaacgttttattcgaacatcgatctcgtcttgtgttagaattctaacatacggt",
"cactaatttattccatgtcacacttttcgcatctttgttatgctatggttatttcat",
"atataaaaaagttcttgctttctaacgtgaaagtggtttaggttaaaagacatcagt",
"caaggtagaatgctttgccttgtcggcctgattaatggcacgatagtcgcatcggat",
"ggccaaaaaatatcttgtactatttacaaaacctatggtaactctttaggcattcct",
"taggcaccccaggctttacactttatgcttccggctcgtatgttgtgtggaattgtg",
"ccatcaaaaaaatattctcaacataaaaaactttgtgtaatacttgtaacgctacat",
"tggggacgtcgttactgatccgcacgtttatgatatgctatcgtactctttagcgag",
"tcagaaatattatggtgatgaactgtttttttatccagtataatttgttggcataat"]

if __name__ == '__main__':
    main(sys.argv[1:])