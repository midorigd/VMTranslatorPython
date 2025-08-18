// for labels of function filename.func

/* label LABELNAME */

(filename.func$LABELNAME)


/* goto LABELNAME (unconditional goto) */

@filename.func$LABELNAME
0;JMP


/* if-goto LABELNAME (conditional goto) */

// implementation: D = stack.pop()
// if D: goto LABELNAME

stack.pop(D)

@filename.func$LABELNAME
D;JNE // Boolean implementation: -1 = True, 0 = False
