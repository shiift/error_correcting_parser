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
    def add_production(self, string):
        self.productions.append(Production(string))
    def __repr__(self):
        string = ""
        for prod in self.productions:
            string += str(prod) + "\n"
        return string

class Lookup:
    data = {}
    def __init__(self, productions):
        for production in productions:
            data[production] = []
