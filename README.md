# VMTranslator (Python)

This is a Python implementation of the VM language to Hack assembly translator from projects 7-8 of nand2tetris.

The assembler takes a single `.vm` file or a directory of `.vm` files as a command-line argument and creates an `.asm` file with the corresponding assembly code.

## Modules

VMTranslator: Program entry point  

### src

CodeWriter: Writes assembly commands to output  
Parser: Handles input filestream and categorizes commands and arguments  
VMConstants: Enums for commands, segments, and operators  
VMTranslator: Drives the translation process  

### utils

ArrayStack: A simple implementation of a stack
utils: Helper functions for command line argument processing

## Building the project

Run the following from the terminal:

```zsh
git clone https://github.com/midorigd/VMTranslatorPython
cd VMTranslatorPython
```

## Running the project

Run one of the following from the project directory:

```zsh
python3 -m VMTranslator path/to/dir
python3 -m VMTranslator path/to/file.vm
```

## Notes

My C++ implementation of this project: [VMTranslator (C++)](https://github.com/midorigd/VMTranslatorCpp)

## References

[nand2tetris](https://www.nand2tetris.org/course)

