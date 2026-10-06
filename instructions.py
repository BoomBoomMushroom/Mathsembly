import typing
import struct
import math

from registers import REGISTER
if typing.TYPE_CHECKING: from executor import Memory

class Instruction:
    def __init__(self, opcode: int = 0x00, operandBytes: int = 0):
        self.opcode = opcode
        self.operandBytes = operandBytes
    def execute(self, mem: Memory):
        raise NotImplementedError(f"Execute for this instruction has not been implemented yet! opcode={hex(self.opcode)}")


class PlaceInMemory_PseudoInstruction(Instruction):
    def __init__(self, location):
        self.location = location
        super().__init__(opcode=-1, operandBytes=-1)

class AddressReference_PseudoInstruction(Instruction):
    def __init__(self, name: str):
        self.name = name
        super().__init__(opcode=-1, operandBytes=-1)

# Misc and I/O instructions | 0x00-0x1F
class NOP_Instruction(Instruction):
    """
    `NOP`\n
    Does nothing
    """
    def __init__(self):
        super().__init__(opcode=0x00, operandBytes=0)

    def execute(self, mem): pass

class MOVE_Instruction(Instruction):
    """
    `STORE REG_A REG_B`\n
    REG_A: The source register\n
    REG_B: The destination register\n
    Copies the value in REG_A into REG_B\n
    If going from a float register to an integer register or vise versa it will convert appropriately\n
    Example: REG_0F (3.14) -> REG_0I(3)
    """
    def __init__(self, regA: REGISTER, regB: REGISTER):
        self.regA = regA
        self.regB = regB
        super().__init__(opcode=0x01, operandBytes=2)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]
        
        rVal = aVal
        rType = ">d" if mem.isFloatReg(self.regB) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"moving {self.regA} to {self.regB}")
        mem.setGeneralRegBytes(self.regB, rBytes)
        mem.zeroReg = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class COPY_Instruction(Instruction):
    """
    `COPY REG_A REG_B`\n
    REG_A: The source register\n
    REG_B: The destination register\n
    Copies the bytes value in REG_A into REG_B regardless of what they represent\n
    If the destination register has less bytes than the source, like REG_0I to ADDR, then it will copy the needed amount of bottom bytes from the source register into the destination register\n
    If the source register has less bytes than the destination, like ADDR to REG_0I, then it will copy into the the bottom bytes of the destination\n
    Example: REG_0F (3.14) -> REG_0I(4614253070214989087)\n
    """
    def __init__(self, regA: REGISTER, regB: REGISTER):
        self.regA = regA
        self.regB = regB
        super().__init__(opcode=0x02, operandBytes=2)

    def execute(self, mem):
        val: bytes = mem.getGeneralRegBytes(self.regA)
        mem.setGeneralRegBytes(self.regB, val)
        print(f"copying {val=} from {self.regA=} to {self.regB=}")

# Copy LsB to MsB (least significant byte to most significant byte)
class CLTB_Instruction(Instruction):
    """
    `CLTB REG_A REG_B`\n
    REG_A: The source register\n
    REG_B: The destination register\n
    Copies the least significant byte (rightmost/bottom 8 bits) of REG_A into the most significant byte (leftmost/top 8 bits) of REG_B regardless of what they represent\n
    """
    def __init__(self, regA: REGISTER, regB: REGISTER):
        self.regA = regA
        self.regB = regB
        
        super().__init__(opcode=0x03, operandBytes=2)
    
    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        bBytes = bytearray(mem.getGeneralRegBytes(self.regB))
        
        bBytes[0] = aBytes[-1]
        print(f"setting {self.regB}'s top byte to {self.regA}'s bottom byte topByte={aBytes[-1]}/{hex(aBytes[-1])} - b={bBytes}")
        mem.setGeneralRegBytes(self.regB, bBytes)

class SHOW_Instruction(Instruction):
    """
    `SHOW`\n
    Draws the screen with the values in video memory
    """
    def __init__(self):
        super().__init__(opcode=0x04, operandBytes=0)

class PRINT_Instruction(Instruction):
    """
    `PRINT REG_A REG_B`\n
    REG_A: The integer register, the value of the length of the printed string\n
    REG_B: The integer register, the value explains how to print the data, 0=UTF-8, 1=BINARY, 2=DECIMAL, 3=HEXADECIMAL\n
    Prints bytes from `ADDR` to `ADDR+N` (include, exclusive) displayed as the type specified
    """
    def __init__(self, regA:REGISTER, regB:REGISTER):
        self.regA = regA
        self.regB = regB
        super().__init__(opcode=0x05, operandBytes=2)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = math.floor(struct.unpack(aType, aBytes)[0])
        
        bBytes = mem.getGeneralRegBytes(self.regB)
        bType = ">d" if mem.isFloatReg(self.regB) else ">q"
        bVal = math.floor(struct.unpack(bType, bBytes)[0])
        
        strBytes = mem.readBytes(mem.addrReg, aVal, readAsBytes=True)
        strOut = ""
        if bVal == 0: strOut = strBytes.decode("utf-8")
        else:
            for byte in strBytes:
                appendVal = str(byte) # decimal
                if bVal == 1: appendVal = bin(byte)
                elif bVal == 3: appendVal = hex(byte)
                
                strOut += appendVal + " "
        
        return strOut

class STOP_Instruction(Instruction):
    """
    `STOP`\n
    Ends the program\n
    """
    def __init__(self):
        super().__init__(opcode=0x06, operandBytes=0)

# TODO: add stack popping and pushing

# Boolean Instructions | 0x10-0x1F
class NOT_Instruction(Instruction):
    """
    `NOT REG_A REG_B`\n
    REG_A: The register holding the value to invert\n
    REG_B: The register that will receive the changed value\n
    Inverts the value in `REG_A` and then stores it in `REG_B`
    """
    def __init__(self, regA: REGISTER, regB: REGISTER):
        self.regA = regA
        self.regB = regB
        super().__init__(opcode=0x10, operandBytes=2)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]
        
        rVal = ~aVal
        rType = ">d" if mem.isFloatReg(self.regB) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"not {self.regA} and storing it in {self.regB}; ~{aVal} = {rVal}")
        mem.setGeneralRegBytes(self.regC, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class AND_Instruction(Instruction):
    """
    `AND REG_A REG_B REG_C`\n
    REG_A: The first operand in `A & B`\n
    REG_B: The second operand in `A & B`\n
    REG_C: The place to store the result of `A & B`\n
    Computes `REG_A & REG_B` and stores it in `REG_C`    
    """
    def __init__(self, regA: REGISTER, regB: REGISTER, regC: REGISTER):
        self.regA = regA
        self.regB = regB
        self.regC = regC
        super().__init__(opcode=0x11, operandBytes=3)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]

        bBytes = mem.getGeneralRegBytes(self.regB)
        bType = ">d" if mem.isFloatReg(self.regB) else ">q"
        bVal = struct.unpack(bType, bBytes)[0]
        
        rVal = aVal & bVal
        rType = ">d" if mem.isFloatReg(self.regC) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"and {self.regA} & {self.regB} and storing it in {self.regC}; {aVal} & {bVal} = {rVal}")
        mem.setGeneralRegBytes(self.regC, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class OR_Instruction(Instruction):
    """
    `OR REG_A REG_B REG_C`\n
    REG_A: The first operand in `A | B`\n
    REG_B: The second operand in `A | B`\n
    REG_C: The place to store the result of `A | B`\n
    Computes `REG_A | REG_B` and stores it in `REG_C`    
    """
    def __init__(self, regA: REGISTER, regB: REGISTER, regC: REGISTER):
        self.regA = regA
        self.regB = regB
        self.regC = regC
        super().__init__(opcode=0x12, operandBytes=3)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]

        bBytes = mem.getGeneralRegBytes(self.regB)
        bType = ">d" if mem.isFloatReg(self.regB) else ">q"
        bVal = struct.unpack(bType, bBytes)[0]
        
        rVal = aVal | bVal
        rType = ">d" if mem.isFloatReg(self.regC) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"or {self.regA} | {self.regB} and storing it in {self.regC}; {aVal} | {bVal} = {rVal}")
        mem.setGeneralRegBytes(self.regC, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class XOR_Instruction(Instruction):
    """
    `XOR REG_A REG_B REG_C`\n
    REG_A: The first operand in `A ^ B`\n
    REG_B: The second operand in `A ^ B`\n
    REG_C: The place to store the result of `A ^ B`\n
    Computes `REG_A ^ REG_B` and stores it in `REG_C`    
    """
    def __init__(self, regA: REGISTER, regB: REGISTER, regC: REGISTER):
        self.regA = regA
        self.regB = regB
        self.regC = regC
        super().__init__(opcode=0x13, operandBytes=3)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]

        bBytes = mem.getGeneralRegBytes(self.regB)
        bType = ">d" if mem.isFloatReg(self.regB) else ">q"
        bVal = struct.unpack(bType, bBytes)[0]
        
        rVal = aVal ^ bVal
        rType = ">d" if mem.isFloatReg(self.regC) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"xor {self.regA} ^ {self.regB} and storing it in {self.regC}; {aVal} ^ {bVal} = {rVal}")
        mem.setGeneralRegBytes(self.regC, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

# Math Instructions | 0x20-0x2F
class ADD_Instruction(Instruction):
    """
    `ADD REG_A REG_B REG_C`\n
    REG_A: The first operand in `A + B`\n
    REG_B: The second operand in `A + B`\n
    REG_C: The place to store the result of `A + B`\n
    Computes `REG_A + REG_B` and stores it in `REG_C`    
    """
    def __init__(self, regA: REGISTER, regB: REGISTER, regC: REGISTER):
        self.regA = regA
        self.regB = regB
        self.regC = regC

        super().__init__(opcode=0x20, operandBytes=3)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]

        bBytes = mem.getGeneralRegBytes(self.regB)
        bType = ">d" if mem.isFloatReg(self.regB) else ">q"
        bVal = struct.unpack(bType, bBytes)[0]
        
        rVal = aVal + bVal
        rType = ">d" if mem.isFloatReg(self.regC) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"adding {self.regA} with {self.regB} and storing it in {self.regC}; {aVal} + {bVal} = {rVal}")
        mem.setGeneralRegBytes(self.regC, rBytes)
        mem.zeroReg = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class SUB_Instruction(Instruction):
    """
    `SUB REG_A REG_B REG_C`\n
    REG_A: The first operand in `A - B`\n
    REG_B: The second operand in `A - B`\n
    REG_C: The place to store the result of `A - B`\n
    Computes `REG_A - REG_B` and stores it in `REG_C`    
    """
    def __init__(self, regA: REGISTER, regB: REGISTER, regC: REGISTER):
        self.regA = regA
        self.regB = regB
        self.regC = regC

        super().__init__(opcode=0x21, operandBytes=3)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]

        bBytes = mem.getGeneralRegBytes(self.regB)
        bType = ">d" if mem.isFloatReg(self.regB) else ">q"
        bVal = struct.unpack(bType, bBytes)[0]
        
        rVal = aVal - bVal
        rType = ">d" if mem.isFloatReg(self.regC) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"subtracting {self.regA} - {self.regB} and storing it in {self.regC}; {aVal} - {bVal} = {rVal}")
        mem.setGeneralRegBytes(self.regC, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class MULT_Instruction(Instruction):
    """
    `MULT REG_A REG_B REG_C`\n
    REG_A: The first operand in `A * B`\n
    REG_B: The second operand in `A * B`\n
    REG_C: The place to store the result of `A * B`\n
    Computes `REG_A * REG_B` and stores it in `REG_C`    
    """
    def __init__(self, regA: REGISTER, regB: REGISTER, regC: REGISTER):
        self.regA = regA
        self.regB = regB
        self.regC = regC

        super().__init__(opcode=0x22, operandBytes=3)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]

        bBytes = mem.getGeneralRegBytes(self.regB)
        bType = ">d" if mem.isFloatReg(self.regB) else ">q"
        bVal = struct.unpack(bType, bBytes)[0]
        
        rVal = aVal * bVal
        rType = ">d" if mem.isFloatReg(self.regC) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"multiplying {self.regA} * {self.regB} and storing it in {self.regC}; {aVal} * {bVal} = {rVal}")
        mem.setGeneralRegBytes(self.regC, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class DIV_Instruction(Instruction):
    """
    `DIV REG_A REG_B REG_C`\n
    REG_A: The first operand in `A / B`\n
    REG_B: The second operand in `A / B`\n
    REG_C: The place to store the result of `A / B`; If it's an integer register it will automatically round down\n
    Computes `REG_A / REG_B` and stores it in `REG_C`    
    """
    def __init__(self, regA: REGISTER, regB: REGISTER, regC: REGISTER):
        self.regA = regA
        self.regB = regB
        self.regC = regC

        super().__init__(opcode=0x23, operandBytes=3)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]

        bBytes = mem.getGeneralRegBytes(self.regB)
        bType = ">d" if mem.isFloatReg(self.regB) else ">q"
        bVal = struct.unpack(bType, bBytes)[0]
        
        rVal = aVal / bVal
        rType = ">d" if mem.isFloatReg(self.regC) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"diving {self.regA} / {self.regB} and storing it in {self.regC}; {aVal} / {bVal} = {rVal}")
        mem.setGeneralRegBytes(self.regC, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class SQRT_Instruction(Instruction):
    """
    `SQRT REG_A REG_B`\n
    REG_A: The register holding the value to square root\n
    REG_B: The register that will receive the resulting value; If it's an integer register it will automatically round down\n
    Square roots the value in `REG_A` and then stores it in `REG_B`
    """
    def __init__(self, regA: REGISTER, regB: REGISTER):
        self.regA = regA
        self.regB = regB
        super().__init__(opcode=0x24, operandBytes=2)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]
        
        rVal = math.sqrt(aBytes)
        rType = ">d" if mem.isFloatReg(self.regB) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"sqrt {self.regA} and storing it in {self.regB}; sqrt({aVal}) = {rVal}")
        mem.setGeneralRegBytes(self.regB, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class POW_Instruction(Instruction):
    """
    `POW REG_A REG_B REG_C`\n
    REG_A: The first operand in `A ** B`\n
    REG_B: The second operand in `A ** B`\n
    REG_C: The place to store the result of `A ** B`\n
    Computes REG_A raised to the power of REG_B and stores it in `REG_C`    
    """
    def __init__(self, regA: REGISTER, regB: REGISTER, regC: REGISTER):
        self.regA = regA
        self.regB = regB
        self.regC = regC
        super().__init__(opcode=0x25, operandBytes=3)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]

        bBytes = mem.getGeneralRegBytes(self.regB)
        bType = ">d" if mem.isFloatReg(self.regB) else ">q"
        bVal = struct.unpack(bType, bBytes)[0]
        
        rVal = aVal ** bVal
        rType = ">d" if mem.isFloatReg(self.regC) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"pow {self.regA} ** {self.regB} and storing it in {self.regC}; {aVal} ** {bVal} = {rVal}")
        mem.setGeneralRegBytes(self.regC, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class LN_Instruction(Instruction):
    """
    `LN REG_A REG_B`\n
    REG_A: The register holding the value to take the natural log of\n
    REG_B: The register that will receive the` resulting value\n
    Takes the natural log of the value in `REG_A` and then stores it in `REG_B`
    """
    def __init__(self, regA: REGISTER, regB: REGISTER):
        self.regA = regA
        self.regB = regB
        super().__init__(opcode=0x26, operandBytes=2)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]
        
        rVal = math.log(aBytes)
        rType = ">d" if mem.isFloatReg(self.regB) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"ln {self.regA} and storing it in {self.regB}; ln({aVal}) = {rVal}")
        mem.setGeneralRegBytes(self.regB, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class ROUND_Instruction(Instruction):
    """
    `ROUND REG_A REG_B`\n
    REG_A: The float register holding the value to round \n
    REG_B: The register that will receive the` resulting value\n
    Rounds the value in `REG_A` and then stores it in `REG_B`
    """
    def __init__(self, regA: REGISTER, regB: REGISTER):
        self.regA = regA
        self.regB = regB
        super().__init__(opcode=0x27, operandBytes=2)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]
        
        rVal = round(aBytes)
        rType = ">d" if mem.isFloatReg(self.regB) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"rounding {self.regA} and storing it in {self.regB}; round({aVal}) = {rVal}")
        mem.setGeneralRegBytes(self.regB, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class FLOOR_Instruction(Instruction):
    """
    `FLOOR REG_A REG_B`\n
    REG_A: The float register holding the value to round \n
    REG_B: The register that will receive the` resulting value\n
    Floors the value in `REG_A` and then stores it in `REG_B`
    """
    def __init__(self, regA: REGISTER, regB: REGISTER):
        self.regA = regA
        self.regB = regB
        super().__init__(opcode=0x28, operandBytes=2)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]
        
        rVal = math.floor(aBytes)
        rType = ">d" if mem.isFloatReg(self.regB) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"floor {self.regA} and storing it in {self.regB}; floor({aVal}) = {rVal}")
        mem.setGeneralRegBytes(self.regB, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class CEIL_Instruction(Instruction):
    """
    `CEIL REG_A REG_B`\n
    REG_A: The float register holding the value to round \n
    REG_B: The register that will receive the` resulting value\n
    Ceils the value in `REG_A` and then stores it in `REG_B`
    """
    def __init__(self, regA: REGISTER, regB: REGISTER):
        self.regA = regA
        self.regB = regB
        super().__init__(opcode=0x29, operandBytes=2)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]
        
        rVal = math.ceil(aBytes)
        rType = ">d" if mem.isFloatReg(self.regB) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"ceil {self.regA} and storing it in {self.regB}; ceil({aVal}) = {rVal}")
        mem.setGeneralRegBytes(self.regB, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

# Trig Instructions | 0x30-0x3F
class SIN_Instruction(Instruction):
    """
    `SIN REG_A REG_B`\n
    REG_A: The register holding the angle, in radians, to take the sin of\n
    REG_B: The register that will receive the` resulting value; If it's an integer register it will automatically round down\n
    Computes `sin(REG_A)` and then stores it in `REG_B`
    """
    def __init__(self, regA: REGISTER, regB: REGISTER):
        self.regA = regA
        self.regB = regB
        super().__init__(opcode=0x30, operandBytes=2)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]
        
        rVal = math.sin(aBytes)
        rType = ">d" if mem.isFloatReg(self.regB) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"sin {self.regA} and storing it in {self.regB}; sin({aVal}) = {rVal}")
        mem.setGeneralRegBytes(self.regB, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class COS_Instruction(Instruction):
    """
    `COS REG_A REG_B`\n
    REG_A: The register holding the angle, in radians, to take the cos of\n
    REG_B: The register that will receive the` resulting value; If it's an integer register it will automatically round down\n
    Computes `cos(REG_A)` and then stores it in `REG_B`
    """
    def __init__(self, regA: REGISTER, regB: REGISTER):
        self.regA = regA
        self.regB = regB
        super().__init__(opcode=0x31, operandBytes=2)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]
        
        rVal = math.cos(aBytes)
        rType = ">d" if mem.isFloatReg(self.regB) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"cos {self.regA} and storing it in {self.regB}; cos({aVal}) = {rVal}")
        mem.setGeneralRegBytes(self.regB, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class TAN_Instruction(Instruction):
    """
    `TAN REG_A REG_B`\n
    REG_A: The register holding the angle, in radians, to take the tan of\n
    REG_B: The register that will receive the` resulting value; If it's an integer register it will automatically round down\n
    Computes `tan(REG_A)` and then stores it in `REG_B`
    """
    def __init__(self, regA: REGISTER, regB: REGISTER):
        self.regA = regA
        self.regB = regB
        super().__init__(opcode=0x32, operandBytes=2)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]
        
        rVal = math.tan(aBytes)
        rType = ">d" if mem.isFloatReg(self.regB) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"tan {self.regA} and storing it in {self.regB}; tan({aVal}) = {rVal}")
        mem.setGeneralRegBytes(self.regB, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)
class ASIN_Instruction(Instruction):
    """
    `ASIN REG_A REG_B`\n
    REG_A: The float register holding the value to take the asin of\n
    REG_B: The register that will receive the` resulting value; If it's an integer register it will automatically round down\n
    Computes `asin(REG_A)` and then stores it in `REG_B`
    """
    def __init__(self, regA: REGISTER, regB: REGISTER):
        self.regA = regA
        self.regB = regB
        super().__init__(opcode=0x33, operandBytes=2)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]
        
        rVal = math.asin(aBytes)
        rType = ">d" if mem.isFloatReg(self.regB) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"asin {self.regA} and storing it in {self.regB}; asin({aVal}) = {rVal}")
        mem.setGeneralRegBytes(self.regB, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class ACOS_Instruction(Instruction):
    """
    `ACOS REG_A REG_B`\n
    REG_A: The float register holding the value to take the acos of\n
    REG_B: The register that will receive the` resulting value; If it's an integer register it will automatically round down\n
    Computes `acos(REG_A)` and then stores it in `REG_B`
    """
    def __init__(self, regA: REGISTER, regB: REGISTER):
        self.regA = regA
        self.regB = regB
        super().__init__(opcode=0x34, operandBytes=2)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]
        
        rVal = math.acos(aBytes)
        rType = ">d" if mem.isFloatReg(self.regB) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"acos {self.regA} and storing it in {self.regB}; acos({aVal}) = {rVal}")
        mem.setGeneralRegBytes(self.regB, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

class ATAN2_Instruction(Instruction):
    """
    `ATAN REG_A REG_B`\n
    REG_A: The float register holding the value to y value for atan\n
    REG_B: The float register holding the value to x value for atan\n
    REG_C: The register that will receive the` resulting value; If it's an integer register it will automatically round down\n
    Computes `atan2(REG_A, REG_B)` and then stores it in `REG_C`
    """
    def __init__(self, regA: REGISTER, regB: REGISTER, regC: REGISTER):
        self.regA = regA
        self.regB = regB
        self.regC = regC
        super().__init__(opcode=0x35, operandBytes=3)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]

        bBytes = mem.getGeneralRegBytes(self.regB)
        bType = ">d" if mem.isFloatReg(self.regB) else ">q"
        bVal = struct.unpack(bType, bBytes)[0]
        
        rVal = math.atan2(aVal, bVal)
        rType = ">d" if mem.isFloatReg(self.regC) else ">q"
        if rType == ">q": rVal = math.floor(rVal)
        rBytes = struct.pack(rType, rVal)

        print(f"atan {self.regA} and {self.regB} and storing it in {self.regC}; atan2({aVal}, {bVal}) = {rVal}")
        mem.setGeneralRegBytes(self.regC, rBytes)
        mem.zeroFlag = (rVal == 0)
        mem.negativeFlag = (rVal < 0)

# Branching Instructions | 0x40-0x4F
class JMZ_Instruction(Instruction):
    """
    `JMZ REG_A`\n
    REG_A: The register holding the new address if the jump condition is met\n
    Preforms `COPY REG_A PC` if the zero flag is set, else it preforms `NOP`
    """
    def __init__(self, regA: REGISTER):
        self.regA = regA
        super().__init__(opcode=0x40, operandBytes=1)
    
    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]

        zeroFlag = mem.zeroFlag

        msg = f"jmz, {zeroFlag=} ; "
        if zeroFlag:
            msg += f"setting ADDR to {aVal}/{hex(aVal)}/{aBytes}"
            mem.pcReg = aVal
        else:
            msg += "condition not met"
        print(msg)

class JMC_Instruction(Instruction):
    """
    `JMC REG_A`\n
    REG_A: The register holding the new address if the jump condition is met\n
    Preforms `COPY REG_A ADDR` if the carry flag is set, else it preforms `NOP`
    """
    def __init__(self, regA: REGISTER):
        self.regA = regA
        super().__init__(opcode=0x41, operandBytes=1)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]

        carryFlag = mem.carryFlag

        msg = f"jmz, {carryFlag=} ; "
        if carryFlag:
            msg += f"setting ADDR to {aVal}/{hex(aVal)}/{aBytes}"
            mem.pcReg = aVal
        else:
            msg += "condition not met"
        print(msg)

class JMN_Instruction(Instruction):
    """
    `JMN REG_A`\n
    REG_A: The register holding the new address if the jump condition is met\n
    Preforms `COPY REG_A ADDR` if the negative flag is set, else it preforms `NOP`
    """
    def __init__(self, regA: REGISTER):
        self.regA = regA
        super().__init__(opcode=0x42, operandBytes=1)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aType = ">d" if mem.isFloatReg(self.regA) else ">q"
        aVal = struct.unpack(aType, aBytes)[0]

        negativeFlag = mem.negativeFlag

        msg = f"jmz, {negativeFlag=} ; "
        if negativeFlag:
            msg += f"setting ADDR to {aVal}/{hex(aVal)}/{aBytes}"
            mem.pcReg = aVal
        else:
            msg += "condition not met"
        print(msg)

class JMP_Instruction(Instruction):
    """
    `JMP REG_A`\n
    REG_A: The register holding the new address\n
    Preforms `SET PC REG_A`
    """
    def __init__(self, regA: REGISTER):
        self.regA = regA
        super().__init__(opcode=0x43, operandBytes=1)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aVal = struct.unpack(">q", aBytes)[0]
        
        mem.pcReg = aVal

class PUSH_Instruction(Instruction):
    """
    `PUSH REG_A`\n
    REG_A: The register holding the value to be put onto the stack\n
    Increments the stack pointer and writes the bytes of the REG_A into the place the stack pointer is pointing towards
    """
    def __init__(self, regA: REGISTER):
        self.regA = regA
        super().__init__(opcode=0x44, operandBytes=1)

    def execute(self, mem):
        aBytes = mem.getGeneralRegBytes(self.regA)
        aVal = struct.unpack(">q", aBytes)[0]
        
        mem.spReg += 1
        mem.writeBytes( mem.STACK_START_ADDR + (mem.spReg*8), aBytes, 8 )
        
class POP_Instruction(Instruction):
    """
    `POP REG_A`\n
    REG_A: The register to receive the value popped from the stack\n
    Reads the bytes of the place the stack pointer is pointing towards into the REG_A and then decrements the stack pointer
    """
    def __init__(self, regA: REGISTER):
        self.regA = regA
        super().__init__(opcode=0x45, operandBytes=1)

    def execute(self, mem):
        stackBytes = mem.readBytes( mem.STACK_START_ADDR + (mem.spReg*8), 8, True )
        mem.setGeneralRegBytes(self.regA, stackBytes)
        mem.spReg -= 1
    


