/* commands: gt, lt, eq */

// y = D
stack.pop(D)
@y
M=D

// D = x
stack.pop(D)

// D = x-y
@y
D=D-M

// if D > 0, D = 0, D < 0: go to COMPTRUE
@COMPTRUE
D;JGT, D;JEQ, D;JLT

// else: skip COMPTRUE and go to COMPEND
D=0
@COMPEND
0;JMP

(COMPTRUE)
D=-1

(COMPEND)
stack.push(D)


/* commands: neg, not */

stack.pop(D)

// D = -D, !D
D=-D, D=!D

stack.push(D)


/* commands: add, subtract, and, or */

// y = D
stack.pop(D)
@y
M=D

// D = x
stack.pop(D)

// D = x+y, x-y, x&y, x|y
@y
D=D+M, D=D-M, D=D&M, D=D|M

stack.push(D)
