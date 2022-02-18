# upper 2 bits of overy response are checkbits, the order is: first K1, then K0
# K0 = even
# K1 = odd

# high byte is first 8, low byte is last 8. Received in low/high order.



def testit():
    # diff is 4000 in hex, 16384 in dec,
    response = 0x61AB
    result = 0x21AB
    assert check_checksum(response)
    assert get_result(response) == result

def str_to_hex(thestring):
        try:
            result = int(thestring, 16)
        except Exception as e:
            print("Error with result:", thestring)
            return -1
        return result

def h2b(hexin):
    return f"{hexin:#018b}" # includes the 0b prefix so 16 + 2

def bytes_to_word(lsb, msb):
    return (msb<<8)+lsb

def get_result(full_response):
    mask = 0x3FFF # 0011111111111111
    return full_response & mask


def check_checksum(word):
    """
    Odd:   K1 = !(H5^H3^H1^L7^L5^L3^L1)
    Even:  K0 = !(H4^H2^H0^L6^L4^L2^L0)

    From the above response 0x61AB:
    Odd:   0 = !(1^0^0^1^1^1^1) = correct
    Even:  1 = !(0^0^1^0^0^0^1) = correct

    example:
        HIGH     LOW
        01100001 10101011
        76543210 76543210
        FEDCBA98 76543210

        H5^H3^H1^L7^L5^L3^L1
    K1: 13 ^ 11 ^ 9 ^ 7 ^ 5 ^ 3 ^ 1

        H4^H2^H0^L6^L4^L2^L0
    K0: 12 ^ 10 ^ 8 ^ 6 ^ 4 ^ 2 ^ 0

    """
    k1 = word >> 15 & 1
    k0 = word >> 14 & 1
    k1_result = not (word>>13&1 ^ word>>11&1 ^ word>>9&1 ^ word>>7&1 ^ word>>5&1 ^ word>>3&1 ^ word>>1&1)
    k0_result = not (word>>12&1 ^ word>>10&1 ^ word>>8&1 ^ word>>6&1 ^ word>>4&1 ^ word>>2&1 ^ word>>0&1)
    correct = k1_result == k1 and k0_result == k0
    #print(k1, k1_result, k0, k0_result, correct)
    return correct

if __name__ == '__main__':
    import sys
    print("Give the two hex bytes and we'll check the checksum")
    msb, lsb = sys.argv[1], sys.argv[2]
    print(f"input: {msb} and {lsb}")
    msbi = str_to_hex(msb)
    lsbi = str_to_hex(lsb)
    print(f"string to hex result: {msbi} and {lsbi}")
    words = bytes_to_word(msbi, lsbi)
    print(f"word: {words}")
    print(f"checksum: {check_checksum(words)}")
