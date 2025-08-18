from src.Parser import Parser
from src.CodeWriter import CodeWriter
from src.VMConstants import COMMAND

import os
import glob

class VMTranslator:
    def __init__(self, sourceFile: str, *, commentMode=False):
        inFiles, outFile = VMTranslator.fileManager(sourceFile)
        self._inFiles = inFiles
        self._codeWriter = CodeWriter(outFile, commentMode)

    @staticmethod
    def sortSysInit(vmFile: str):
        return vmFile == 'Sys.vm'

    @staticmethod
    def fileManager(file: str):
        file = file.rstrip(os.sep)

        dirname = file if os.path.isdir(file) else os.path.dirname(file)
        outFile = os.path.basename(file).removesuffix('.vm') + '.asm'

        os.chdir(dirname)
        fileLst = glob.glob('*.vm')
        fileLst.sort(key=VMTranslator.sortSysInit, reverse=True)

        return fileLst, outFile

    def translateAll(self):
        if self._inFiles[0] == 'Sys.vm':
            self._codeWriter.writeBootstrap()
        
        for vmFile in self._inFiles:
            self._translate(vmFile)
        
        self._codeWriter.closeFile()

    def _translate(self, vmFile: str):
        parser = Parser(vmFile)
        self._codeWriter.loadFile(vmFile)

        while parser.hasMoreLines():
            parser.advance()

            match parser.commandType():
                case COMMAND.ARITHMETIC:    self._codeWriter.writeArithmetic(parser.arg1())
                case COMMAND.LABEL:         self._codeWriter.writeLabel(parser.arg1())
                case COMMAND.GOTO:          self._codeWriter.writeGoto(parser.arg1())
                case COMMAND.IF:            self._codeWriter.writeIf(parser.arg1())
                case COMMAND.CALL:          self._codeWriter.writeCall(parser.arg1(), parser.arg2())
                case COMMAND.FUNCTION:      self._codeWriter.writeFunction(parser.arg1(), parser.arg2())
                case COMMAND.RETURN:        self._codeWriter.writeReturn()
                case _:                     self._codeWriter.writePushPop(parser.commandType(), parser.arg1(), parser.arg2())
