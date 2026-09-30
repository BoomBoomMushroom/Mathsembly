class Instruction:
    def __init__(self, opcode: int = 0x00, operandBytes: int = 0):
        self.opcode = opcode
        self.operandBytes = operandBytes


class EXAMPLE_Instruction(Instruction):
    """
    ``\n
    
    """
    def __init__(self):
        super().__init__(opcode=0x00, operandBytes=0)

# Misc and I/O instructions | 0x00-0x1F
class NOP_Instruction(Instruction):
    """
    `NOP`\n
    Does nothing
    """
    def __init__(self):
        super().__init__(opcode=0x00, operandBytes=0)

class MOVE_Instruction(Instruction):
    """
    `STORE REG_A REG_B`\n
    REG_A: The source register\n
    REG_B: The destination register\n
    Copies the value in REG_A into REG_B
    """
    def __init__(self):
        super().__init__(opcode=0x01, operandBytes=2)

class SHOW_Instruction(Instruction):
    """
    `SHOW`\n
    Draws the screen with the values in video memory
    """
    def __init__(self):
        super().__init__(opcode=0x01, operandBytes=0)

class PRINT_Instruction(Instruction):
    """
    `PRINT N TYPE`\n
    N: Length of the printed string\n
    TYPE: How to print the data, 0=UTF-8, 1=BINARY, 2=DECIMAL, 3=HEXADECIMAL\n
    Prints bytes from `ADDR` to `ADDR+N` (include, exclusive) displayed as the type specified
    """
    def __init__(self):
        super().__init__(opcode=0x02, operandBytes=2)

# Boolean Instructions | 0x10-0x1F
class NOT_Instruction(Instruction):
    """
    `NOT REG_A, REG_B`\n
    REG_A: The register holding the value to invert\n
    REG_B: The register that will receive the changed value\n
    Inverts the value in `REG_A` and then stores it in `REG_B`
    """
    def __init__(self):
        super().__init__(opcode=0x10, operandBytes=2)

class AND_Instruction(Instruction):
    """
    `AND REG_A REG_B REG_C`\n
    REG_A: The first operand in `A & B`\n
    REG_B: The second operand in `A & B`\n
    REG_C: The place to store the result of `A & B`\n
    Computes `REG_A & REG_B` and stores it in `REG_C`    
    """
    def __init__(self):
        super().__init__(opcode=0x11, operandBytes=3)

class OR_Instruction(Instruction):
    """
    `OR REG_A REG_B REG_C`\n
    REG_A: The first operand in `A | B`\n
    REG_B: The second operand in `A | B`\n
    REG_C: The place to store the result of `A | B`\n
    Computes `REG_A | REG_B` and stores it in `REG_C`    
    """
    def __init__(self):
        super().__init__(opcode=0x12, operandBytes=3)

class XOR_Instruction(Instruction):
    """
    `XOR REG_A REG_B REG_C`\n
    REG_A: The first operand in `A ^ B`\n
    REG_B: The second operand in `A ^ B`\n
    REG_C: The place to store the result of `A ^ B`\n
    Computes `REG_A ^ REG_B` and stores it in `REG_C`    
    """
    def __init__(self):
        super().__init__(opcode=0x13, operandBytes=3)

# Math Instructions | 0x20-0x2F
class ADD_Instruction(Instruction):
    """
    `ADD REG_A REG_B REG_C`\n
    REG_A: The first operand in `A + B`\n
    REG_B: The second operand in `A + B`\n
    REG_C: The place to store the result of `A + B`\n
    Computes `REG_A + REG_B` and stores it in `REG_C`    
    """
    def __init__(self):
        super().__init__(opcode=0x20, operandBytes=3)

class SUB_Instruction(Instruction):
    """
    `SUB REG_A REG_B REG_C`\n
    REG_A: The first operand in `A - B`\n
    REG_B: The second operand in `A - B`\n
    REG_C: The place to store the result of `A - B`\n
    Computes `REG_A - REG_B` and stores it in `REG_C`    
    """
    def __init__(self):
        super().__init__(opcode=0x21, operandBytes=3)

class MULT_Instruction(Instruction):
    """
    `MULT REG_A REG_B REG_C`\n
    REG_A: The first operand in `A * B`\n
    REG_B: The second operand in `A * B`\n
    REG_C: The place to store the result of `A * B`\n
    Computes `REG_A * REG_B` and stores it in `REG_C`    
    """
    def __init__(self):
        super().__init__(opcode=0x22, operandBytes=3)

class DIV_Instruction(Instruction):
    """
    `DIV REG_A REG_B REG_C`\n
    REG_A: The first operand in `A / B`\n
    REG_B: The second operand in `A / B`\n
    REG_C: The place to store the result of `A / B`\n
    Computes `REG_A / REG_B` and stores it in `REG_C`    
    """
    def __init__(self):
        super().__init__(opcode=0x23, operandBytes=3)

class SQRT_Instruction(Instruction):
    """
    `SQRT REG_A, REG_B`\n
    REG_A: The register holding the value to square root\n
    REG_B: The register that will receive the changed value\n
    Square roots the value in `REG_A` and then stores it in `REG_B`
    """
    def __init__(self):
        super().__init__(opcode=0x24, operandBytes=2)

