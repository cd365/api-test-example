import hmac
import hashlib
import time
import base64
import struct


def generate_totp(secret, interval=30, digits=6):
    # Decode the Base32 key
    key = base64.b32decode(secret, casefold=True)

    # Get the current timestamp and calculate the time step
    timestamp = int(time.time()) // interval

    # Convert time steps to bytes
    msg = struct.pack(">Q", timestamp)

    # Generate hash using HMAC-SHA1
    hash_result = hmac.new(key, msg, hashlib.sha1).digest()

    # Dynamic truncation
    offset = hash_result[-1] & 0x0F
    binary = struct.unpack(">I", hash_result[offset : offset + 4])[0] & 0x7FFFFFFF

    # Generate a verification code with a specified number of digits
    code = binary % (10**digits)
    return f"{code:0{digits}d}"


# # Example
# secret = "U5WM5NKSC757E5A6"
# print(f"current verification code: {generate_totp(secret)}")
