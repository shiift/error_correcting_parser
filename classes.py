import re

class Production:
    def __init__(self, string):
        p = re.compile("->[0-9]+")
        m = p.search(string)
        print m.groups()

Production("S ->0 A B")
