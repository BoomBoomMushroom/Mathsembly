import instructions
import registers
from memory import Memory, RegisterNotFoundException

from manyterm import Terminal
from PIL import Image
import pygame
import time


class Screen:
    def __init__(self):
        self.bgColor = (128,128,128)
        self.maxWidth = 1023
        self.maxHeight = 511
        self.maxBpp = 31
        
        pygame.init()
        self.screen = pygame.display.set_mode((self.maxWidth, self.maxHeight))
    
    def close(self):
        pygame.quit()
    
    # https://stackoverflow.com/questions/25202092/pil-and-pygame-image
    def pilImageToSurface(self, pilImage: Image):
        return pygame.image.frombytes(pilImage.tobytes(), pilImage.size, pilImage.mode).convert()
    
    def displayImage(self, img: Image):
        w, h = img.size
        topLeft = ((self.maxWidth-w)//2, (self.maxHeight-h)//2)
        
        imgSurface = self.pilImageToSurface(img)
        self.screen.fill(self.bgColor)
        self.screen.blit(imgSurface, topLeft)

        pygame.display.flip()

class StopException(Exception): 
    def __init__(self, *args):
        super().__init__(*args)

def writeChunkOfMemory(memory: Memory, addr: int, data: bytes):
    for i in range(0, len(data)):
        memory.write(addr+i, data[i])

def readRegOperand(mem: Memory, address: int) -> tuple[str|int, int]:
    bytesRead = 1
    reg = registers.byteToRegister( mem.read(address) )
    if reg == "immediate":
        bytesRead = 9 # 8 bytes for the immediate, 1 for the reg type is immediate
        reg = mem.readBytes(address + 1, 8)
    return [reg, bytesRead]

def fetchAndDecode(mem: Memory) -> tuple[instructions.Instruction, int]:
    #print("PC", mem.pcReg, hex(mem.pcReg))
    opcode = mem.read( mem.pcReg )
    offset = 1
    
    i = None
    if opcode == 0x00: i = instructions.NOP_Instruction()
    elif opcode == 0x01:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.MOVE_Instruction(regA, regB)
    elif opcode == 0x02:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.COPY_Instruction(regA, regB)
    elif opcode == 0x03:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.CLTB_Instruction(regA, regB)
    elif opcode == 0x04: i = instructions.SHOW_Instruction()
    elif opcode == 0x05:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.PRINT_Instruction(regA, regB)
    elif opcode == 0x06: i = instructions.STOP_Instruction()
    
    elif opcode == 0x10:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.NOT_Instruction(regA, regB)
    elif opcode == 0x11:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regC, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.AND_Instruction(regA, regB, regC)
    elif opcode == 0x12:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regC, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.OR_Instruction(regA, regB, regC)
    elif opcode == 0x13:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regC, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.XOR_Instruction(regA, regB, regC)
    
    elif opcode == 0x20:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regC, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.ADD_Instruction(regA, regB, regC)
    elif opcode == 0x21:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regC, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.SUB_Instruction(regA, regB, regC)
    elif opcode == 0x22:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regC, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.MULT_Instruction(regA, regB, regC)
    elif opcode == 0x23:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regC, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.DIV_Instruction(regA, regB, regC)
    elif opcode == 0x24:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.SQRT_Instruction(regA, regB)
    elif opcode == 0x25:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regC, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.POW_Instruction(regA, regB, regC)
    elif opcode == 0x26:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.LN_Instruction(regA, regB)
    elif opcode == 0x27:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.ROUND_Instruction(regA, regB)
    elif opcode == 0x28:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.FLOOR_Instruction(regA, regB)
    elif opcode == 0x29:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.CEIL_Instruction(regA, regB)
    
    elif opcode == 0x30:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.SIN_Instruction(regA, regB)
    elif opcode == 0x31:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.COS_Instruction(regA, regB)
    elif opcode == 0x32:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.TAN_Instruction(regA, regB)
    elif opcode == 0x33:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.ASIN_Instruction(regA, regB)
    elif opcode == 0x34:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.ACOS_Instruction(regA, regB)
    elif opcode == 0x35:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regB, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        regC, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.ATAN2_Instruction(regA, regB, regC)
    
    elif opcode == 0x40:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.JMZ_Instruction(regA)
    elif opcode == 0x41:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.JMC_Instruction(regA)
    elif opcode == 0x42:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.JMN_Instruction(regA)
    elif opcode == 0x43:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.JMP_Instruction(regA)
    elif opcode == 0x44:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.PUSH_Instruction(regA)
    elif opcode == 0x45:
        regA, _ = readRegOperand(mem, mem.pcReg + offset)
        offset += _
        i = instructions.POP_Instruction(regA)
    
    else: raise Exception(f"Unknown opcode {hex(opcode)}!!")
    
    return i, offset

def renderScreen(mem: Memory, screen: Screen):
    width, height, bpp = mem.videoWidth, mem.videoHeight, mem.videoBBP
    if width==0 or height==0 or bpp==0:
        raise Exception(f"One or more video parameters are zero! {width=} {height=} {bpp=}")
    
    imgMode = ""
    if bpp == 1: imgMode = "1" # 1 bit per pixel stored with 1 pixel per byte
    elif bpp == 8: imgMode = "L" # 8 bit grayscale
    elif bpp == 24: imgMode = "RGB" # 24 bit colors, each channel is 1 byte
    
    imgBytes = mem.readBytes( mem.VIDEO_MEM_ADDR, (width * height * bpp)//8, readAsBytes=True )
    img = Image.frombytes(imgMode, (width, height), imgBytes)
    
    #print(imgBytes, width, height, bpp, imgMode)
    
    imgForPygame = img.convert("RGB")
    screen.displayImage(imgForPygame)

def execute(mem: Memory, i: instructions.Instruction, outTerminal: Terminal, screen: Screen) -> int:
    isNop = False
    isNop = type(i) == instructions.NOP_Instruction
    
    if isNop==False: print(f"executing {i} - pc={hex(mem.pcReg)}")
    #if isNop: return -1
    
    if type(i) == instructions.STOP_Instruction: return 0
    # 0 = success
    # -1 = terminate the program
    if type(i) == instructions.SHOW_Instruction:
        renderScreen(mem, screen)
        return # return nothing so we don't accidentally end the program
    
    
    out = i.execute(mem)
    if type(i) == instructions.PRINT_Instruction:
        outTerminal.print(out)
    

def runProgram(machineCode: bytes, outTerminal: Terminal, screen: Screen):
    global memory
    if memory == None: memory = Memory()
    
    memory.initMemory()
    writeChunkOfMemory(memory, 0x0E1970, machineCode) # load the program into memory
    memory.dumpMemory("./dumps/afterLoad.bin")
    
    while True:
        i, bytesRead = fetchAndDecode(memory)
        memory.pcReg += bytesRead
        response: int = execute(memory, i, outTerminal, screen)
        #time.sleep(0.01)
        
        if response != None:
            print(f"Program exited w/ status code {response}")
            raise StopException("Halt.")


memory: Memory = None

if __name__ == "__main__":
    machineCode = bytes()
    with open("./program.mc", "rb") as f: machineCode = f.read()
    
    outTerminal: Terminal = Terminal()
    screen: Screen = Screen()
    
    try:
        runProgram(machineCode, outTerminal, screen)
    except Exception as e:
        doRaise = True
        if type(e) == StopException:
            doRaise = False
            input("Press enter to exit...")
        
        outTerminal.close()
        screen.close()
        memory.dumpMemory("./dumps/terminate.bin")
        
        if doRaise: raise e


