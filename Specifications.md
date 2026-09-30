INSTRUCTION OP1 OP2 ... OPn
64 General Registers | 8 Bytes
- 32 long long (8 byte integer) registers | REG_0I, REG_1I, ..., REG_31I
- 32 double (8 byte floats point) registers | REG_0F, REG_1F, ..., REG_31F

Special Registers
- ZERO - 8 Byte all 0s register. Writing will do nothing to it
- PC - 3 Byte program counter register
- SP - 1 Byte stack pointer
- ADDR - 3 Byte address register. Works just like a general register otherwise
- REG_M - The 8 bytes the ADDR register points. Works just like a general register. Reads and writes interact directly with memory

Memory Regions
- Everything shares the same memory
- 0x000000 to 0x00000F | ZERO, PC, SP, ADDR, and 0x20 (for padding) in that order
- 0x000010 to 0x00010F | REG_0I to REG_31I
- 0x000110 to 0x00020F | REG_0F to REG_31F
- 0x000210 to 0x00095F | 255 long longs (8 Bytes) in the stack
- 0x000960 to 0x00096F | Video Settings
- 0x000970 to 0x0E196F | Video Pixel Memory
- 0x0E1970 to 0xFFFFFF | Program and scratch memory, the first byte of the program is loaded into 0x0E1970

Video Settings

Instructions
- NOP
TODO: add branching and jumps etc

- MOVE
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
- ATAN2
