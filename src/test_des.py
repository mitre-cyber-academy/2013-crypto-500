#!/usr/bin/env python

import sys
import unittest
import des
from des import key_schedule as ks
from des import feistel as fs

class TestDES(unittest.TestCase):
    def setUp(self):
        message = [chr(int(x, 2)) for x in ['00000001', '00100011', '01000101', '01100111', '10001001', '10101011', '11001101', '11101111']]
        self.message = des.clean(''.join(message))
        self.plaintext = '0000000100100011010001010110011110001001101010111100110111101111'
        keynums = ['00010011', '00110100', '01010111', '01111001', '10011011', '10111100', '11011111', '11110001']
        self.key = ''.join(keynums)

        self.keyenglish = ''.join([chr(int(x, 2)) for x in ['00010011', '00110100', '01010111', '01111001', '10011011', '10111100', '11011111', '11110001']])

    def test_string_to_bits(self):
        string1 = 'aa'
        string2 = 'abcd'
        string3 = 'dog'
        assert(des.string_to_bits(string1) == '0110000101100001')
        assert(des.string_to_bits(string2) == '01100001011000100110001101100100')
        assert(des.string_to_bits(string3) == '011001000110111101100111')

    def test_rotate_bitstring(self):
        string1 = '1000101110'
        string2 = '10110'
        string3 = '101111000101110'
        string4 = '001001101110'
        assert(des.rotate_bitstring(string1, 3) == '0101110100')
        assert(des.rotate_bitstring(string2, 2) == '11010')
        assert(des.rotate_bitstring(string3, 5) == '100010111010111')
        assert(des.rotate_bitstring(string4, 0) == '001001101110')

    def test_table_swap(self):
        table1 = [1, 5, 2, 6, 3, 7, 4]
        table2 = [1, 2, 3, 4, 5, 6, 7]
        table3 = [9, 8, 7, 6, 5, 4, 3, 3, 2, 1]
        table4 = [2, 7, 4, 5, 8, 2, 7, 8, 9, 1]
        string1 = '010101110001'
        string2 = '01011101010001'
        assert(des.table_swap(string1, table1) == '0011011')
        assert(des.table_swap(string1, table3) == '0111010010')
        assert(des.table_swap(string2, table2) == '0101110')
        assert(des.table_swap(string2, table4) == '1011110100')

    def test_XOR(self):
        string1 = '1000101110'
        string2 = '1011010101'
        string3 = '1011110010'
        string4 = '0010101110'
        assert(des.XOR_bitstring(string1, string2) == '0011111011')
        assert(des.XOR_bitstring(string3, string4) == '1001011100')

    def test_clean(self):
        string1 = 'one two three'
        string2 = 'args... whee!'
        assert(des.clean(string1) == ['one two ', 'three\0\0\0'])
        assert(des.clean(string2) == ['args... ', 'whee!\0\0\0'])

    def test_key_schedule(self):
        keys = ks(self.key, False)
        keys.bkey = self.key
        assert(keys.pc1(self.key) == ('1111000011001100101010101111', '0101010101100110011110001111'))
        keys.gen_keys()
        assert(keys.left == '1111000011001100101010101111')
        assert(keys.right == '0101010101100110011110001111')
        assert(keys.subkeys[0] == '000110110000001011101111111111000111000001110010')
        assert(keys.subkeys[1] == '011110011010111011011001110110111100100111100101')
        assert(keys.subkeys[2] == '010101011111110010001010010000101100111110011001')
        assert(keys.subkeys[3] == '011100101010110111010110110110110011010100011101')
        assert(keys.subkeys[4] == '011111001110110000000111111010110101001110101000')
        assert(keys.subkeys[5] == '011000111010010100111110010100000111101100101111')
        assert(keys.subkeys[6] == '111011001000010010110111111101100001100010111100')
        assert(keys.subkeys[7] == '111101111000101000111010110000010011101111111011')
        assert(keys.subkeys[8] == '111000001101101111101011111011011110011110000001')
        assert(keys.subkeys[9] == '101100011111001101000111101110100100011001001111')
        assert(keys.subkeys[10] == '001000010101111111010011110111101101001110000110')
        assert(keys.subkeys[11] == '011101010111000111110101100101000110011111101001')
        assert(keys.subkeys[12] == '100101111100010111010001111110101011101001000001')
        assert(keys.subkeys[13] == '010111110100001110110111111100101110011100111010')
        assert(keys.subkeys[14] == '101111111001000110001101001111010011111100001010')
        assert(keys.subkeys[15] == '110010110011110110001011000011100001011111110101')

    def test_create_halves(self):
        permuted = des.initial_permutation(self.plaintext)
        assert(permuted == '1100110000000000110011001111111111110000101010101111000010101010')
        assert(des.create_halves(permuted) == ('11001100000000001100110011111111', '11110000101010101111000010101010'))

    def test_feistel(self):
        permuted = des.initial_permutation(self.plaintext)
        halves   = des.create_halves(permuted)

        keys      = ks(self.key, False)
        keys.bkey = self.key
        keys.gen_keys()

        expansion_block = '1111 0000 1010 1010 1111 0000 1010 1010'.replace(' ', '')
        mix_block       = '011110 100001 010101 010101 011110 100001 010101 010101'.replace(' ', '')
        sub_block       = '011000 010001 011110 111010 100001 100110 010100 100111'.replace(' ', '')
        permute_block   = '0101 1100 1000 0010 1011 0101 1001 0111'.replace(' ', '')
        final_block     = '0010 0011 0100 1010 1010 1001 1011 1011'.replace(' ', '')

        feistel = fs(halves[0], keys, 0)
        assert(feistel.feistel_expansion(expansion_block) == mix_block)
        current_key = ' 000110 110000 001011 101111 111111 000111 000001 110010'.replace(' ', '')
        assert(feistel.key_mix(mix_block, current_key) == sub_block)
        assert(feistel.substitution(sub_block) == permute_block)
        assert(feistel.permute(permute_block) == final_block)

    def test_final_permutation(self):
        assert(des.final_permutation('00001010 01001100 11011001 10010101 01000011 01000010 00110010 00110100'.replace(' ', '')) == '10000101 11101000 00010011 01010100 00001111 00001010 10110100 00000101'.replace(' ', ''))

    def test_success(self):
        blocks = self.message
        key    = des.key_schedule(self.keyenglish, False)
        final  = des.encode(blocks, key, False)
        test_answer = '10000101 11101000 00010011 01010100 00001111 00001010 10110100 00000101'.replace(' ', '')
        assert(des.string_to_bits(final) == test_answer)

if __name__ == "__main__":
    unittest.main()
