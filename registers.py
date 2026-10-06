from typing import Literal

REGISTER_LIST = [
    "ZERO", "PC", "SP", "ADDR", "FLAGS", "REG_M",
    "REG_0I", "REG_1I", "REG_2I", "REG_3I", "REG_4I", "REG_5I", "REG_6I", "REG_7I", "REG_8I", "REG_9I", "REG_10I", "REG_11I", "REG_12I", "REG_13I", "REG_14I", "REG_15I", "REG_16I", "REG_17I", "REG_18I", "REG_19I", "REG_20I", "REG_21I", "REG_22I", "REG_23I", "REG_24I", "REG_25I", "REG_26I", "REG_27I", "REG_28I", "REG_29I", "REG_30I", "REG_31I",
    "REG_0F", "REG_1F", "REG_2F", "REG_3F", "REG_4F", "REG_5F", "REG_6F", "REG_7F", "REG_8F", "REG_9F", "REG_10F", "REG_11F", "REG_12F", "REG_13F", "REG_14F", "REG_15F", "REG_16F", "REG_17F", "REG_18F", "REG_19F", "REG_20F", "REG_21F", "REG_22F", "REG_23F", "REG_24F", "REG_25F", "REG_26F", "REG_27F", "REG_28F", "REG_29F", "REG_30F", "REG_31F",
    "immediate",
]
REGISTER = Literal[
    "ZERO", "PC", "SP", "ADDR", "FLAGS", "REG_M",
    "REG_0I", "REG_1I", "REG_2I", "REG_3I", "REG_4I", "REG_5I", "REG_6I", "REG_7I", "REG_8I", "REG_9I", "REG_10I", "REG_11I", "REG_12I", "REG_13I", "REG_14I", "REG_15I", "REG_16I", "REG_17I", "REG_18I", "REG_19I", "REG_20I", "REG_21I", "REG_22I", "REG_23I", "REG_24I", "REG_25I", "REG_26I", "REG_27I", "REG_28I", "REG_29I", "REG_30I", "REG_31I",
    "REG_0F", "REG_1F", "REG_2F", "REG_3F", "REG_4F", "REG_5F", "REG_6F", "REG_7F", "REG_8F", "REG_9F", "REG_10F", "REG_11F", "REG_12F", "REG_13F", "REG_14F", "REG_15F", "REG_16F", "REG_17F", "REG_18F", "REG_19F", "REG_20F", "REG_21F", "REG_22F", "REG_23F", "REG_24F", "REG_25F", "REG_26F", "REG_27F", "REG_28F", "REG_29F", "REG_30F", "REG_31F",
    "immediate",
]

def isRegister(register: REGISTER) -> bool: return register in REGISTER_LIST
def registerToByte(register: REGISTER) -> int:
    try:
        return REGISTER_LIST.index(register)
    except:
        raise Exception(f"Register \"{register}\" not found!!")
def byteToRegister(num: int) -> REGISTER: return REGISTER_LIST[num]

