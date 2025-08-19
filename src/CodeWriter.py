from src.VMConstants import *
from utils.ArrayStack import ArrayStack

class CodeWriter:
    _STACK_POINTER = 256

    _INIT_FUNC = 'Sys.init'
    _TEMP_ADDR = 'addr'
    _TEMP_VAR = 'y'
    _RET_ADDR = 'retAddr'
    _END_FRAME = 'endFrame'

    _mappedSegments = {
        SEGMENT.LCL: 4,
        SEGMENT.ARG: 3,
        SEGMENT.THIS: 2,
        SEGMENT.THAT: 1
    }

    def __init__(self, outFile: str, commentMode: bool):
        self._outFile = open(outFile, 'w')
        self._commentMode = commentMode

        # trackers for reused command-specific labels
        self._arithLabelID = 0
        self._functionLabelID = 0
        self._returnAddressID = 0

        self._callStack = ArrayStack()
        self._callStack.push('')

    def loadFile(self, vmFile: str):
        self._filename = vmFile.removesuffix('.vm')
    
    def _currFunction(self):
        return self._callStack.top()
    
    def _createBoundLabel(self, label: str):
        return f'{self._currFunction()}${label}'
    
    def _createReturnLabel(self):
        id = self._returnAddressID
        self._returnAddressID += 1
        return f'{self._currFunction()}$ret.{id}'

    def _createUniqueLabels(self, counter: str, category: str, label1: str, label2: str):
        id = getattr(self, counter)
        setattr(self, counter, id + 1)
        return f'{category}.{label1}{id}', f'{category}.{label2}{id}'
    
    def _createLogicLabels(self):
        return self._createUniqueLabels('_arithLabelID', 'LOGIC', 'COMPTRUE', 'COMPEND')

    def _createFunctionLabels(self):
        return self._createUniqueLabels('_functionLabelID', 'FUNC', 'INITLOCALVARS', 'INITLOCALSEND')


    def writeBootstrap(self):
        self.writeComment('Bootstrap code')

        self._callStack.push(CodeWriter._INIT_FUNC)

        self.constToData(CodeWriter._STACK_POINTER)
        self.dataToPtr(SEGMENT.SP)

        self.writeCall(CodeWriter._INIT_FUNC, 0)

    def writeArithmetic(self, command: OP):
        self.writeComment(command)

        # commands: neg, not (unary operators)
        if command.isUnaryOp():
            self.popD()
            self.commandDestC('D', f'{command}D')
            self.pushD()

        # commands: eq, gt, lt
        elif command.isLogicOp():
            trueLabel, falseLabel = self._createLogicLabels()

            self.popD()
            self.dataToPtr(CodeWriter._TEMP_VAR)

            self.popD()
            self.commandA(CodeWriter._TEMP_VAR)
            self.commandDestC('D', 'D-M')

            self.commandA(trueLabel)
            self.commandJumpC('D', command)

            self.commandDestC('D', 0)
            self.commandA(falseLabel)
            self.absJump()

            self.commandL(trueLabel)
            self.commandDestC('D', -1)

            self.commandL(falseLabel)
            self.pushD()

        # commands: add, sub, and, or
        else:
            self.popD()
            self.dataToPtr(CodeWriter._TEMP_VAR)

            self.popD()
            self.commandA(CodeWriter._TEMP_VAR)
            self.commandDestC('D', f'D{command}M')
            self.pushD()

    def writePushPop(self, command: COMMAND, segment: SEGMENT, index: int):
        self.writeComment(f'{command} {segment} {index}')

        if segment is SEGMENT.CONSTANT:
            if command is COMMAND.POP:
                raise TypeError('Cannot pop to constant segment')

            self.constToData(index)
            self.pushD()

        # segments: local, argument, this, that
        elif segment in CodeWriter._mappedSegments:
            self.copyPointer(segment, CodeWriter._TEMP_ADDR)

            self.constToData(index)
            self.commandA(CodeWriter._TEMP_ADDR)
            self.commandDestC('M', 'M+D')

            if command is COMMAND.PUSH:
                self.dereferencePtr()
                self.memToData()
                self.pushD()

            else:
                self.popD()
                self.commandA(CodeWriter._TEMP_ADDR)
                self.dereferencePtr()
                self.dataToMem()

        # segments: static, temp, pointer
        else:
            # static i in file foo.vm = foo.i
            if segment is SEGMENT.STATIC:
                pointer = f'{self._filename}.{index}'
            
            # temp i = RAM[i + 5]
            elif segment is SEGMENT.TEMP:
                pointer = index + 5
            
            # pointer 0 = THIS, pointer 1 = THAT
            else:
                pointer = SEGMENT.THIS if index == 0 else SEGMENT.THAT
            
            if command is COMMAND.PUSH:
                self.ptrToData(pointer)
                self.pushD()

            else:
                self.popD()
                self.dataToPtr(pointer)

    def writeLabel(self, label: str):
        self.writeComment(f'label {label}')
        self.commandL(self._createBoundLabel(label))

    def writeGoto(self, label: str):
        self.writeComment(f'goto {label}')
        self.commandA(self._createBoundLabel(label))
        self.absJump()

    def writeIf(self, label: str):
        self.writeComment(f'if-goto {label}')
        self.popD()
        self.commandA(self._createBoundLabel(label))
        self.commandJumpC('D', JUMP.JNE)

    def writeCall(self, functionName: str, nArgs: int):
        returnLabel = self._createReturnLabel()

        self.writeComment(f'call {functionName} {nArgs}')

        self.constToData(returnLabel)
        self.pushD()

        for segment in CodeWriter._mappedSegments:
            self.savePointer(segment)

        self.ptrToData(SEGMENT.SP)
        self.commandA(5 + nArgs)
        self.commandDestC('D', 'D-A')

        self.dataToPtr(SEGMENT.ARG)

        self.copyPointer(SEGMENT.SP, SEGMENT.LCL)

        self.commandA(functionName)
        self.absJump()

        self.commandL(returnLabel)

    def writeFunction(self, functionName: str, nVars: int):
        loopLabel, endLabel = self._createFunctionLabels()

        self.writeComment(f'function {functionName} {nVars}')

        self.commandL(functionName)
        self.constToData(nVars)

        self.commandL(loopLabel)
        self.commandA(endLabel)
        self.commandJumpC('D', JUMP.JEQ)

        self.push(0)
        self.decrement('D')

        self.commandA(loopLabel)
        self.absJump()

        self.commandL(endLabel)

        self._callStack.push(functionName)

    def writeReturn(self):
        self.writeComment('return')

        self.copyPointer(SEGMENT.LCL, CodeWriter._END_FRAME)
        self.restorePointer(CodeWriter._RET_ADDR, 5)

        self.popD()
        self.loadArgPtr()
        self.dereferencePtr()
        self.dataToMem()

        self.ptrToData(SEGMENT.ARG)
        self.loadStackPtr()
        self.commandDestC('M', 'D+1')

        for segment, offset in CodeWriter._mappedSegments.items():
            self.restorePointer(segment, offset)

        self.commandA(CodeWriter._RET_ADDR)
        self.dereferencePtr()
        self.absJump()


    def writeCommand(self, command: str):
        print(command, file=self._outFile)

    def writeComment(self, comment: str):
        if self._commentMode:
            self.writeCommand(f'\n// {comment}')

    def commandA(self, label: SEGMENT | str | int):
        self.writeCommand(f'@{label}')

    def commandDestC(self, dest: str, comp: str | int):
        self.writeCommand(f'{dest}={comp}')

    def commandJumpC(self, comp: str | int, jump: JUMP):
        self.writeCommand(f'{comp};{jump}')

    def commandL(self, label):
        self.writeCommand(f'({label})')


    def increment(self, reg: str):
        self.commandDestC(reg, f'{reg}+1')

    def decrement(self, reg: str):
        self.commandDestC(reg, f'{reg}-1')

    def memToData(self):
        self.commandDestC('D', 'M')

    def dataToMem(self):
        self.commandDestC('M', 'D')

    def dereferencePtr(self):
        self.commandDestC('A', 'M')

    def absJump(self):
        self.commandJumpC(0, JUMP.JMP)

    def loadArgPtr(self):
        self.commandA(SEGMENT.ARG)

    def loadStackPtr(self):
        self.commandA(SEGMENT.SP)

    def constToData(self, const: str | int):
        self.commandA(const)
        self.commandDestC('D', 'A')

    def ptrToData(self, pointer: SEGMENT | str | int):
        self.commandA(pointer)
        self.memToData()

    def dataToPtr(self, pointer: SEGMENT | str | int):
        self.commandA(pointer)
        self.dataToMem()


    def push(self, elem: str | int):
        self.loadStackPtr()
        self.dereferencePtr()
        self.commandDestC('M', elem)
        self.loadStackPtr()
        self.increment('M')

    def pushD(self):
        self.push('D')

    def popD(self):
        self.loadStackPtr()
        self.commandDestC('AM', 'M-1')
        self.memToData()

    def savePointer(self, pointer: SEGMENT | str | int):
        self.ptrToData(pointer)
        self.pushD()

    def copyPointer(self, src: SEGMENT | str, dest: SEGMENT | str):
        self.ptrToData(src)
        self.dataToPtr(dest)

    def restorePointer(self, pointer: SEGMENT | str, offset: int):
        if not pointer is CodeWriter._RET_ADDR:
            self.ptrToData(CodeWriter._END_FRAME)

        self.commandA(offset)
        self.commandDestC('A', 'D-A')
        self.memToData()
        self.dataToPtr(pointer)


    def closeFile(self):
        self._outFile.close()
