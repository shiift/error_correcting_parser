# Error Correcting Parser for Context Free Grammars

This project is a python implementation of an error correcting parser for context free grammars that runs in cubic time. The algorithm implemented is the same as the one described by Rajasekaran and Nicolae<sup>1</sup>.

## How It Works

The process consists of two stages:
- Generation of a covering grammar
- Performing the parsing algorithm on a string with the covering grammar

The covering grammar generates "error productions" that allow us to find the shortest distance between any given input string (with symbols in the language) and a string in the language. For example, if our language is a<sup>n</sup>b<sup>n</sup> then we can take any string containing any number of 'a's and 'b's and find the shortest distance to a number of 'a's followed by the same number of 'b's. Tagging information is also encoded with these productions that contains information for inserting, replacing and deleting these productions. This program takes in a file describing productions in [Chomsky Normal Form] in the following format (where S is the top level symbol):
```
S -> A B
A -> a
B -> b
```
Note that errors productions can be specified by putting it in the form: `B ->1 a`

The parsing algorithm does the heavy lifting and first determines the shortest distance between the string and a string in the language using a method described in the paper<sup>1</sup> using a [cky matrix]. From there a parse tree is constructed using the specified errors in the locations determined by the [cky matrix].

## Usage

Generate covering grammar and redirect the output to a file.
```sh
$ python3 generate_cover.py <input_grammar_file> > covering_grammar.txt
```

Use the covering grammar to test a string...
```sh
$ python3 error_parser.py -g covering_grammar.txt -s <input_string>
```
or test a file:
```sh
$ python3 error_parser.py -g covering_grammar.txt -i <input_string_file>
```

You can also view help by running:
```sh
$ python3 error_parser.py --help
```

### Example:

For the language a<sup>n</sup>b<sup>n</sup> we can make the following grammar:
```
S  -> A S B
S  -> A B
A  -> a
B  -> b
```
Which can be converted to [Chomsky Normal Form]:
```
S  -> A A1
S  -> A B
A1 -> S B
A  -> a
B  -> b
```
We can save this file as `grammar_anbn_raw.txt` and then generate the cover using `generate_cover.py`:
```sh
$ python3 generate_cover.py grammar_anbn_raw.txt > grammar_andbn_cover.txt
```
Then we can test a string using `error_parser.py`:
```
$ python3 error_parser.py -g grammar_andbn_cover.txt -s aaaaaab
I : aaaaaab
I': aaaabbbb
E : 3
```

[1] Sanguthevar Rajasekaran and Marius Nicolae. An error correcting parser for context free grammars
that takes less than cubic time. Manuscript, 2014.

[cky matrix]: https://en.wikipedia.org/wiki/CYK_algorithm
[Chomsky Normal Form]: https://en.wikipedia.org/wiki/Chomsky_normal_form
