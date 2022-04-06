import sys
# sys.path.append("../")

from util.lexer import *
from util.parser import *
from util.semantic_analyzer import *
from util.interpreter import *


def main():
    if len(sys.argv)<2:
        exit("Usage: python3 tinygo.py  filename.go")
        
    filename = sys.argv[1]
    
    with open(filename, "r") as f:
        input = "".join(f.readlines())+"\n"
        
        try:
            print("[Phase 1] Lexing...")
            lexer = Lexer(filename, input)
            print("[Phase 2] Parsing...")
            parser = Parser(lexer)
            tree = parser.parse()
            print("[Phase 3] Semantic Checking...")        
            s = SemanticAnalyzer()
            s.analyze(tree)
            print("[Phase 4] Interpreting...")        
            interpreter = Interpreter(tree)
            interpreter.interpret()
        
        except (LexerError,ParserError,SemanticError, InterpretError)as e:
            print(e.message)
            exit(1)
        
        print("Interpret completed.")
            
if __name__ == '__main__':
    main()