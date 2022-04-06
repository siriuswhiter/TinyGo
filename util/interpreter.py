from util.parser import *
from util.semantic_analyzer import *
from util.error import *

class ARType(Enum):
    PROGRAM = "Program"
    FUNCTION = "Function"
            
class ActivationRecord:
    def __init__(self, name, type, nested_level):
        self.name = name
        self.type = type
        self.nested_level = nested_level
        self.members = {}
        
    def __setitem__(self, k, v):
        self.members[k] = v 
    
    def __getitem__(self, k):
        return self.members[k] 
    
    def get(self, key):
        return self.members.get(key)
        
    def __str__(self):
        lines = [
            "{level}: {type} {name}".format(
                level = self.nested_level,
                type = self.type,
                name = self.name,
            )
        ]
        for name, val in self.members.items():
            lines.append(f'  {name}: {val}')

        return "\n".join(lines)
        
    def __repr__(self):
        return self.__str__()
    
class CallStack:
    def __init__(self):
        self._records = []

    def push(self, ar):
        self._records.append(ar)

    def pop(self):
        return self._records.pop()

    def peek(self):
        return self._records[-1]

    def __str__(self):
        s = '\n'.join(repr(ar) for ar in reversed(self._records))
        s = f'CALL STACK\n===============\n{s}\n'
        return s

    def __repr__(self):
        return self.__str__()
    
    
     
class Interpreter(NodeVisitor):
    def __init__(self, tree):
        self.tree = tree
        self.cur_level = 0
        self.callstack = CallStack()
        
    def interpret(self):
        self.visit(self.tree)
    
    def log(self, msg):
        print(msg)
 
    def abort(self, error_code, msg):
        print(self.callstack)
        raise InterpretError(
            error_code=error_code.value,
            message= msg
        )
        
    def visit_Program(self, node):
        self.cur_level += 1
        
        ar = ActivationRecord(
            name = node.package,
            type = ARType.PROGRAM,
            nested_level = self.cur_level
        )
        self.callstack.push(ar)
        
        self.visit(node.block)
        
        # print(self.callstack)
        self.callstack.pop()
        
    
    def visit_Block(self, node):
        global_func = {}
        for var in node.vardecls:
            self.visit(var)
        for func in node.functions:
            global_func[func.name] = func
        
        main = FuncCall("main")
        main.func_sym = global_func["main"]
        print(self.visit(main))
        # self.visit_FuncCall(global_func["main"])
        
    
    def visit_VarDecl(self, node):
        name = node.ident            
    
    # def visit_FuncBlock(self, node):     
    #     # # func block
    #     print("Enter Function %s" % node.name)
            
    #     self.visit(node.statementlist)
        
    #     print("Exit Function %s" % node.name)
   
        

    def visit_FuncCall(self, node):
        func_name = node.name
        
        self.cur_level += 1
        ar = ActivationRecord(
            name = func_name,
            type = ARType.FUNCTION,
            nested_level = self.cur_level,
        )
        
        func_sym = node.func_sym
        
        if func_sym==None:
            self.abort(ErrorCode.ID_NOT_FOUND, "Function %s can't found"%func_name)
            
        formal_params = func_sym.params 
        actual_params = node.args
    
        if formal_params!= [] and actual_params!=[]:
            for param_sym, arg in zip(formal_params, actual_params):
                ar[param_sym.ident] = self.visit(arg)
                
        self.callstack.push(ar) 
        
        ret = self.visit(func_sym.statementlist)
        
        # self.log(self.callstack)
        self.callstack.pop()
        
        return ret
        # if func_sym.rettypes != None and len(func_sym.rettypes) != 0:
        #     return ret
        
              
    def visit_StatesList(self, node):
        for state in node.states:
            last = self.visit(state)
            if last != None:
                return last
            
        
    def visit_IfStatement(self, node):
        if self.visit(node.cond):
            last = self.visit(node.states)
            if last != None:
                return last
        
    def visit_ForStatement(self, node):
        while self.visit(node.cond):
            last = self.visit(node.states)
            if last != None:
                return last
        
    def visit_ConditionOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op.text == "==":
            return left == right 
        elif node.op.text == "!=":
            return left != right 
        elif node.op.text == ">":
            return left > right 
        elif node.op.text == ">=":
            return left >= right 
        elif node.op.text == "<":
            return left < right 
        elif node.op.text == "<=":
            return left <= right 
        
    def visit_RetDecl(self, node): 
        return self.visit(node.val)
        
    
    def visit_AssignOp(self, node):
        name = node.left
        value = self.visit(node.right)
        
        ar = self.callstack.peek()
        ar[name] = value
        # self.log("%s = %s" % (name, value))
        
    def visit_UnaryOp(self, node):
        if node.op.name != "PLUS":
            return (-1)*self.visit(node.right)
        return self.visit(node.right)
    
    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op.text == "*":
            return left  *   right 
        elif node.op.text == "/":
            return left  /  right 
        elif node.op.text == "+":
            return left  +  right 
        elif node.op.text == "-":
            return left  -  right 
            
            
    def visit_Ident(self, node):
        name = node.text
        ar = self.callstack.peek()
        value = ar.get(name)
        return value
        
    def visit_Num(self, node):
        return node.value
    
    
    def visit_LabelDecl(self, node):
        pass
    
    def visit_GotoDecl(self, node):
        pass
    
     