/* call functionName nArgs */

// create and save return address label: @{functionName}$ret.{returnID}
@thisFunction$ret.1
D=A
stack.push(D)

// save caller's segment pointers: push LCL, ARG, THIS, THAT to stack
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

// reposition ARG to function args: ARG = SP - 5 - nArgs
@SP
D=M
@5
D=D-A
@{nArgs}
D=D-A
@ARG
M=D

// reposition LCL to top of global stack: LCL = SP
@SP
D=M
@LCL
M=D

// inject branching to called function
@functionName
0;JMP

// inject return address label
(thisFunction$ret.1)


/*

   GLOBAL STACK
------------------
caller stack
function args x nArgs
return address
saved LCL
saved ARG
saved THIS
saved THAT

*/
