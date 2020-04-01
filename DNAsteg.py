#!/usr/bin/env python3

'''
Author: Patrick Kelly (patrickyunen@gmail.com)
Last Updated: 4-1-2020
'''

import argparse


nucleotides = ['A', 'C', 'G', 'T']
code_dict = {'A': '00', 'C': '01', 'G': '10', 'T': '11'}
reverse_dict = {'00': 'A', '01':'C', '10':'G', '11':'T'}


# Convert list of ASCII values to bitstream
def get_bitstream(ascii_list):
    bitstream = ''
    for char in ascii_list:
        binary = '{0:08b}'.format(char)
        bitstream += binary
    return bitstream


# Convert DNA sequence to bitstream
def DNA_to_binary(sequence):
    binary = ''
    for nucleotide in sequence:
        if nucleotide not in nucleotides:
            continue
        binary += code_dict[nucleotide]
    return binary


# Convert a bitstream to a DNA sequence
def binary_to_DNA(sequence):
    DNA = ''
    for index in range(0,len(sequence),2):
        word = sequence[index:index+2]
        DNA += reverse_dict[word]
    return DNA


# Conceal message string in DNA sequence using specified keys
def encode(message, sequence, key1, key2=3):
    mssg_list = list(message)
    mssg_list.reverse()
    ascii_list = [ord(i) for i in mssg_list]

    ascii_list[0] = key1 ^ ascii_list[0]
    for j in range(1,len(ascii_list)):
        ascii_list[j] ^= ascii_list[j-1]

    msgstream = get_bitstream(ascii_list)
    seqstream = DNA_to_binary(sequence)

    steg_binary = ''
    seq_index, msg_index = 0,0

    while msg_index < len(msgstream):
        segment = seqstream[seq_index:seq_index+key2]
        message_bit = msgstream[msg_index]
        steg_binary += message_bit + segment
        seq_index += key2
        msg_index += 1

    encoded = binary_to_DNA(steg_binary)
    return encoded


# Extract a message from steganographic DNA
def decode(sequence, key1, key2):
    msgstream = ''
    seqstream = DNA_to_binary(sequence)
    for index in range(0,len(seqstream),key2+1):
        segment = seqstream[index:index+key2+1]
        msgstream += segment[0]
    ascii_list = []
    for index in range(0,len(msgstream),8):
        byte = int(msgstream[index:index+8],2)
        ascii_list.append(byte)
    ascii_list.reverse()

    for j in range(len(ascii_list)-1):
        ascii_list[j] ^= ascii_list[j+1]
    ascii_list[-1] ^= key1

    decoded = ''
    for num in ascii_list:
        decoded += chr(num)
    return decoded


# Read sequence from FASTA text file
def get_FASTA_sequence(filename):
    with open(filename,'r') as fh:
        next(fh)
        return fh.read()


# Get the steganographic DNA sequence from formatted text file
def get_steg_sequence(filename):
    with open(filename,'r') as fh:
        lines = fh.readlines()
        key1 = int(lines[0].split()[1])
        key2 = int(lines[1].split()[1])
        sequence = lines[2]
        return key1, key2, sequence


# Write the stegDNA to a file (with keys)
def write_file(filename, key1, key2, sequence):
    with open(filename, 'w') as fh:
        fh.writelines([f'Key1: {key1}\n', f'Key2: {key2}\n', sequence])


# Check that sequence is long enough for message
def validate_input(mssg, input_seq, key2):
    if (len(input_seq)/key2) < len(mssg):
        print(len(input_seq))
        print(len(mssg))
        print('**Invalid Input!')
        print('**Message is too long for input sequence')
        exit(1)
    return


#Concealer function
def concealer(message, input_seq, key1, output_file, key2=3):
    base_sequence = get_FASTA_sequence(input_seq)
    validate_input(message, base_sequence, key2)
    steg_sequence = encode(message, base_sequence, key1, key2)
    write_file(output_file, key1, key2, steg_sequence)


# Extracter function
def extracter(filename):
    key1, key2, sequence = get_steg_sequence(filename)
    message = decode(sequence, key1, key2)
    print(message)


# The main event
def main():

    #Command line options (-c,-d,-i,-p,-o,-s,-g) with argparse module:
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()

    group.add_argument("-c", "--conceal", action="store_true", help="conceal message in DNA sequence")
    group.add_argument("-r", "--read", action="store_true", help="extract message from DNA sequence")
    parser.add_argument("-i", "--input", type=str, help="input file (base sequence for conceal mode, steg sequence for extract mode")
    parser.add_argument("-m", "--message", type=str, help="message string to be concealed")
    parser.add_argument("-o", "--output", type=str, help="name of output file for steg DNA sequence")
    parser.add_argument("-k", "--key", type=int, help="encryption key (an integer between 0 and 255)")
    parser.add_argument("-l", "--length", type=int, help="frequency of message bit insertion; default is 3")

    args = parser.parse_args()


    #Set variables with command-line inputs
    conceal = args.conceal
    read = args.read
    input = args.input
    message = args.message
    outfile = args.output
    key1 = args.key
    key2 = args.length


    #Runtime
    if conceal:
        if key2:
            concealer(message, input, key1, outfile, key2)
        else:
            concealer(message, input, key1, outfile)
    else:
        extracter(input)


if __name__ == '__main__':
    main()
