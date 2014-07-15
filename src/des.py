#!/usr/bin/env python

'''
DES
Will Farmer


Throughout this code there are a couple spots where a table is used to swap
bits around. These tables create new bitstrings from the locations given in the
table from an old bitstring. I know I use the term table, but in reality it is
a list.
'''

import sys
import argparse

total_number_of_rounds = 33

def main():
    args   = get_args()
    blocks = clean(args.message)                  # Get message blocks
    keys   = key_schedule(args.key, args.simple)  # Get 16 keys
    final  = encode(blocks, keys, args.decrypt)   # Encode
    if args.bits:
        for byte in final:
            print '%08d' %int(bin(ord(byte))[2:]),
    else:
        print final

def encode(blocks, keys, decrypt):
    '''
    Core Algorithm
    :param list<string>: blocks
    :param class: keys
    :param bool: decrypt
    '''
    final  = ''
    keys.gen_keys()                                          # Create all of our keys
    if decrypt:
            keys.subkeys.reverse()
    for block in blocks:                                     # Iterate through all the blocks
        bitstring        = string_to_bits(block)             # Convert each block to its corresponding bitstring
        permutated_block = initial_permutation(bitstring)    # Perform the initial permutation
        half1, half2     = create_halves(permutated_block)   # Split each 64 bit block into two 32 bit halves
        half2_old        = None
        for roundnum in range(total_number_of_rounds):                           # Perform this 16 times
            half2_old = half2                                # We need this value later
            half2     = feistel(half2, keys, roundnum).final # Turn half2 into it's fiestel equivalent
            half1     = XOR_bitstring(half1, half2)          # Half1 now equals half1^half2
            half2     = half1                                # Turn half2 into half1
            half1     = half2_old                            # Turn half1 into the old half2
        joined = half2 + half1                               # After the rounds, join them together
        last_permute = final_permutation(joined)             # Perform the final permutation
        byte = [last_permute[x:x + 8] for x in range(0,
                    len(last_permute), 8)]                   # Take 8 bit chunks
        for item in byte:                                    # Convert back to ASCII
            final += chr(int(item, 2))
    return final

def create_halves(permutated_block):
    '''
    Split our block into two halves
    :param bitstring: permutated_block
    '''
    half1 = permutated_block[0:len(permutated_block) / 2]
    half2 = permutated_block[len(permutated_block) / 2:len(permutated_block)]
    return half1, half2

def string_to_bits(block):
    '''
    Converts a string to a bitstring
    :param string: block
    '''
    bitstring = ''
    for char in block:
        bitstring += '%08d' %int(bin(ord(char))[2:])
    return bitstring

def rotate_bitstring(bitstring, shift):
    '''
    Performs the classic << but on a user string
    :param string: bitstring
    :param int: shift
    '''
    final = ''
    for number in range(len(bitstring)):
        cursor = (number + shift) % len(bitstring)
        final += bitstring[cursor]
    return final

def table_swap(block, table):
    '''
    With a given input of a bitstring and swap table, this generates a new
    bitstring from the locations given by the table. If the table has a number
    '23' in position 4, it means the new bitstring has the old bitstring's
    value at position 23 in position 4.
    :param string: block
    :param list: table
    '''
    swapped = ''
    for item in table:
        position = item - 1
        swapped += block[position]
    return swapped

def XOR_bitstring(a_bits, b_bits):
    '''
    Performs ^ on two bitstrings. Implemented my own to deal with bitstrings
    :param bitstring: a_bits
    :param bitstring: b_bits
    '''
    a     = list(a_bits)
    b     = list(b_bits)
    final = ''
    assert(len(a) == len(b))
    for number in range(len(a)):
        a_int = int(a[number])
        b_int = int(b[number])
        xor = a_int ^ b_int
        if xor:
            final += '1'
        else:
            final += '0'
    return final


def initial_permutation(bitstring):
    '''
    Initial permutation. Not strictly necessary, but when this algorithm was
    developed it made their lives easier.
    :param bitstring: bitstring
    '''
    table=[58, 50, 42, 34, 26, 18, 10, 2,
            60, 52, 44, 36, 28, 20, 12, 4,
            62, 54, 46, 38, 30, 22, 14, 6,
            64, 56, 48, 40, 32, 24, 16, 8,
            57, 49, 41, 33, 25, 17, 9, 1,
            59, 51, 43, 35, 27, 19, 11, 3,
            61, 53, 45, 37, 29, 21, 13, 5,
            63, 55, 47, 39, 31, 23, 15, 7]
    return table_swap(bitstring, table)

def final_permutation(bitstring):
    '''
    Final Permutation, see initial_permutation
    :param bitstring: bitstring
    '''
    table = [40, 8, 48, 16, 56, 24, 64, 32,
            39, 7, 47, 15, 55, 23, 63, 31,
            38, 6, 46, 14, 54, 22, 62, 30,
            37, 5, 45, 13, 53, 21, 61, 29,
            36, 4, 44, 12, 52, 20, 60, 28,
            35, 3, 43, 11, 51, 19, 59, 27,
            34, 2, 42, 10, 50, 18, 58, 26,
            33, 1, 41, 9, 49, 17, 57, 25]
    return table_swap(bitstring, table)

def clean(message):
    '''
    Clean the message. In other words, split it up into 8 byte chunks with null
    padding at the end to make things nice and pretty.
    :param string: message
    '''
    message += '\0\0\0\0\0\0\0\0'                                  # These are our null bytes
    blocks = [message[x:x + 8] for x in range(0, len(message), 8)] # Grab 8 byte chunks
    del blocks[len(blocks) - 1]                                    # The last is a null byte remainder, delete it
    return blocks

class key_schedule:
    '''
    Class to generate our keys. In a seperate class as to organize the code a
    little.
    '''
    def __init__(self, key, simple):
        '''
        The key arg is our keyword, while the simple arg is a boolean telling
        the code whether or not to make the thing simple. If it is True, then
        the keyword will shrink down to the first letter of the key repeated 8
        times, e.g. 'yourking' -> 'yyyyyyyy', to keep the 64 bit key.
        :param string: key
        :param bool: simple
        '''
        if simple:
            self.key = key[0] * 8
        else:
            self.key = key
        self.bkey    = string_to_bits(self.key) # Our bkey is the important part
        self.subkeys = None
        self.left    = None
        self.right   = None

    def gen_keys(self):
        '''
        The actual function to generate keys.
        '''
        subkeys       = []                         # This will fill with 16 48 bit keys
        left, right   = self.pc1(self.bkey)        # Our initial function splits our bkey into left and right parts for the rounds
        single_rounds = [0, 1, 8, 15]              # There are a couple rounds, these indicate which have a shift of 1
        for number in range(total_number_of_rounds):
            if number in single_rounds:
                shift = 1
            else:
                shift = 2
            left  = rotate_bitstring(left, shift)  # All this does is perform << by shift
            right = rotate_bitstring(right, shift)
            subkeys.append(self.pc2(left, right))  # Append our modified new key to subkeys
        self.subkeys = subkeys
        return subkeys

    def pc1(self, key):
        '''
        With 64 bit key input, this generates two seperate 28 bit keys. The
        remaining 8 bits are thrown out. These garbage bits come from the last
        bit of each letter.
        :param bitstring: key
        '''
        lrows = [57, 49, 41, 33, 25, 17, 9,
                1, 58, 50, 42, 34, 26, 18,
                10, 2, 59, 51, 43, 35, 27,
                19, 11, 3, 60, 52, 44, 36]
        rrows = [63, 55, 47, 39, 31, 23, 15,
                7, 62, 54, 46, 38, 30, 22,
                14, 6, 61, 53, 45, 37, 29,
                21, 13, 5, 28, 20, 12, 4]
        left       = table_swap(key, lrows)
        right      = table_swap(key, rrows)
        self.left  = left
        self.right = right
        return left, right

    def pc2(self, left, right):
        '''
        With 64 bit input, this non-linearly shuffles the bits around.
        :param bitstring: left
        :param bitstring: right
        '''
        current_key = left + right
        table = [14, 17, 11, 24, 1, 5, 3, 28,
                 15, 6, 21, 10, 23, 19, 12, 4,
                 26, 8, 16, 7, 27, 20, 13, 2,
                 41, 52, 31, 37, 47, 55, 30, 40,
                 51, 45, 33, 48, 44, 49, 39, 56,
                 34, 53, 46, 42, 50, 36, 29, 32]
        subkey = table_swap(current_key, table)
        return subkey

class feistel:
    '''
    The feistel operation is at the heart of this algorithm.
    '''
    def __init__(self, half, key, round_num):
        '''
        When this class is initialized, it will perform the function and set self.final as the answer
        :param bitstring: half
        :param class: key
        :param int: round_num
        '''
        # Lookup tables
        self.S = {'0':[[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
                    [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
                    [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
                    [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
                  '1':[[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
                   [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
                   [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
                   [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],
                  '2':[[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
                   [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
                   [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
                   [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],
                  '3':[[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
                   [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
                   [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
                   [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],
                  '4':[[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
                   [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
                   [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
                   [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],
                  '5':[[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
                   [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
                   [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
                   [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],
                  '6':[[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
                   [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
                   [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
                   [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]],
                  '7':[[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
                   [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
                   [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
                   [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]
                  }
        self.round_num = round_num
        self.block     = half
        self.key       = key
        self.expanded  = self.feistel_expansion(self.block)
        self.mixed     = self.key_mix(self.expanded, self.key.subkeys[self.round_num])
        self.subbed    = self.substitution(self.mixed)
        self.permuted  = self.permute(self.subbed)
        self.final     = self.permuted

    def feistel_expansion(self, block):
        '''
        Stage One of the Feistel Operation. Essentially just a tableswap
        :param bitstring: block
        '''
        table = [32, 1, 2, 3, 4, 5,
                4, 5, 6, 7, 8, 9,
                8, 9, 10, 11, 12, 13,
                12, 13, 14, 15, 16, 17,
                16, 17, 18, 19, 20, 21,
                20, 21, 22, 23, 24, 25,
                24, 25, 26, 27, 28, 29,
                28, 29, 30, 31, 32, 1]
        outstring = table_swap(block, table)
        return outstring

    def key_mix(self, block, key):
        '''
        Stage Two of the Feistel Operation. XORs the current key and the bitstring
        :param bitstring: block
        :param bitstring: key
        '''
        final = XOR_bitstring(block, key)
        return final

    def substitution(self, block):
        '''
        Stage Three of the Feistel Operation. Uses our lookup tables
        initialized above to convert 6 bit chunks in our bitstring to 4 bit
        chunks. This table is also nonlinear, leading to the increased
        complexity of the algorithm.
        :param bitstring: block
        '''
        final_block = ''
        pieces = [block[x:x + 6] for x in range(0, len(block), 6)]
        for number in range(8):
            x = pieces[number][1:5]
            y = pieces[number][0] + pieces[number][5]
            num = '%04d' %int(bin(self.S[str(number)][int(y, 2)][int(x, 2)])[2:])
            final_block += num
        return final_block

    def permute(self, block):
        '''
        Stage Four of the Feistel Operation. Again, just a lookup table.
        :param bitstring: block
        '''
        table = [16, 7, 20, 21, 29, 12, 28, 17,
                1, 15, 23, 26, 5, 18, 31, 10,
                2, 8, 24, 14, 32, 27, 3, 9,
                19, 13, 30, 6, 22, 11, 4, 25]
        s_block = table_swap(block, table)
        return s_block

def get_args():
    default = '''the quick BROWN fox lept OVER\
    the lazy DOG_1234568790=_=-=_+_+\][|}{~`!@#$%^&*():/.,?><'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--message', type=str,
                        default=default, help='Input Message')
    parser.add_argument('-d', '--decrypt', action='store_true',
                        help='Decrypt?')
    parser.add_argument('-e', '--encrypt', action='store_true',
                        help='Encrypt?')
    parser.add_argument('-f', '--fileinput', type=str,
                        default=None, help='Input File')
    parser.add_argument('-k', '--key', type=str,
                        default='yourking', help='Encryption Key')
    parser.add_argument('-s', '--simple', action='store_true',
                        help='Use Simple DES?')
    parser.add_argument('-b', '--bits', action='store_true',
                        help='Output Raw Bits')
    args = parser.parse_args()
    if args.decrypt and args.message == default:
        args.message = ''
    if args.fileinput:
        args.message = open(args.fileinput, 'r').read()
    return args

if __name__ == "__main__":
    sys.exit(main())
