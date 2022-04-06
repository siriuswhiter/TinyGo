from collections import OrderedDict
from enum import Enum
from util.error import SemanticError, ErrorCode

class NodeVisitor:
    def visit(self, node):
        method = "visit_" + type(node).__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception("[Semantic error] : No visit_%s method" % type(node).__name__)
    
class SemanticAnalyzer(NodeVisitor):
    def __init__(self):
        self._init_scope()
    
    def analyze(self, tree):
        self.visit(tree)
        
    def _init_scope(self):
        self.cur_level = 0
        self.cur_scope = ScopedSymbolTable("builtin", self.cur_level)
        self.cur_scope.set(BuiltinTypeSymbol("int"))
        self.cur_scope.set(BuiltinTypeSymbol("float"))
 
    def log(self, msg):
        PRINT_SCOPE = False
        if PRINT_SCOPE:
            print(msg)
        
        
    def abort(self, error_code, msg):
        # s = "%s:%d:%d - %s" % (self.parser.lexer.fname, self.parser.lexer.curLine,self.parser.lexer.curCol, msg)
        
        raise SemanticError(
            error_code=error_code.value,
            message= msg
        )
        
    def visit_Program(self, node):
        self.log("Enter Program")
        self.cur_level += 1
        scope = ScopedSymbolTable("global", self.cur_level, self.cur_scope)
        self.cur_scope = scope
        
        self.visit(node.block)
        
        self.log("Exit Program")
        self.log(scope)
        self.cur_scope = self.cur_scope.enclosing_scope
        self.cur_level -= 1 
        self.log(self.cur_scope)
        
    
    def visit_Block(self, node):
        for var in node.vardecls:
            self.visit(var)
        for func in node.functions:
            self.visit(func)
        
    
    def visit_VarDecl(self, node):
        name = node.ident       
        if self.cur_scope.get(name, True):
            self.abort(ErrorCode.DUPLICATE_ID," Duplicate identifier '%s' found" % name)
        val = self.cur_scope.get(node.type.text)
        self.cur_scope.set(VarSymbol(name, val))
    
    def visit_FuncBlock(self, node):
        func_name = node.name
        self.log("Enter Scope %s" % func_name)
        func_sym = FuncSymbol(func_name, node.params,node.rettypes)
        self.cur_scope.set(func_sym)
        
        self.cur_level += 1
        scope = ScopedSymbolTable(func_name, self.cur_level, self.cur_scope)
        self.cur_scope = scope
        
        
        # parameter
        for param in node.params:
            vartype = self.cur_scope.get(param.type)
            self.cur_scope.set(VarSymbol(param.ident, vartype))      
        
        # func block
        self.visit(node.statementlist)
        
        self.log(self.cur_scope)
        
        self.cur_level -= 1
        self.cur_scope = self.cur_scope.enclosing_scope        
        self.log("Leave Scope %s" % func_name)
        
        # set block for interpreter
        func_sym.statementlist = node.statementlist
        

    def visit_FuncCall(self, node):
        # params count check
        
        for arg in node.args:
            self.visit(arg)
            
        node.func_sym = self.cur_scope.get(node.name)
        
        
        
    def visit_StatesList(self, node):
        for state in node.states:
            self.visit(state)
        
    def visit_IfStatement(self, node):
        self.visit(node.states)
        
    def visit_ForStatement(self, node):
        self.visit(node.states)
        
    def visit_LabelDecl(self, node):
        pass
    
    def visit_GotoDecl(self, node):
        pass
    
    def visit_RetDecl(self, node): 
        self.visit(node.val)
    
        # have_cnts =  len(node.val)
        # expected_cnts = len(self.cur_scope.enclosing_scope.get(self.cur_scope.scope_name).rettypes)
        # if  have_cnts != expected_cnts:
        #     self.abort(ErrorCode.MISMATCH_ERROR, "Expected return %d values, but found %d values."% (expected_cnts, have_cnts) )
        
    
    def visit_AssignOp(self, node):
        name = node.left
        value = self.visit(node.right)
        
    def visit_UnaryOp(self, node):
        self.visit(node.right)
    
    
    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
            
            
    def visit_Ident(self, node):
        name = node.text
        
        sym = self.cur_scope.get(name)
        if sym is None:
            self.abort(ErrorCode.ID_NOT_FOUND,"NameError : Undefined variable: '%s'" % name)
        
    def visit_Num(self, node):
        return node.value
    
  
class Symbol(object):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type
        # self.category = category
    
class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super().__init__(name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{class_name}(name='{name}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
        )
    
class VarSymbol(Symbol):
    
    def __init__(self, name, type):
        super().__init__(name, type)

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
        )

    __repr__ = __str__
    
class FuncSymbol(Symbol):
    def __init__(self, name, params=[], rettypes=[]):
        super(FuncSymbol, self).__init__(name)
        self.params = params
        self.rettypes = rettypes
        self.statementlist = None
        
    def __str__(self):
        return '<{class_name}(name={name}, parameters={params}, rettypes={rettypes})>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            params=self.params,
            rettypes=self.rettypes
        )

    __repr__ = __str__
        
# str: Symbol  
class ScopedSymbolTable(object):
    
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self._symbols = OrderedDict()
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope
        
        
    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        for header_name, header_value in (
            ('Scope name', self.scope_name),
            ('Scope level', self.scope_level),
            ('Enclosing scope',
             self.enclosing_scope.scope_name if self.enclosing_scope else None
            )
        ):
            lines.append('%-15s: %s' % (header_name, header_value))
        h2 = 'Scope (Scoped symbol table) contents'
        lines.extend([h2, '-' * len(h2)])
        lines.extend(
            ('%7s: %r' % (key, value))
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        s = '\n'.join(lines)
        return s
    
    __repr__ = __str__
    
    def set(self, symbol):
        self._symbols[symbol.name] = symbol
        
    def get(self, name, cur_scope_only = False):
        symbol = self._symbols.get(name)
        if symbol != None or cur_scope_only:
            return symbol
        
        if self.enclosing_scope != None:
            return self.enclosing_scope.get(name) 
   