/* function functionName nVars */

// inject function's entry point label
(functionName)

// initialize nVars local variables: push 0 to stack nVars times
@{nVars}
D=A

(INITLOCALVARS)
@INITLOCALSEND
D;JEQ

stack.push(0)
D=D-1

@INITLOCALVARS
0;JMP

(INITLOCALSEND)


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
local vars x nVars
working callee stack

*/
