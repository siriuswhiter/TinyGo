from enum import Enum

class ErrorCode(Enum):
    ILLEGAL_CHAR = "Illegal character"
    UNEXPECTED_TOKEN = "Unexpcted token"
    ID_NOT_FOUND = "Identifier not found"
    DUPLICATE_ID = "Duplicate identifier found"
    SYNTAX_ERROR = "Syntax error"
    MISMATCH_ERROR = "Mismatching parameter"
    
class Error(Exception):
    def __init__(self, error_code=None,  message=None):
        # super().__init__(self)
        self.error_code = error_code
        self.message = message
        
    def __str__(self):
        return self.error_code + " : "+ self.message
    
class LexerError(Error):
    pass

class ParserError(Error):
    pass

class SemanticError(Error):
    pass

class InterpretError(Error):
    pass