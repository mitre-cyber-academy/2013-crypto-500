#!/usr/bin/env python

import sys
import des
import pp

jobServer = pp.Server()
jobs = []

blocks = open('./ciphertext.txt', 'r').read()[:-1]
message = des.clean(blocks)

des.total_number_of_rounds = 33

def main():
    alphabet = [chr(x) for x in range(97, 123)]
    for letter1 in alphabet:
        for letter2 in alphabet:
            key = (letter1 + letter2) * 4
            jobs.append(
                    jobServer.submit(
                        cracker,
                        (key, message),
                        (lambda a: a, lambda b: b),
                        ('des', 'argparse', 'sys')))

    for job in jobs:
        job()

    jobServer.print_stats()

def cracker(key, message):
    keys = des.key_schedule(key, False)
    print key
    print(des.encode(message, keys, True))


if __name__ == "__main__":
    sys.exit(main())
