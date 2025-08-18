/* bootstrap code */

// SP = 256
@256
D=A
@SP
M=D

/* call Sys.init (no arguments) */

// create and save return address label
@Sys.init$ret.0
D=A
stack.push(D)

// save caller segment pointers: LCL, ARG, THIS, THAT
@LCL
D=M
stack.push(D)

@ARG
D=M
stack.push(D)

@THIS
D=M
stack.push(D)

@THAT
D=M
stack.push(D)

// reposition ARG to function args: ARG = SP - 5
@SP
D=M
@5
D=D-A
@ARG
M=D

// reposition LCL to top of global stack: LCL = SP
@SP
D=M
@LCL
M=D

// inject branching to called function
@Sys.init
0;JMP

// inject return address label
(Sys.init$ret.0)
