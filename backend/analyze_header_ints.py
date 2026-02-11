import struct
import os

CHUNK_PATH = r"D:\Steam\steamapps\common\Monster Hunter World\chunk\chunkG0.bin"

with open(CHUNK_PATH, "rb") as f:
    f.read(8) # Skip Magic + Version
    
    print("Reading 4-byte integers after version:")
    for i in range(16):
        val = struct.unpack("<I", f.read(4))[0]
        print(f"Int {i}: {val} (0x{val:x})")
