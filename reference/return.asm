/* return */

// endFrame is memory address immediately below saved pointers of caller
@LCL
D=M
@endFrame
M=D

// retAddr is return address to jump to after finishing function call
@5
A=D-A
D=M
@retAddr
M=D

// replace function args with return value
stack.pop(D)
@ARG
A=M
M=D

// move SP to point directly below return value, erasing function memory
@ARG
D=M
@SP
M=D+1

// restore segment pointers LCL, ARG, THIS, THAT
@endFrame
D=M

@{pointerOffset} // LCL = 4, ARG = 3, etc.
A=D-A
D=M
@{segment}
M=D

// jump to return address
@retAddr
A=M
0;JMP


/*

   GLOBAL STACK
------------------
caller stack
function args x nArgs  <- REPLACE WITH return value
return address         <- move SP here, "erasing" memory below return value
saved LCL
saved ARG
saved THIS
saved THAT
local vars x nVars
working callee stack
return value

*/
