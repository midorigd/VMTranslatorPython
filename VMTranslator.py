from src.VMTranslator import VMTranslator
from utils.utils import *

import sys

def main():
    if not isValidArguments(sys.argv):
        displayUsage()
        return

    sourceFile = sys.argv[1]
    commentMode = (len(sys.argv) == 3)

    translator = VMTranslator(sourceFile, commentMode)
    translator.translateAll()

main()
