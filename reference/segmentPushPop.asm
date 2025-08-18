/* push constant i */

@{i}
D=A
stack.push(D)


/* push local i */

@LCL // same as pop from here...
D=M
@addr
M=D

@{i}
D=A
@addr
M=M+D // ...to here

A=M
D=M

stack.push(D)


/* pop local i */

@LCL // RAM[LCL] = 1015
D=M
@addr // addr = 1015 = RAM[LCL]
M=D

@{i} // D = 2 = index
D=A
@addr // addr += index
M=M+D

stack.pop(D)

@addr // RAM[addr + index] = D
A=M
M=D


/* push static/temp/pointer i */

@pointer
D=M
stack.push(D)


/* pop static/temp/pointer i */

stack.pop(D)
@pointer
M=D
