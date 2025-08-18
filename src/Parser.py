from src.VMConstants import *

import re

class Parser:
    def __init__(self, filename: str):
        with open(filename) as file:
            self._data = [trimLine for line in file.readlines() if (trimLine := Parser._removeComments(line)) != '']
        self._pos = -1

    @staticmethod
    def _removeComments(line):
        return re.sub(r'//.*', '', line.strip())

    @property
    def _current(self):
        return self._data[self._pos].split()

    def hasMoreLines(self):
        return self._pos < len(self._data) - 1
    
    def advance(self):
        self._pos += 1
    
    def commandType(self):
        keyword = self._current[0]
        if keyword in COMMAND:
            return COMMAND(keyword)
        return COMMAND.ARITHMETIC
    
    def arg1(self):
        if (type := self.commandType()) is COMMAND.RETURN:
            raise TypeError('RETURN commands have no arguments')
        
        if type is COMMAND.ARITHMETIC:
            return OP(self._current[0])
            # return Parser._arithmeticLookup[self._current[0]]
        
        if type is COMMAND.PUSH or type is COMMAND.POP:
            return SEGMENT(self._current[1])
            # return Parser._segmentLookup[self._current[1]]
        
        return self._current[1]
    
    def arg2(self):
        if self.commandType() not in {COMMAND.PUSH, COMMAND.POP, COMMAND.FUNCTION, COMMAND.CALL}:
            raise TypeError(f'{self.commandType()} commands only have 1 argument')
        
        return int(self._current[2])
