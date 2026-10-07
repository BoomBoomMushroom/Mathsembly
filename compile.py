import struct

import instructions
import registers
START_MEMORY_LOCATION = 0x0E1970

class InstructionList:
    def __init__(self, start:list[instructions.Instruction]=[]):
        self.list: list[instructions.Instruction] = start
        self.ignoreList: list[instructions.Instruction] = [
            instructions.PlaceInMemory_PseudoInstruction,
            instructions.AddressReference_PseudoInstruction
        ]
    def append(self, instruction: instructions.Instruction):
        self.list.append(instruction)
    def __getitem__(self, index) -> instructions.Instruction:
        return self.list[index]
    def __len__(self):
        c = 0
        for i in self.list:
            if type(i) in self.ignoreList: continue
            c += 1
        return c

def loadSourceCode(path):
    src = ""
    with open(path, "r") as f: src = f.read()
    return src

def parseLiteral(string, ANDValue=None):
    try:
        v = int(string, base=0) # base=0 means to interpret it however
        if ANDValue != None: v &= ANDValue
    except ValueError as e:
        v = float(string)
    
    return v 

def turnIntoInstructionsList(src: str) -> list[instructions.Instruction]:
    #out: InstructionList = InstructionList()
    out: list[instructions.Instruction] = []
    
    lines = src.splitlines()
    for l in lines:
        l = l.strip()
        line = l.split(";")[0]
        if len(line) == 0: continue
        splits = line.split(" ")
        iName = splits[0]
        
        if iName == "#":
            # place memory in specific region
            loc = parseLiteral(splits[1], 0xFFFFFF) # make sure it's at most 3 bytes
            out.append( instructions.PlaceInMemory_PseudoInstruction(loc) )
        elif iName.startswith("!"):
            refName = line[1:]
            if refName.endswith(":"): refName = refName[:-1] # remove a trailing ":"
            refName = refName.strip()
            out.append( instructions.AddressReference_PseudoInstruction(refName) )
        
        elif iName == "NOP": out.append( instructions.NOP_Instruction() )
        elif iName == "MOVE": out.append( instructions.MOVE_Instruction(splits[1],splits[2]) )
        elif iName == "COPY": out.append( instructions.COPY_Instruction(splits[1],splits[2]) )
        elif iName == "CLTB": out.append( instructions.CLTB_Instruction(splits[1],splits[2]) )
        elif iName == "SHOW": out.append( instructions.SHOW_Instruction() )
        elif iName == "PRINT": out.append( instructions.PRINT_Instruction(splits[1], splits[2]) )
        elif iName == "STOP": out.append( instructions.STOP_Instruction() )
        
        elif iName == "NOT": out.append( instructions.NOT_Instruction(splits[1],splits[2]) )
        elif iName == "AND": out.append( instructions.AND_Instruction(splits[1],splits[2],splits[3]) )
        elif iName == "OR": out.append( instructions.OR_Instruction(splits[1],splits[2],splits[3]) )
        elif iName == "XOR": out.append( instructions.XOR_Instruction(splits[1],splits[2],splits[3]) )
        elif iName == "ADD": out.append( instructions.ADD_Instruction(splits[1],splits[2],splits[3]) )
        elif iName == "SUB": out.append( instructions.SUB_Instruction(splits[1],splits[2],splits[3]) )
        elif iName == "MULT": out.append( instructions.MULT_Instruction(splits[1],splits[2],splits[3]) )
        elif iName == "DIV": out.append( instructions.DIV_Instruction(splits[1],splits[2],splits[3]) )
        elif iName == "SQRT": out.append( instructions.SQRT_Instruction(splits[1],splits[2]) )
        elif iName == "POW": out.append( instructions.POW_Instruction(splits[1],splits[2],splits[3]) )
        elif iName == "LN": out.append( instructions.LN_Instruction(splits[1],splits[2]) )
        elif iName == "ROUND": out.append( instructions.ROUND_Instruction(splits[1],splits[2]) )
        elif iName == "FLOOR": out.append( instructions.FLOOR_Instruction(splits[1],splits[2]) )
        elif iName == "CEIL": out.append( instructions.CEIL_Instruction(splits[1],splits[2]) )
        
        elif iName == "SIN": out.append( instructions.SIN_Instruction(splits[1],splits[2]) )
        elif iName == "COS": out.append( instructions.COS_Instruction(splits[1],splits[2]) )
        elif iName == "TAN": out.append( instructions.TAN_Instruction(splits[1],splits[2]) )
        elif iName == "ASIN": out.append( instructions.ASIN_Instruction(splits[1],splits[2]) )
        elif iName == "ACOS": out.append( instructions.ACOS_Instruction(splits[1],splits[2]) )
        elif iName == "ATAN": out.append( instructions.ATAN2_Instruction(splits[1],splits[2],splits[3]) )

        elif iName == "JMZ": out.append( instructions.JMZ_Instruction(splits[1]) )
        elif iName == "JMC": out.append( instructions.JMC_Instruction(splits[1]) )
        elif iName == "JMN": out.append( instructions.JMN_Instruction(splits[1]) )
        elif iName == "JMP": out.append( instructions.JMP_Instruction(splits[1]) )
        elif iName == "PUSH": out.append( instructions.PUSH_Instruction(splits[1]) )
        elif iName == "POP": out.append( instructions.POP_Instruction(splits[1]) )
        elif iName == "": pass # this ain't an instruction 
        else:
            raise Exception(f"Instruction not found! Trying to find instruction \"{iName}\"")

    return out

def instructionsToMachineCode(instructs: list[instructions.Instruction]) -> bytes:
    machineCode = bytearray([0x00] * 0xFFFFFF)
    minAddrBound = START_MEMORY_LOCATION
    maxAddrBound = START_MEMORY_LOCATION
    addr = START_MEMORY_LOCATION
    
    references: dict[str, int] = {} # key, value = referenceName, addressPointed
    toReplace: list[tuple[int, str]] = [] # each tuple is (addressToReplace, referenceName)
    
    for i in instructs:        
        minAddrBound = min(minAddrBound, addr)
        maxAddrBound = max(maxAddrBound, addr)
        if type(i) == instructions.PlaceInMemory_PseudoInstruction:
            addr = i.location
            continue
        elif type(i) == instructions.AddressReference_PseudoInstruction:
            if i.name in references:
                raise KeyError(f"Reference with the same name already exists! name=\"{i.name}\"")
            references[i.name] = addr
            continue
        
        machineCode[addr] = i.opcode
        addr += 1
        for reg in ["regA", "regB", "regC"]:
            if hasattr(i, reg):
                regName = getattr(i, reg)
                
                literalVal = None
                try:
                    literalVal = int(regName, base=0)
                    if literalVal > 0xFFFFFFFFFFFFFFFF: raise Exception("Immediate value exceeds 0xFFFFFFFFFFFFFFFF (8 bytes)!")
                except:
                    try:
                        literalVal = float(regName)
                    except: pass
                
                if registers.isRegister(regName) == False and literalVal == None:
                    literalVal = 0x00000000_00000000
                    toReplace.append( (addr+1, regName) )
                
                if literalVal != None:
                    machineCode[addr] = registers.registerToByte("immediate")
                    addr += 1
                    
                    if type(literalVal) == float:
                        literalVal = struct.unpack(">q", struct.pack(">d", literalVal))[0] # convert float to int preserving its bytes
                    bytesLeft = 8
                    while bytesLeft > 0:
                        b = (literalVal >> (8*(bytesLeft-1))) & 0xFF
                        machineCode[addr] = b
                        bytesLeft -= 1
                        addr += 1
                else:
                    machineCode[addr] = registers.registerToByte(regName)
                    addr += 1
        
        if hasattr(i, "immediate"):
            iVal = i.immediate
            if type(iVal) == str:
                try:
                    iVal = int(iVal, base=0)
                    if iVal > 0xFFFFFFFFFFFFFFFF: raise Exception("Immediate value exceeds 0xFFFFFFFFFFFFFFFF (8 bytes)!")
                except:
                    iVal = float(iVal)
            
            if type(iVal) == float:
                iVal = struct.unpack(">q", struct.pack(">d", iVal))[0] # convert float to int preserving its bytes
            
            while i.immediateLengthBytes > 0:
                b = (iVal >> (8*(i.immediateLengthBytes-1))) & 0xFF
                machineCode[addr] = b
                i.immediateLengthBytes -= 1
                addr += 1
    
    # put in the references
    for replaceAddr, refName in toReplace:
        setAddr = references.get(refName, None)
        if setAddr == None:
            raise Exception(f"Reference not found! Make sure it is defined! {refName=} {references=}")
        
        bytesLeft = 8
        while bytesLeft > 0:
            b = (setAddr >> (8*(bytesLeft-1))) & 0xFF
            machineCode[replaceAddr] = b
            bytesLeft -= 1
            replaceAddr += 1
    
    minAddrBound = min(minAddrBound, addr)
    maxAddrBound = max(maxAddrBound, addr)
    machineCode = machineCode[minAddrBound:maxAddrBound+1]
    
    #print(hex(minAddrBound), hex(maxAddrBound))
    return machineCode


if __name__ == "__main__":
    fileName = input("Enter source file name (must be placed in ./examplePrograms): ")
    if fileName == "": fileName = "bounce.masm"
    programSourceCode = loadSourceCode(f"./examplePrograms/{fileName}")
    programInstructions: list[instructions.Instruction] = turnIntoInstructionsList(programSourceCode)
    for a in programInstructions: print("\t", a)
    machineCode = instructionsToMachineCode(programInstructions)
    with open("./program.mc", "wb") as f: f.write(machineCode)
    print("Wrote compiled program to `./program.mc`")

