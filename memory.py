import registers
import struct

class RegisterNotFoundException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

class Memory:
    def __init__(self):
        self.memory = bytearray()
        self.ZERO_ADDR = 0x000000
        self.PC_ADDR = 0x000008
        self.SP_ADDR = 0x00000B
        self.ADDR_ADDR = 0x00000C
        self.FLAGS_ADDR = 0x00000F
        self.INT_REG_START_ADDR = 0x000010
        self.FLOAT_REG_START_ADDR = 0x000110
        self.STACK_START_ADDR = 0x000210
        self.VIDEO_CONFIG_ADDR = 0x000960
        self.VIDEO_MEM_ADDR = 0x000970
    
    def initMemory(self):
        self.memory = bytearray([0x00] * 0xFFFFFF)
        self.pcReg = 0x0E1970
    
    def dumpMemory(self, filePath):
        with open(filePath, "wb") as f: f.write(self.memory)
    
    def read(self, addr: int): return self.memory[addr]
    def readBytes(self, addr, readLength, readAsBytes=False, isSigned=True):
        out = bytearray()
        for i in range(0, readLength):
            out.append( self.read(addr + i) )
        
        if readAsBytes == False: out = int.from_bytes(out, byteorder="big", signed=isSigned)
        return out
    
    def write(self, addr, value): self.memory[addr] = value
    def writeBytes(self, addr, value: bytes|int, writeLength, isSigned=True):
        if type(value) == int:
            print(hex(addr), value, hex(value), writeLength, isSigned)
            value = value.to_bytes(writeLength, byteorder="big", signed=isSigned)
        
        for i in range(0, writeLength):
            self.write( addr, value[i] )
            addr += 1
    
    @property
    def videoWidth(self) -> int: return self.readBytes(self.VIDEO_CONFIG_ADDR, 2) >> 6 # make the width 10 bits
    @property
    def videoHeight(self) -> int: return ((self.readBytes(self.VIDEO_CONFIG_ADDR+1, 2) & 0b00111111_11100000) >> 5)
    @property
    def videoBBP(self) -> int: return (self.readBytes(self.VIDEO_CONFIG_ADDR+2, 1) & 0b00011111)
    
    @property
    def zeroReg(self) -> int: return 0
    @zeroReg.setter
    def zeroReg(self, val: int): pass # writing does nothing to the zero register
    
    @property
    def pcReg(self) -> int: return self.readBytes(self.PC_ADDR, 3, isSigned=False)
    @pcReg.setter
    def pcReg(self, val: int): self.writeBytes(self.PC_ADDR, val, 3, isSigned=False)
 
    @property
    def spReg(self) -> int: return self.readBytes(self.SP_ADDR, 1, isSigned=False)
    @spReg.setter
    def spReg(self, val: int): self.writeBytes(self.SP_ADDR, val, 1, isSigned=False)
    
    @property
    def addrReg(self) -> int: return self.readBytes(self.ADDR_ADDR, 3, isSigned=False)
    @addrReg.setter
    def addrReg(self, val: int): self.writeBytes(self.ADDR_ADDR, val, 3, isSigned=False)
    
    @property
    def regM(self) -> int: return self.readBytes(self.addrReg, 8)
    @regM.setter
    def regM(self, val: int): self.writeBytes(self.addrReg, val, 8)
    
    @property
    def flagsReg(self) -> int: return self.readBytes(self.FLAGS_ADDR, 1, isSigned=False)
    @flagsReg.setter
    def flagsReg(self, val: int): self.writeBytes(self.FLAGS_ADDR, val, 1, isSigned=False)
    
    @property
    def zeroFlag(self) -> bool: return (self.flagsReg & 0b1) == 0b1
    @zeroFlag.setter
    def zeroFlag(self, val: bool):
        self.flagsReg &= 0b11111110
        self.flagsReg |= (0b1 if val else 0b0)
    
    @property
    def carryFlag(self) -> bool: return (self.flagsReg & 0b10) == 0b10
    @carryFlag.setter
    def carryFlag(self, val: bool):
        self.flagsReg &= 0b11111101
        self.flagsReg |= (0b10 if val else 0b00)
    
    @property
    def negativeFlag(self) -> bool: return (self.flagsReg & 0b100) == 0b100
    @negativeFlag.setter
    def negativeFlag(self, val: bool):
        self.flagsReg &= 0b11111011
        self.flagsReg |= (0b100 if val else 0b000)
    
    def isImmediateReg(self, regName: registers.REGISTER) -> bool:
        return type(regName) == int or type(regName) == float
    def isSpecialReg(self, regName: registers.REGISTER) -> bool:
        if self.isImmediateReg(regName): return False
        return regName in ["ZERO", "PC", "SP", "ADDR", "FLAGS", "REG_M"]
    def isIntegerReg(self, regName: registers.REGISTER) -> bool:
        if self.isImmediateReg(regName) or self.isSpecialReg(regName): return False
        return "I" in regName
    def isFloatReg(self, regName: registers.REGISTER) -> bool:
        if self.isImmediateReg(regName) or self.isSpecialReg(regName) or self.isIntegerReg(regName): return False
        return "F" in regName
    
    def getIntegerReg(self, regN) -> int: return struct.unpack(">q", self.readBytes(self.INT_REG_START_ADDR + 8*regN, 8, readAsBytes=True))[0]
    def setIntegerReg(self, regN, val: int): self.writeBytes(self.INT_REG_START_ADDR + 8*regN, struct.pack(">q", val), 8)

    def getFloatReg(self, regN) -> float: return struct.unpack(">d", self.readBytes(self.FLOAT_REG_START_ADDR + 8*regN, 8, readAsBytes=True))[0]
    def setFloatReg(self, regN, val: float): self.writeBytes(self.FLOAT_REG_START_ADDR + 8*regN, struct.pack(">d", val), 8)

    def getGeneralRegBytes(self, regName: registers.REGISTER) -> bytes:
        val = 0
        if type(regName) == int:
            val = regName
        elif type(regName) == float:
            val = struct.unpack(">q", struct.pack(">d", val))[0] # convert it to an int so we can get the bytes cleanly
        elif regName == "ZERO": val = self.zeroReg
        elif regName == "PC": val = self.pcReg
        elif regName == "SP": val = self.spReg
        elif regName == "ADDR": val = self.addrReg
        elif regName == "FLAGS": val = self.flagsReg
        elif regName == "REG_M": val = self.regM
        else:
            regNum = int( regName.split("_")[1].replace("I","").replace("F", "") )
            if "I" in regName: val = self.getIntegerReg(regNum)
            elif "F" in regName:
                val = self.getFloatReg(regNum)
                val = struct.unpack(">q", struct.pack(">d", val))[0] # convert it to an int so we can get the bytes cleanly
            else:
                raise RegisterNotFoundException(f"Register not found! {regName=}")   
        
        #print(regName, self.addrReg, val, hex(val))
        return struct.pack(">q", val) # return the bytes

    def setGeneralRegBytes(self, regName: registers.REGISTER, value: bytes):
        valInt = struct.unpack(">q", value)[0] # use >q since nothing will be more than 8 bytes
        
        if self.isImmediateReg(regName):
            raise Exception(f"Cannot assign a value to a literal! {regName=} {value=}")
        elif regName == "ZERO": self.zeroReg = valInt & 0xFFFFFFFF_FFFFFFFF # 8 bytes
        elif regName == "PC": self.pcReg = valInt & 0xFFFFFF
        elif regName == "SP": self.spReg = valInt & 0xFF
        elif regName == "ADDR": self.addrReg = valInt & 0xFFFFFF
        elif regName == "FLAGS": self.flagsReg = valInt & 0xFF
        #elif regName == "REG_M": self.regM = valInt & 0xFFFFFFFF_FFFFFFFF
        elif regName == "REG_M": self.regM = value # REG_M should be written as bytes typically
        else:
            regNum: int = int( regName.split("_")[1].replace("I","").replace("F", "") )
            if self.isIntegerReg(regName):
                self.setIntegerReg(regNum, struct.unpack(">q", value)[0])
            elif self.isFloatReg(regName):
                self.setFloatReg(regNum, struct.unpack(">d", value)[0])
            else:
                raise Exception(f"Register not found! {regName=}")

