def isValidArguments(argv):
    return len(argv) == 2 or (len(argv) == 3 and argv[2] == '-c')

def displayUsage():
    print('Usage: python3 -m VMTranslator <dirname OR filename.vm> [-c]')
    print('   -c: Enables comments in output file')
