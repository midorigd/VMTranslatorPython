// stack.push(D)
@SP
A=M
M=D
@SP
M=M+1

// D = stack.pop()
@SP
AM=M-1
D=M
