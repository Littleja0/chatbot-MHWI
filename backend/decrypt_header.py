from Crypto.Cipher import Blowfish
import struct

CHUNK_PATH = r"D:\Steam\steamapps\common\Monster Hunter World\chunk\chunkG0.bin"
KEY = b"TR5Rr2X(9L<2.a_1"

with open(CHUNK_PATH, "rb") as f:
    # Read first 256 bytes
    data = f.read(256)

# Try decrypting from byte 0
cipher = Blowfish.new(KEY, Blowfish.MODE_ECB)

try:
    decrypted = cipher.decrypt(data)
    print("=== Decrypted from byte 0 ===")
    print(f"Magic?: {decrypted[:4]}")
    print(f"Hex: {decrypted[:64].hex()}")
except Exception as e:
    print(f"Error decrypting from 0: {e}")

# Try decrypting from byte 4 (skip MAGIC)
cipher = Blowfish.new(KEY, Blowfish.MODE_ECB)
try:
    decrypted_skip = cipher.decrypt(data[4:])
    print("\n=== Decrypted from byte 4 ===")
    print(f"Hex: {decrypted_skip[:64].hex()}")
except Exception as e:
    print(f"Error decrypting from 4: {e}")
