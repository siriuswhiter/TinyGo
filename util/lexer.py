from util.error import LexerError,ErrorCode

class Lexer:
    def __init__(self, fname, input):
        self.fname = fname
        self.source = input
        self.curChar = ""
        self.curPos = -1
        self.curLine = 1
        self.curCol = 1
        self.nextChar()
            
    def nextChar(self):
        self.curPos += 1
        self.curCol += 1
        if self.curPos >= len(self.source):
            self.curChar = "\0"
        else:
            self.curChar = self.source[self.curPos]
    
    def peek(self):
        if self.curPos + 1 >= len(self.source):
            return "\0"
        return self.source[self.curPos+1]
    
    def abort(self, error_code=None, msg=None):        
        s = "%s:%d:%d - %s" % (self.fname, self.curLine,self.curCol, msg)
        raise LexerError(error_code= error_code.value,message=s)
    
    def skipWhitespace(self):
        while self.curChar==" " or self.curChar=="\r" or self.curChar=="\t":
            self.nextChar()
    
    def skipComment(self):
        if self.curChar == "/" and self.peek() == "/":
            while self.curChar != "\n":
                self.nextChar()
    
    
    def getToken(self):
        self.skipWhitespace()
        self.skipComment()
        
        token = None
        
        # try:
        #     token_type = TokenType(self.curChar)
        # except ValueError:
        #     self.abort()
        # else:
        #     token = Token(token_type.text, token_type, self.curLine, self.curCol)
            
        # operator
        if self.curChar == "+":
            token = Token(self.curChar, TokenType.PLUS,self.curLine, self.curCol)
        elif self.curChar == "-":
            token = Token(self.curChar, TokenType.MINUS,self.curLine, self.curCol)
        elif self.curChar == "*":
            token = Token(self.curChar, TokenType.MULTI,self.curLine, self.curCol)
        elif self.curChar == "/":
            token = Token(self.curChar, TokenType.DIVID,self.curLine, self.curCol)
        elif self.curChar == "(":
            token = Token(self.curChar, TokenType.LPAREN,self.curLine, self.curCol)
        elif self.curChar == ")":
            token = Token(self.curChar, TokenType.RPAREN,self.curLine, self.curCol)
        elif self.curChar == "{":
            token = Token(self.curChar, TokenType.LBRACE,self.curLine, self.curCol)
        elif self.curChar == "}":
            token = Token(self.curChar, TokenType.RBRACE,self.curLine, self.curCol)   
        elif self.curChar == ",":
            token = Token(self.curChar, TokenType.COMMA,self.curLine, self.curCol)  
                        
        # special character
        elif self.curChar == "\n":
            token = Token(self.curChar, TokenType.NEWLINE,self.curLine, self.curCol)
            self.curLine += 1
            self.curCol = -1
            
        elif self.curChar == "\0":
            token = Token(self.curChar, TokenType.EOF,self.curLine, self.curCol)
            
        # cmp instruction
        elif self.curChar == "=":
            if self.peek() == "=":
                prev = self.curChar
                self.nextChar()
                token = Token(prev+self.curChar, TokenType.EQEQ,self.curLine, self.curCol)
            else:
                token = Token(self.curChar, TokenType.EQ,self.curLine, self.curCol)
        elif self.curChar == "!" and self.peek() == "=":
            prev = self.curChar
            self.nextChar()
            token = Token(prev+self.curChar, TokenType.NOTEQ,self.curLine, self.curCol)
        elif self.curChar == ">":
            if self.peek() == "=":
                prev = self.curChar
                self.nextChar()
                token = Token(prev+self.curChar, TokenType.GTEQ,self.curLine, self.curCol)
            else:
                token = Token(self.curChar, TokenType.GT,self.curLine, self.curCol)
        elif self.curChar == "<":
            if self.peek() == "=":
                prev = self.curChar
                self.nextChar()
                token = Token(prev+self.curChar, TokenType.LTEQ,self.curLine, self.curCol)
            else:
                token = Token(self.curChar, TokenType.LT,self.curLine, self.curCol)
        
        # string
        elif self.curChar == "\"":
            self.nextChar()
            startPos = self.curPos
            
            while self.curChar != "\"":
                if self.curChar == "\r" or self.curChar=="\n" or self.curChar=="\t" or self.curChar=="\\" or self.curChar=="%":
                    self.abort(ErrorCode.ILLEGAL_CHAR,"Illegal character in string : %s" % self.curChar)
                self.nextChar()
            token = Token(self.source[startPos :self.curPos], TokenType.STRING,self.curLine, self.curCol)
            
        # number
        elif self.curChar.isdigit():
            startPos = self.curPos
            
            while self.peek().isdigit():
                self.nextChar()
            
            if self.peek() == ".":
                self.nextChar()
                
                if not self.peek().isdigit():
                    self.abort(ErrorCode.ILLEGAL_CHAR,"Illegal character in number : %s" % self.curChar)
                while self.peek().isdigit():
                    self.nextChar()
                token = Token(self.source[startPos :self.curPos+1], TokenType.FLOAT_NUM,self.curLine, self.curCol)
            else:
                token = Token(self.source[startPos :self.curPos+1], TokenType.INT_NUM,self.curLine, self.curCol)
            
        elif self.curChar.isalpha():
            startPos = self.curPos
            while self.peek().isalnum():
                self.nextChar()
            
            tokText = self.source[startPos :self.curPos+1]
            keyword = Token.isKeyword(tokText)
            token = Token(tokText, keyword,self.curLine, self.curCol)
                
            
        else:
            self.abort(ErrorCode.ILLEGAL_CHAR,"Unknown token: %s" % self.curChar)
        
        self.nextChar()
        return token
    

class Token:
    def __init__(self, tokenText, tokenKind, line=None, col=None):
        self.text = tokenText
        self.kind = tokenKind
        
        self.line = line
        self.col = col
       
    def __str__(self):
        return 'Token({type}, {value}, position={lineno}:{column})'.format(
            type=self.kind,
            value=repr(self.text),
            lineno=self.line,
            column=self.col,
        )
    
    __repr__  = __str__

    @staticmethod
    def isKeyword(tokenText):
        for kind in TokenType:
            if kind.name.lower() == tokenText and kind.value > TokenType.RESERVED_KEYWORD_START.value and kind.value< TokenType.RESERVED_KEYWORD_END.value:
                return kind
        return TokenType.IDENT

import enum
class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    INT_NUM = 10
    FLOAT_NUM = 11
    # Keywords.
    RESERVED_KEYWORD_START = 100
    PACKAGE = 101
    LABEL = 102
    GOTO = 103
    VAR = 105
    IF = 106
    FOR = 109
    FUNC = 112
    RETURN = 113
    INT = 120
    FLOAT = 121
    RESERVED_KEYWORD_END = 200
    # Operators.
    EQ = 201  
    PLUS = 202
    MINUS = 203
    MULTI = 204
    DIVID = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211
    # 
    LPAREN = 212 # (
    RPAREN = 213 # )
    LBRACE = 214 # {
    RBRACE = 215 # }   
    COMMA = 216 # ,
    