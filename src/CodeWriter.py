from src.VMConstants import *
from utils.ArrayStack import ArrayStack

class CodeWriter:
    STACK_POINTER = 256

    INIT_FUNC = 'Sys.init'
    TEMP_ADDR = 'addr'
    TEMP_VAR = 'y'
    RET_ADDR = 'retAddr'
    END_FRAME = 'endFrame'

    # trackers for reused command-specific labels
    _arithLabelID = 0
    _functionLabelID = 0
    _returnAddressID = 0

    _callStack = ArrayStack()

    # lookup tables for commands and arguments
    _offsetTable = {
        SEGMENT.LCL: 4,
        SEGMENT.ARG: 3,
        SEGMENT.THIS: 2,
        SEGMENT.THAT: 1
    }

    def __init__(self, outFile: str, commentMode: bool):
        self._outFile = open(outFile, 'w')
        self.commentMode = commentMode

    def loadFile(self, vmFile: str):
        self._fileBasename = vmFile.rstrip('.vm')
    
    def _currFunction(self):
        if CodeWriter._callStack.isEmpty():
            return ''
            # raise Exception('callStack is empty')
        
        return CodeWriter._callStack.top()
    
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

        CodeWriter._callStack.push(CodeWriter.INIT_FUNC)

        self.constToData(CodeWriter.STACK_POINTER)
        self.dataToPtr(SEGMENT.SP)

        self.writeCall(CodeWriter.INIT_FUNC, 0)

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
            self.dataToPtr(CodeWriter.TEMP_VAR)

            self.popD()
            self.commandA(CodeWriter.TEMP_VAR)
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
            self.dataToPtr(CodeWriter.TEMP_VAR)

            self.popD()
            self.commandA(CodeWriter.TEMP_VAR)
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
        elif segment in CodeWriter._offsetTable:
            self.copyPointer(segment, CodeWriter.TEMP_ADDR)

            self.constToData(index)
            self.commandA(CodeWriter.TEMP_ADDR)
            self.commandDestC('M', 'M+D')

            if command is COMMAND.PUSH:
                self.dereferencePtr()
                self.memToData()
                self.pushD()

            else:
                self.popD()
                self.commandA(CodeWriter.TEMP_ADDR)
                self.dereferencePtr()
                self.dataToMem()

        # segments: static, temp, pointer
        else:
            # static i in foo.vm = foo.i
            if segment is SEGMENT.STATIC:
                pointer = f'{self._fileBasename}.{index}'
            
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

    # TO REVISE: bind filename.func$LABEL ??
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

    # TO REVISE: save pointer
    def writeCall(self, functionName: str, nArgs: int):
        returnLabel = self._createReturnLabel()

        self.writeComment(f'call {functionName} {nArgs}')

        self.constToData(returnLabel)
        self.pushD()

        for segment in CodeWriter._offsetTable:
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

        CodeWriter._callStack.push(functionName)

    # TO REVISE: offset pointer lookup
    def writeReturn(self):
        def restorePointer(segment: SEGMENT):
            self.ptrToData(CodeWriter.END_FRAME)
            self.commandA(CodeWriter._offsetTable[segment])
            self.commandDestC('A', 'D-A')
            self.memToData()
            self.dataToPtr(segment)

        self.writeComment('return')

        self.copyPointer(SEGMENT.LCL, CodeWriter.END_FRAME)

        self.commandA(5)
        self.commandDestC('A', 'D-A')
        self.memToData()
        self.commandA(CodeWriter.RET_ADDR)
        self.dataToMem()

        self.popD()
        self.loadArgPtr()
        self.dereferencePtr()
        self.dataToMem()

        self.ptrToData(SEGMENT.ARG)
        self.loadStackPtr()
        self.commandDestC('M', 'D+1')

        for segment in self._offsetTable:
            restorePointer(segment)

        self.commandA(CodeWriter.RET_ADDR)
        self.dereferencePtr()
        self.absJump()

        # self._callStack.pop()


    def writeCommand(self, command):
        print(command, file=self._outFile)

    def writeComment(self, comment):
        if self.commentMode:
            self.writeCommand(f'\n// {comment}')

    def commandA(self, label):
        self.writeCommand(f'@{label}')

    def commandDestC(self, dest, comp):
        self.writeCommand(f'{dest}={comp}')

    def commandJumpC(self, comp, jump):
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

    def constToData(self, const: SEGMENT | str | int):
        self.commandA(const)
        self.commandDestC('D', 'A')

    def ptrToData(self, pointer: SEGMENT | str | int):
        self.commandA(pointer)
        self.memToData()

    def dataToPtr(self, pointer: SEGMENT | str | int):
        self.commandA(pointer)
        self.dataToMem()


    def push(self, elem):
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


    def closeFile(self):
        self._outFile.close()
