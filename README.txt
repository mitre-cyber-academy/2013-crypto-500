Name: Modern Cryptography Standards

Description: The year is 1972, and as an official of the US government it's come to your attention that a new standard for classified information is needed in this modern day and age. In the past cryptography has worked well, no ciphers currently exist that would be suitable for this task, however a new cipher has just been proposed by IBM and it's up to you to try to crack their message. You know that they used a weak keyword consisting of 4 pairs of 2 letters each (e.g. 'AeAeAeAe') as well as a weak encryption method, the electronic codebook. Since IBM's cipher relies on a certain number of rounds, you also know that they could be using anywhere from 10 to 50 rounds. Everyone's counting on you to give an answer on whether or not this cipher is a good fit for the government. Good Luck.

How to crack: In order to break this cipher, the users need to first make an adaptable version of DES that supports multiple rounds. They then need to bruteforce every key [aaaaaaaa, abababab, ..., zzzzzzzz] with every round inbetween [10, 50]. The corrent number of rounds is 33.

To Build: No building necessary. To generate do: ./des.py -f ./plaintext.txt -k jvjvjvjv > ./ciphertext.txt

What to distribute: ./dist/ciphertext.txt

Flag: MCA-5243342B (Points to RC4)
