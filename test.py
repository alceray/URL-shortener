BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
import string
from math import floor

def encode(id, base = BASE62):
    baselen = len(base)
    encoded_id = ""
    while id:
        encoded_id = base[id % baselen] + encoded_id
        id //= baselen
        #print(id)
    return encoded_id
def toBase62(num, b = 62):
    if b <= 0 or b > 62:
        return 0
    base = string.digits + string.ascii_lowercase + string.ascii_uppercase
    r = num % b
    res = base[r];
    q = floor(num / b)
    while q:
        r = q % b
        q = floor(q / b)
        res = base[int(r)] + res
    return res
def toBase10(num, b = 62):
    base = string.digits + string.ascii_lowercase + string.ascii_uppercase
    limit = len(num)
    res = 0
    for i in range(limit):
        res = b * res + base.find(num[i])
    return res
def decode(code, base = BASE62):
    baselen = len(base)
    codelen = len(code)
    id = 0
    for i in range(codelen):
        id += base.find(code[i]) * (baselen ** (codelen - i - 1))
    return id

#print(encode(3))
print(encode(8))
print(toBase62(7159))
print(decode('1fA'))
print(toBase10('1fA'))
