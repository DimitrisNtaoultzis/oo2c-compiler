from antlr4 import FileStream, CommonTokenStream
from oosLexer import oosLexer
from oosParser import oosParser
from symbol_collector import SymbolCollector
from codegen import CodeGenVisitor

import sys

input_stream = FileStream(sys.argv[1], encoding="utf-8")
lexer = oosLexer(input_stream)
tokens = CommonTokenStream(lexer)
parser = oosParser(tokens)
tree = parser.startRule()

collector = SymbolCollector()
classes = collector.visit(tree)

codegen = CodeGenVisitor(classes)
c_code = codegen.generate()
print(c_code)

if __name__  == "__main__":
    pass
