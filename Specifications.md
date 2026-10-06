Writing:
- `INSTRUCTION OP1 OP2 ... OPn` This is the format to write instructions, it's instruction name and then all of it's operands
- `;` Used for comments, everything after the first `;` of a line will be ignored
- `#` Used to place all the instructions and code after it into certain regions memory addresses, it must be >= 0x0E1970
    - During compile time `# 0x0E1970` is assumed added at the beginning of the program

64 General Registers | 8 Bytes
- 32 long long (8 byte integer) registers | REG_0I, REG_1I, ..., REG_31I
- 32 double (8 byte floats point) registers | REG_0F, REG_1F, ..., REG_31F

Special Registers
- ZERO - 8 Byte all 0s register. Writing will do nothing to it
- PC - 3 Byte program counter register
- SP - 1 Byte stack pointer
- ADDR - 3 Byte address register. Works just like a general register otherwise
- FLAGS - 1 Byte status/flags register. Normal integer register but instructions like `ADD` and `POW` will update it's value
- REG_M - The 8 bytes the ADDR register points. Works just like a general register. Reads and writes interact directly with memory

Memory Regions
- Everything shares the same memory
- 0x000000 to 0x00000F | ZERO, PC, SP, ADDR, and FLAGS in that order
- 0x000010 to 0x00010F | REG_0I to REG_31I
- 0x000110 to 0x00020F | REG_0F to REG_31F
- 0x000210 to 0x00095F | 255 long longs (8 Bytes) in the stack
- 0x000960 to 0x00096F | Video Settings
- 0x000970 to 0x0E196F | Video Pixel Memory
- 0x0E1970 to 0xFFFFFF | Program and scratch memory, the first byte of the program is loaded into 0x0E1970 by default

Video Settings
- It is possible to use the space after the video pixel memory region (inside of the program & scratch memory region) as more video memory if you use more memory than what is given. Be careful to not override your program though!
- Bytes 0 to 15 are mapped from 0x000960 to 0x00096F
- Bytes 0, 1, and 2 are for the video width (10 bits), video height (9 bits), and color bit depth (5 bits)
    - Bits (MSB on the left): WWWWWWWW WWHHHHHH HHHCCCCC
    - W = Video width, the dedicated video memory region has space for a max value of 640 at 24bbp (0x280 or 0b1010000000)
    - H = Video height, the dedicated video memory region has space for a max value of 480 at 24bbp (0x1e0 or 0b111100000)
    - C = Color bit depth, default accepted values are: 1, 2, 3, 4, 5, 6, 8, 12, 15, 16, 18, and 24

Flags Register (76543210)
- Bit 0: Zero flag
- Bit 1: Carry flag (Did overflow/underflow?)
- Bit 2: Negative flag
- Bit 3:
- Bit 4:
- Bit 5:
- Bit 6:
- Bit 7:

Instructions
- NOP
- STOP

- MOVE
- COPY
- CLTB
- SHOW
- PRINT

- NOT
- AND
- OR
- XOR

- ADD
- SUB
- MULT
- DIV
- MOD

- SQRT
- POW
- LN

- ROUND
- FLOOR
- CEIL

- SIN
- COS
- TAN
- ASIN
- ACOS
- ATAN

- JMZ
- JMC
- JMN
- JMP
- PUSH
- POP
