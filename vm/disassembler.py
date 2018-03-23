from common import *
import sys
import numpy as np


def parse_command(line, arg1_type=None, arg2_type=None):
    ret_val = commands_id_to_name.get(line[0])
    Check(ret_val is not None)

    if arg1_type is None:
        return ret_val + "\n"
    elif arg1_type == "reg":
        reg_name = registers_id_to_name.get(line[1])
        Check(reg_name is not None)
        ret_val += " " + reg_name
    elif arg1_type == "line":
        ret_val += " " + str((line[1] - FIRST_COMMAND_ADDR) // COMMAND_LEN + 1)

    if arg2_type is None:
        pass
    elif arg2_type == "reg":
        reg_name = registers_id_to_name.get(line[2])
        Check(reg_name is not None)
        ret_val += " " + reg_name
    elif arg2_type == "int":
        ret_val += " " + str(line[2])
    return ret_val + "\n"


def make_asm_from_array(array, path_out):
    with open(path_out, mode='w') as command_file:
        pos = FIRST_COMMAND_ADDR

        while pos < len(array):
            line = [array[pos], array[pos+1], array[pos+2]]
            command_id = line[0]
            pos += 3
            if command_id == MOV:
                command_file.write(parse_command(line, "reg", "reg"))
            elif command_id == MOVN:
                command_file.write(parse_command(line, "reg", "int"))
            elif command_id == ADD:
                command_file.write(parse_command(line, "reg", "reg"))
            elif command_id == ADDN:
                command_file.write(parse_command(line, "reg", "int"))
            elif command_id == SUB:
                command_file.write(parse_command(line, "reg", "reg"))
            elif command_id == SUBN:
                command_file.write(parse_command(line, "reg", "int"))
            elif command_id == JMP:
                command_file.write(parse_command(line, "line"))
            elif command_id == JLZ:
                command_file.write(parse_command(line, "line", "reg"))
            elif command_id == PUSH:
                command_file.write(parse_command(line, "reg"))
            elif command_id == POP:
                command_file.write(parse_command(line, "reg"))
            elif command_id == CALL:
                command_file.write(parse_command(line, "line"))
            elif command_id == RET:
                command_file.write(parse_command(line))
            elif command_id == END:
                command_file.write(parse_command(line))
            elif command_id == PRINT:
                if line[2] == 1:
                    start = line[1] + 1 + len(array) - STATIC_SIZE
                    length = array[start - 1]
                    encoded = array[start:start + length]
                    decoded = bytes(list(encoded)).decode('utf-8')
                    command_file.write("print ")
                    command_file.write(decoded)
                    command_file.write("\n")
                else:
                    command_file.write(parse_command(line, "reg"))
            elif command_id == READN:
                command_file.write(parse_command(line, "reg"))
            else:
                print("Error: " + line[0] + " is not a valid command")
                return False


if __name__ == '__main__':
    if len(sys.argv) not in [2, 3]:
        print("Usage: disassembler.py <.btc file> [<dest file>]")
        exit(-1)
    output_path = str(sys.argv[1]) + ".txt"
    if len(sys.argv) == 3:
        output_path = sys.argv[2]

    array = np.fromfile(sys.argv[1], dtype=int)
    make_asm_from_array(array, output_path)