#!/usr/bin/env python3

# ALDL_Py

import sys
import argparse
import time
import serial
import os
import json
from bitarray import bitarray
from simpleeval import simple_eval

#### Global variables ##########################################################
log_filetype_version = 1
log_time = time.localtime()
log_file = os.path.join(os.path.abspath(os.getcwd()), "dumps/recieve", time.strftime("%Y-%m-%d-%H-%M-%S", log_time) + ".ecmlog")

log_file_increment = 0
while True:
    if os.path.exists(log_file):
        log_file_increment += 1
        log_file = os.path.join(os.path.abspath(os.getcwd()), "dumps/recieve", time.strftime(f"%Y-%m-%d-%H-%M-%S{(str(log_file_increment))}", log_time) + ".ecmlog")
    else:
        break

with open(log_file, "wb") as file:
    file.write(log_filetype_version.to_bytes(2, "little"))

def parse_data(data_definition, transmit_mode, msg_body):
    mode_definition = list(filter(lambda d: int(d['transmit_mode'], 16) == transmit_mode, data_definition["transmit_modes"]))
    print(transmit_mode)
    if mode_definition:
        ("Definition file slayyed")
        bytes = [msg_body[i : i + 1] for i in range(len(msg_body))]
        formatted_bytes = []
        bytes_iter = iter(enumerate(bytes))
        print(str(int(time.time())))
        for position, byte in bytes_iter:
            word = byte
            byte_definition = list(filter(lambda d: int(d['offset'], 16) == position, mode_definition[0]["data_definitions"]))
            
            if byte_definition:
                
                byte_name = byte_definition[0]["name"]
                definition_offset = int(byte_definition[0]["offset"], 16)
                shared_byte_definitions = list(filter(lambda d: int(d["offset"], 16) >= definition_offset, sorted(list(filter(lambda d: d["name"] == byte_name, mode_definition[0]["data_definitions"])), key=lambda i: int(i["offset"] , 16))))
                
                if len(shared_byte_definitions) > 1:

                    loop = 1
                    offset = int(shared_byte_definitions[0]['offset'], 16)
                    filtered_shared_byte_definitions = [shared_byte_definitions[0]]

                    for defintion in shared_byte_definitions[1:]:
                        if offset + 1 == int(shared_byte_definitions[loop]['offset'], 16):
                            filtered_shared_byte_definitions.append(shared_byte_definitions[loop])
                            loop += 1
                            offset += 1
                            if loop >= len(shared_byte_definitions):
                                break
                        else:
                            break

                    if len(filtered_shared_byte_definitions) > 1:
                        word = bytes[position  : position + len(filtered_shared_byte_definitions)]

                        for i in range(len(filtered_shared_byte_definitions) - 1):
                            next(bytes_iter, None)
                       
            else:
                print("No definition found :(")
                continue
            
            formatted_bytes.append(word)


        formatted_bytes_iter = iter(enumerate(formatted_bytes))

        position = 0
        for i, word in formatted_bytes_iter:
            whole_word = b''
            byte_definition = list(filter(lambda d: int(d['offset'], 16) == position, mode_definition[0]["data_definitions"]))
            # print(position)
            print(byte_definition[0]["name"])
            if byte_definition:
                if type(word) is list:
                    whole_word = b"".join(word)
                else:
                    whole_word = word
                
                if "bit_flags" in byte_definition[0]:
                    
                    bits = bitarray()
                    bits.frombytes(whole_word)

                    for bit_position, bit in enumerate(bits):
                        if byte_definition[0]["bit_flags"][bit_position]:       
                            bit_definition = byte_definition[0]["bit_flags"][bit_position]

                            if bit:  
                                print(bit_definition["description"] + ": True")
                            else:
                                print(bit_definition["description"] + ": False")
                    # todo: handle lookup tables
                else:
                    # print(word)
                    byte_int = int.from_bytes(whole_word, 'big')
                    # todo: handle signed and unsigned ints successfully
                    print(byte_int)
                    if "conversion" in byte_definition[0]:
                        converted_int = simple_eval(byte_definition[0]["conversion"].replace("n", str(byte_int)))
                    else:
                        converted_int = byte_int
                    
                    print(converted_int)
                    print(whole_word.hex())


            if type(word) is list:
                position += len(word)
            else:
                position += 1
        
            print("-------------------")
    
    else:
        print("Definition file slayn't")
        return

def print_formatted(msg):
    print("ID:    {:#04x}".format(msg[0]))
    print("Mode:  {:#04x}".format(msg[1]))
    print("Body:")
    for i in range(len(msg[2])):
        print("   {0:3d}:  {1:#04x}  {2:04b} {3:04b}  {1:3d}".format(i,
            msg[2][i], msg[2][i] >> 4, msg[2][i] >> 0x0f))

def message_log(message_time, message_id, message_length, message_mode, message, checksum):
    message_chunk = bytearray()
    message_time = int(message_time * 1000)

    message_chunk += message_time.to_bytes(8, "little")
    message_chunk += message_id.to_bytes(1, "little")
    message_chunk += message_length.to_bytes(1, "little")
    message_chunk += message_mode.to_bytes(1, "little")
    message_chunk += message
    message_chunk += checksum.to_bytes(1, "little")
    message_chunk = int(len(message_chunk) + 2).to_bytes(2, "little") + message_chunk

    with open(log_file, "ab") as file:
        file.write(message_chunk)

#### Serial interface ##########################################################

def message_recv(s, data_definition):
    """Wait for a valid message, then return its contents

    Wait for either an 0xf4 or an 0xf5. When it comes, read the rest of the
    message and verify its checksum. If all checks out, then return the message
    as an (id, mode, message) tuple. Otherwise, try again.
    """
    
    while True:
        msg_id = None
        msg_len = None
        msg_mode = None
        msg_body = None

        start_time = time.time()
        while True:
            if time.time() - start_time > 5:
                return()

            else:
                try:
                    msg_id = s.read()[0]
                    # print(msg_id)
                    if msg_id == 0xf4 or msg_id == 0xf5:
                        break
                except IndexError:
                    print("Index Error")
                    return()


        print("Message received")
        checksum = msg_id
        msg_len_original = s.read()[0]
        checksum += msg_len_original
        msg_len = msg_len_original - 0x56
        
        msg_mode = s.read()[0]
        checksum += msg_mode

        msg_body = s.read(msg_len)
        for b in msg_body:
            checksum += b

        checksum = (-checksum) & 0xff
        checksum_in = s.read()[0]
        # print(checksum.to_bytes(1, "little").hex())
        if checksum != checksum_in:
            print("Warning: Checksum fail. Msg: {:02x} {:02x} {:02x}".format(
                msg_id, msg_len + 0x56, msg_mode), end="", file=sys.stderr)
            for b in msg_body:
                print(" {:02x}".format(b), end="", file=sys.stderr)
            print(" {:02x}".format(checksum_in), file=sys.stderr)
            return()
        else:

            message_log(time.time(), msg_id, msg_len_original, msg_mode, msg_body, checksum)

            '''
            disable logging until revamp
            with open(os.path.join(dump_location, "receive", str(time.time()).replace(".", "-") + ".bin"), "wb+") as f:
                f.write(msg_body) 
            '''

            parse_data(data_definition, msg_mode, msg_body)
            return(msg_id)
        

# s is the serial object
def message_send(s, msg_id, msg_mode, msg_body):
    """Send a message to the ECM.

    Message length and checksum are calculated automatically. See the data
    stream definition for what the parameters mean.

    Arguments:
    s: An open serial object
    msg_id: An integer representing the message ID
    msg_mode: An integer representing the message mode
    msg_body: A bytes or bytearray object containing the message body
    """
    msg = bytearray()
    msg.append(msg_id)
    checksum = msg_id

    msg_len = 0x56 + len(msg_body)
    msg.append(0x56 + len(msg_body))
    checksum = (checksum + msg_len)

    msg.append(msg_mode)
    checksum = (checksum + msg_mode)

    msg += msg_body
    for b in msg_body:
        checksum = (checksum + b)

    # Checksum is 1's compliment of sum of all bytes in the message
    msg.append((-checksum) & 0xff)
    
    '''
    with open(os.path.join(dump_location, "send", str(time.time()).replace(".", "-") + ".bin"), "wb+") as f:
        f.write(msg)
    '''
    s.write(msg)
    while s.out_waiting > 0:
        continue
    s.read(len(msg)) # read the message echo out of the buffer
    print("Message sent 🗣️")
    #DEBUG
    #print("@@@ 1", repr(msg), file=sys.stderr)

# This function should be called with an open serial object. It starts with
# the actual communication and echoing.
# s is the serial object
def manage_stream(s, data_definition):
    # It seems this works (on 8192 baud ALDL's) by sending one command
    # requesting a data transmit mode, which the ECM responds to with one
    # message of data. It's not entirely clear what mode the ECM is left in
    # after this happens, but two things seem apparent:
    #   1) The ECM will not send any more data until another request is sent to
    #      it.
    #   2) It's probably a good idea to send a "switch to normal mode" command
    #      before terminating the serial link. The Windows ALDL program that
    #      I analyzed did this, and the normal mode command must exist for some
    #      reason, after all. Hopefully this doesn't mean there is a potential
    #      safety risk if the program crashes before this is sent!

    #message_send(s, 0xf4, 0x01, b'\x00')
    #message_send(s, 0xf5, 0x01, b'\x00')
    #message_send(s, 0xf5, 0x01, b'\x01')

    try:
        while True:
            message_send(s, 0xf4, 0x01, b'\x00')
            # time.sleep(1)
            new_msg = message_recv(s, data_definition)
            if not new_msg:
                print("No reply 😔")
            '''if new_msg:
                print("\n### New Message ###")
                print_formatted(new_msg)
            else:
                print("No reply 😔")'''

            #time.sleep(1)
            #message_send(s, 0xf5, 0x01, b'\x00')
            #new_msg = message_recv(s)
            #print("\n### New Message ###")
            #print_formatted(new_msg)

            #time.sleep(1)
            #message_send(s, 0xf5, 0x01, b'\x01')
            #new_msg = message_recv(s)
            #print("\n### New Message ###")
            #print_formatted(new_msg)
            # time.sleep(3) # for testing
    except KeyboardInterrupt:
        print("Stopping...", file=sys.stderr)

    # Restore normal mode
    message_send(s, 0xf4, 0x00, b'')
    #message_send(s, 0xf5, 0x00, b'')

#### Program startup and init ##################################################

def main(args, data_definition):

    try:
        s = serial.Serial(args.port, baudrate = 8192, timeout = 5)
    except serial.SerialException as e:
        print("Error: {}".format(e.strerror))
        sys.exit(1)
    else:
        manage_stream(s, data_definition)
        s.close()

def log(args, data_definition):
    in_file = args.log[0]

    if os.path.isdir(in_file):

        files = []
        for root, directories, file in os.walk(in_file):
            for file in file:
                if(file.endswith(".bin")):
                    files.append(os.path.join(root,file))
        files.sort()

        for i, f in enumerate(files):
            if not i == len(files) - 1:        
                file, e = os.path.splitext(os.path.basename(f))
                next_file, e = os.path.splitext(os.path.basename(files[i + 1]))
                interval_time = float(next_file.replace("-", ".")) - float(file.replace("-", "."))
            else:
                interval_time = 0
            with open(f, 'rb') as f:
                parse_data(data_definition, b'\x01', f.read())
            time.sleep(interval_time)
    elif os.path.isfile(in_file) and in_file.endswith(".bin"):
        print("Valid log file")
    else:
        pass

if __name__ == "__main__":
    ap = argparse.ArgumentParser(
            description="Echo data parsed from the ALDL port",
            epilog="See the README for full documentation.")
    data_source_group = ap.add_mutually_exclusive_group()
    ap.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")
    data_source_group.add_argument("-l", "--log", nargs=1)
    data_source_group.add_argument("-p", "--port",
            help="The serial port to use (e.g. COM1, /dev/ttyACM0)")
    ap.add_argument("data_stream", nargs='+', type=argparse.FileType('rb'),
            help="One or more data stream definition files")


    args = ap.parse_args()
    data_definition = json.loads(args.data_stream[0].read())

    if args.log:
        log(args, data_definition)
    else:
       main(args, data_definition)
