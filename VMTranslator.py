from src.VMTranslator import VMTranslator

import sys

def main():
    if len(sys.argv) == 2:
        sourceFile = sys.argv[1]
    else:
        print('Usage: python3 -m VMTranslator <dirname OR filename.vm>')
        return

    translator = VMTranslator(sourceFile)
    translator.translateAll()

main()
