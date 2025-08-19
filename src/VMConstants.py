from enum import Enum

class PrintEnum(Enum):
    def __str__(self):
        return super().value.__str__()

class COMMAND(PrintEnum):
    PUSH = 'push'
    POP = 'pop'
    LABEL = 'label'
    GOTO = 'goto'
    IF = 'if-goto'
    CALL = 'call'
    FUNCTION = 'function'
    RETURN = 'return'
    ARITHMETIC = 'arithmetic'

class SEGMENT(PrintEnum):
    SP = 'SP'
    LCL = 'local'
    ARG = 'argument'
    THIS = 'this'
    THAT = 'that'
    CONSTANT = 'constant'
    STATIC = 'static'
    TEMP = 'temp'
    POINTER = 'pointer'

    def __str__(self):
        _strTable = {
            SEGMENT.LCL: 'LCL',
            SEGMENT.ARG: 'ARG',
            SEGMENT.THIS: 'THIS',
            SEGMENT.THAT: 'THAT'
        }
        return _strTable.get(self, super().__str__())

class JUMP(PrintEnum):
    JMP = 'JMP'
    JEQ = 'JEQ'
    JLT = 'JLT'
    JGT = 'JGT'
    JNE = 'JNE'

class OP(PrintEnum):
    ADD = 'add'
    SUB = 'sub'
    AND = 'and'
    OR = 'or'
    EQ = 'eq'
    GT = 'gt'
    LT = 'lt'
    NEG = 'neg'
    NOT = 'not'

    def __str__(self):
        _opTable = {
            OP.ADD: '+',
            OP.SUB: '-',
            OP.AND: '&',
            OP.OR: '|',
            OP.EQ: JUMP.JEQ,
            OP.GT: JUMP.JGT,
            OP.LT: JUMP.JLT,
            OP.NEG: '-',
            OP.NOT: '!'
        }
        return str(_opTable[self])

    def isUnaryOp(self):
        return self in {OP.NEG, OP.NOT}
    
    def isLogicOp(self):
        return self in {OP.EQ, OP.GT, OP.LT}
