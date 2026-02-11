import struct
import os

CHUNK_PATH = r"D:\Steam\steamapps\common\Monster Hunter World\chunk\chunkG0.bin"

with open(CHUNK_PATH, "rb") as f:
    # Read header
    magic = f.read(4)
    print(f"Magic: {magic}")
    
    # Read version?
    version = struct.unpack("<I", f.read(4))[0]
    print(f"Version: {version}")
    
    # Read counts
    count1 = struct.unpack("<Q", f.read(8))[0]
    count2 = struct.unpack("<Q", f.read(8))[0]
    print(f"Count1: {count1} (0x{count1:x})")
    print(f"Count2: {count2} (0x{count2:x})")
    
    # Read next 8 bytes
    offset = struct.unpack("<Q", f.read(8))[0]
    print(f"Offset/Other: {offset} (0x{offset:x})")
