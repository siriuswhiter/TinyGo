from util.lexer import *
from util.error import ParserError, ErrorCode

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        
        self.curToken = self.lexer.getToken()
        self.peekToken = self.lexer.getToken()
    
    def checkToken(self, kind):
        return kind == self.curToken.kind
    
    def checkPeek(self, kind):
        return kind == self.peekToken.kind
    
    def match(self,kind):
        if not self.checkToken(kind):
            self.abort(ErrorCode.UNEXPECTED_TOKEN,"Expected %s, but found %s" % (kind.name, self.curToken.kind.name))
        self.nextToken()
            
    
    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()
    
    def abort(self, error_code, msg):
        s = "%s:%d:%d - %s" % (self.lexer.fname, self.curToken.line,self.curToken.col, msg)
        # print(s)
        raise ParserError(error_code=error_code.value, message= s)
       
    def newline(self):
        self.match(TokenType.NEWLINE)
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken() 
        
    def isCmpOp(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ) 
        
    def parse(self):
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
        

        self.match(TokenType.PACKAGE)
        pname = self.curToken
        self.match(TokenType.IDENT)
        self.newline()
        
        root = Block()
        while not self.checkToken(TokenType.EOF):
            out = self.declaration()
            if isinstance(out, FuncBlock):
                root.new_function(out)
            elif isinstance(out, VarDecl):
                root.new_vardecl(out)
            self.newline()
        
        return Program(pname, root)
    
    #  "ident" type {"," "ident" type}
    #  a int | a int, b int | a,b int | empty
    def params(self):
        param_list = []
        if not self.checkToken(TokenType.RPAREN):
            idents = [self.curToken.text]
            self.nextToken()
            while self.checkToken(TokenType.COMMA):
                self.nextToken()
                idents.append(self.curToken.text)
                self.nextToken()
            if self.isIdentType():
                for ident in idents:
                    param_list.append(VarDecl(ident, self.curToken.text))
                self.nextToken()
            else:
                self.abort(ErrorCode.UNEXPECTED_TOKEN,"Expected type , but found %s" % self.curToken.text)
            
            if self.checkToken(TokenType.COMMA):
                self.nextToken()
                param_list.extend(self.params())
            elif not self.checkToken(TokenType.RPAREN):
                self.abort(ErrorCode.UNEXPECTED_TOKEN,"Expected ')' or ident , but found %s" % self.curToken.text)

        return param_list
         
    # type | "(" type (, type)* ")"   
    def retTypes(self):
        if self.isIdentType():
            type_ = self.curToken.text
            self.nextToken()
            return type_
        
        # types = []
        # if not self.checkToken(TokenType.LPAREN):
        #     if self.isIdentType():
        #         types.append(self.curToken.text)
        #         self.nextToken()
        #         return types
        #     else:
        #         self.abort(ErrorCode.UNEXPECTED_TOKEN, "Expected type , but found %s" % self.curToken.text)
        # else:
        #     self.nextToken() # (
                
        #     if not self.checkToken(TokenType.RPAREN):
        #         if self.isIdentType():
        #             types.append(self.curToken.text)
        #             self.nextToken()
        #         else:
        #             self.abort(ErrorCode.UNEXPECTED_TOKEN, "Expected type , but found %s" % self.curToken.text)
        #         while self.checkToken(TokenType.COMMA):
        #             self.nextToken()
        #             if self.isIdentType():
        #                 types.append(self.curToken.text)
        #                 self.nextToken()
        #             else:
        #                 self.abort(ErrorCode.UNEXPECTED_TOKEN, "Expected type , but found %s" % self.curToken.text)
        #         self.match(TokenType.RPAREN)
            
        #     else:
        #         self.abort(ErrorCode.UNEXPECTED_TOKEN, "Expected type , but found %s" % self.curToken.text)
        
        # return types
        
    
    def declaration(self):
        statement = None
        
        # "FUNC" ident "(" formal_param_list ")"  "{" {statement} "}"
        if self.checkToken(TokenType.FUNC):
            self.nextToken()
            fname = self.curToken.text
            self.match(TokenType.IDENT)
            self.match(TokenType.LPAREN)
            
            # parameters 
            params = self.params()
            self.match(TokenType.RPAREN)
        
            #  return type
            rettypes = None
            if not self.checkToken(TokenType.LBRACE):
                rettypes = self.retTypes()
                
            self.match(TokenType.LBRACE)
            self.newline()
            
            
            statementlist = StatesList()
            while not self.checkToken(TokenType.RBRACE):
                statementlist.append(self.statement())
            
            self.match(TokenType.RBRACE)
            statement = FuncBlock(fname,params, rettypes, statementlist)
            
        # "VAR" ident identType
        elif self.checkToken(TokenType.VAR):
            self.nextToken()
            ident = self.curToken.text
            self.match(TokenType.IDENT)
            if self.isIdentType():
                identType = self.curToken
                self.nextToken()
                statement = VarDecl(ident, identType)
            else:
                self.abort(ErrorCode.SYNTAX_ERROR,"Only allowed variable declare outside function.")
        
        # self.newline()
        return statement
            
        
    def statement(self):
        # print("Statement : %s" % self.curToken.kind.name)
        
        statement = self.declaration()
        
        # func / var 
        if statement:
            pass

        # "IF" condition "{" {statement} "}"
        elif self.checkToken(TokenType.IF):
            self.nextToken()
            condition = self.condition()
            
            self.match(TokenType.LBRACE)
            self.newline()
            
            statements = StatesList()
            while not self.checkToken(TokenType.RBRACE):
                statements.append(self.statement())
            
            self.match(TokenType.RBRACE)
            statement = IfStatement(condition, statements)
        
        # "FOR" condition "{" {statement} "}"
        elif self.checkToken(TokenType.FOR):
            self.nextToken()
            condition = self.condition()
            
            self.match(TokenType.LBRACE)
            self.newline()
            
            statements = StatesList()
            while not self.checkToken(TokenType.RBRACE):
                statements.append(self.statement())
            
            self.match(TokenType.RBRACE)
            statement = ForStatement(condition, statements)
            
        # "GOTO" ident
        elif self.checkToken(TokenType.GOTO):
            self.nextToken()
            ident = self.curToken
            self.match(TokenType.IDENT)
        
            statement = GotoDecl(ident)
          
        # "LABEL" ident
        elif self.checkToken(TokenType.LABEL):
            self.nextToken()
            ident = self.curToken
            self.match(TokenType.IDENT)
            statement = LabelDecl(ident)
            
        # "RETURN" expression
        elif self.checkToken(TokenType.RETURN):
            self.nextToken()
            # retVals = []
            # if not self.checkToken(TokenType.NEWLINE):
            #     retVals.append(self.expression())
            #     while self.checkToken(TokenType.COMMA):
            #         self.nextToken()
            #         retVals.append(self.expression())
            
            statement = RetDecl(self.expression())
            
        # ident "=" expression  | ident()
        elif self.checkToken(TokenType.IDENT):
            if self.checkPeek(TokenType.EQ):
                ident = self.curToken.text
                self.nextToken()
                self.nextToken()
                statement = AssignOp(ident, self.expression())
            elif self.checkPeek(TokenType.LPAREN):
                statement = self.funcCall()
        
        else:
            self.abort(ErrorCode.SYNTAX_ERROR,"Invalid statement  %s at (%s)" % ( self.curToken.text, self.curToken.kind.name))
        
        self.newline()
        return statement
         
    def funcCall(self):
        ident = self.curToken.text
        self.nextToken()
        statement = None
        if self.checkToken(TokenType.LPAREN):
            self.nextToken()
            args = []
            if not self.checkToken(TokenType.RPAREN):
                args.append(self.expression())
                while self.checkToken(TokenType.COMMA):
                    self.nextToken()
                    args.append(self.expression())
            self.match(TokenType.RPAREN)
            statement = FuncCall(ident, args)
        return statement
        
    def isValidNumber(self):
        return self.checkToken(TokenType.INT_NUM) or self.checkToken(TokenType.FLOAT_NUM)
        
    def isIdentType(self):
        return self.checkToken(TokenType.INT) or self.checkToken(TokenType.FLOAT)
    
    # condition ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)
    def condition(self):
        left = self.expression()
        if self.isCmpOp():
            op = self.curToken
            self.nextToken()
            right = self.expression()
        else:
            self.abort(ErrorCode.UNEXPECTED_TOKEN,"Expected condition operator at : %s " % self.curToken.text)
        
        return ConditionOp(left,op, right)        
        # while self.isCmpOp():
        #     self.nextToken()
        #     self.expression()
    
    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        # print("Expression")
        node = self.term()
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            preToken = self.curToken
            self.nextToken()
            
            node = BinOp(left=node, op=preToken, right = self.term())
        
        return node
    
    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        # print("Term")
        node = self.unary()
        while self.checkToken(TokenType.MULTI) or self.checkToken(TokenType.DIVID):
            preToken = self.curToken
            self.nextToken()
            node = BinOp(left=node, op=preToken, right = self.unary())
        return node
    
    # unary ::= ["+" | "-"] primary
    def unary(self):
        # print("Unary")
        op = TokenType.PLUS
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            op = self.curToken
            self.nextToken()
        return UnaryOp(op, self.primary())
    
    # primary ::= number | ident "(" (expression)* ")" | "(" expression ")"
    def primary(self):
        preToken = self.curToken.text
        if self.checkToken(TokenType.INT_NUM):
            self.nextToken()
            return Num(int(preToken), "int")
        elif self.checkToken(TokenType.FLOAT_NUM):
            self.nextToken()
            return Num(float(preToken), "float")
        elif self.checkToken(TokenType.IDENT):
            self.nextToken()
            if not self.checkToken(TokenType.LPAREN):
                return Ident(preToken)
            else:
                # function call
                self.nextToken()
                args = []
                while not self.checkToken(TokenType.RPAREN):
                    args.append(self.expression())
                self.match(TokenType.RPAREN)
                return FuncCall(preToken, args)
        elif self.checkToken(TokenType.LPAREN):
            self.nextToken()
            node = None
            while not self.checkToken(TokenType.RPAREN):
                node = self.expression()
            self.match(TokenType.RPAREN)
            if node!=None:
                return node
            self.abort(ErrorCode.SYNTAX_ERROR,"The Left and Right PARENTS are NOT allowed to put together.")
        else:
            self.abort(ErrorCode.UNEXPECTED_TOKEN,"Unexpected token at %s" % self.curToken.text)
            

class AST:
    pass

class Program(AST):
    def __init__(self, package, block):
        self.package = package
        self.block = block
        
class Block(AST):
    def __init__(self):
        self.vardecls = []
        self.functions = []
    
    def new_vardecl(self, var):
        self.vardecls.append(var)
    
    def new_function(self, func):
        self.functions.append(func)
    
    
class FuncBlock(AST):
    def __init__(self,name, params, rettypes ,statementlist):
        self.name = name
        self.params = params
        self.rettypes = rettypes
        self.statementlist = statementlist
  
class FuncCall(AST):
    def __init__(self, name, args=[]):
        self.name = name
        self.args = args
        
        self.func_sym = None # point to func_declaration
      
class VarDecl(AST):
    def __init__(self, ident, type):
        self.ident = ident
        self.type = type
        
class IfStatement(AST):
    def __init__(self, condition, statesList):
        self.cond = condition
        self.states = statesList
    
class ForStatement(AST):
    def __init__(self, condition, statesList):
        self.cond = condition
        self.states = statesList
    
class AssignOp(AST):
    def __init__(self,ident,expression):
        self.left = ident
        self.right = expression
        
class StatesList(AST):
    def __init__(self):
        self.states = []

    def append(self, state):
        self.states.append(state)
        
class LabelDecl(AST):
    def __init__(self, ident):
        self.ident = ident
        
class GotoDecl(AST):
    def __init__(self,ident):
        self.ident = ident
  
class RetDecl(AST):
    def __init__(self, retvals):
        self.val = retvals
      
class ConditionOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right
    
class UnaryOp(AST):
    def __init__(self, op, right):
        self.token = self.op = op
        self.right = right

    
class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Ident(AST):
    def __init__(self, text):
        self.text = text
        
class Num(AST):
    def __init__(self, value, type):
        self.value = value
        self.type = type        


