from dataclasses import dataclass, field
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor


@dataclass
class CFGGrammar:
    rules: list

@dataclass
class CFGRule:
    lhs: 'CFGNonterminal'
    rhs: list
    rid: int

@dataclass
class CFGNonterminal:
    name: str

@dataclass
class CFGTerminal:
    val: str

grammar = Grammar(
    r"""
    grammar     = (ws* rule ws* ";")* ws*
    rule        = nt ws* "=" (ws* (t / nt))*
    nt          = ~r"[a-zA-Z][a-zA-Z0-9_]*"
    t           = ~r'"(\\"|[^"])*"'
    ws          = ~"\s*"
    """
)

class CFGGrammarVisitor(NodeVisitor):
    def visit_grammar(self, node, visited_children):
        rules = []
        for i, c in enumerate(visited_children[0]):
            c[1].rid = i
            rules.append(c[1])
        return CFGGrammar(rules=rules)
    def visit_rule(self, node, visited_children):
        lhs = visited_children[0]
        rhs = []
        for c in visited_children[3]:
            rhs.append(c[1])
        return CFGRule(lhs=lhs, rhs=rhs, rid=0)
    def visit_nt(self, node, visited_children):
        return CFGNonterminal(name=node.text)
    def visit_t(self, node, visited_children):
        return CFGTerminal(val=bytes(node.text[1:-1], "utf-8").decode("unicode_escape"))
    def generic_visit(self, node, visited_children):
        return visited_children or node

def parse_cfg(in_file):
    visitor = CFGGrammarVisitor()
    with open(in_file) as reader:
        contents = reader.read()
        print(contents)
        tree = grammar.parse(contents)
        return visitor.visit(tree)

if __name__ == "__main__":
       print(parse_cfg("project/parson/grammar"))