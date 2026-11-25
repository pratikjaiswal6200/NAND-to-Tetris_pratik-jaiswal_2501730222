// Roll 2501730222. Rows 22-41, columns 0-47.
// R13 = row address, R14 = rows left, R15 = pixel word.
(POLL)
    @KBD
    D=M
    @WHITE
    D;JEQ
    D=-1
    @SETUP
    0;JMP
(WHITE)
    D=0
(SETUP)
    @R15
    M=D
    @SCREEN
    D=A
    @704        // 22 rows times 32 words per row
    D=D+A
    @R13
    M=D
    @20
    D=A
    @R14
    M=D
(ROW)
    @R15
    D=M
    @R13
    A=M
    M=D
    A=A+1
    M=D
    A=A+1
    M=D
    @32         // Step from row start to next row start
    D=A
    @R13
    M=D+M
    @R14
    MD=M-1
    @ROW
    D;JGT
    @POLL
    0;JMP
