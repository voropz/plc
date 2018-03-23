from common import *
import sys
import numpy as np


def parse_command(line, arg1_type=None, arg2_type=None):
    arg1 = 0
    if arg1_type is None:
        return [0, 0]
    elif arg1_type == "reg":
        arg1 = registers.get(line[1])
        Check(arg1 is not None, "Неверный аргумент " + line[1])
    elif arg1_type == "line":
        try:
            arg1 = (int(line[1]) - 1) * COMMAND_LEN + FIRST_COMMAND_ADDR
        except ValueError:
            Check(False, "Неверный аргумент " + line[1])
    arg2 = 0
    if arg2_type is None:
        pass
    elif arg2_type == "reg":
        arg2 = registers.get(line[2])
        Check(arg2 is not None, "Неверный аргумент " + line[2])
    elif arg2_type == "int":
        try:
            arg2 = int(line[2])
        except ValueError:
            Check(False, "Неверный аргумент " + line[2])
    return [arg1, arg2]


def make_array_from_asm(path_in):
    with open(path_in, mode='r') as command_file:
        output = []
        output += [0] * len(registers)
        output[EIP] = FIRST_COMMAND_ADDR
        statics = [0] * STATIC_SIZE
        statics_pos = 0

        for line in command_file:
            line = line.split(" ;", 1)[0]
            print_static = False
            if line.startswith("print \""):
                line = line.strip('\n').split('\"')[:-1]
                line[0] = "print"
                print_static = True
            else:
                line = line.strip('\n').split(' ')

            command_id = commands.get(line[0])
            output.extend([command_id])
            if command_id == MOV:
                output.extend(parse_command(line, "reg", "reg"))
            elif command_id == MOVN:
                output.extend(parse_command(line, "reg", "int"))
            elif command_id == ADD:
                output.extend(parse_command(line, "reg", "reg"))
            elif command_id == ADDN:
                output.extend(parse_command(line, "reg", "int"))
            elif command_id == SUB:
                output.extend(parse_command(line, "reg", "reg"))
            elif command_id == SUBN:
                output.extend(parse_command(line, "reg", "int"))
            elif command_id == JMP:
                output.extend(parse_command(line, "line"))
            elif command_id == JLZ:
                output.extend(parse_command(line, "line", "reg"))
            elif command_id == PUSH:
                output.extend(parse_command(line, "reg"))
            elif command_id == POP:
                output.extend(parse_command(line, "reg"))
            elif command_id == CALL:
                output.extend(parse_command(line, "line"))
            elif command_id == RET:
                output.extend(parse_command(line))
            elif command_id == END:
                output.extend(parse_command(line))
            elif command_id == PRINT:
                if print_static:
                    output.extend([statics_pos, 1])
                    encoded = list(line[1].encode('utf-8'))
                    statics[statics_pos] = len(encoded)
                    statics_pos += 1
                    for i in range(len(encoded)):
                        statics[statics_pos] = encoded[i]
                        statics_pos += 1
                else:
                    output.extend(parse_command(line, "reg"))
            elif command_id == READN:
                output.extend(parse_command(line, "reg"))
            else:
                print("Error: " + line[0] + " is not a valid command")
                return False

        output[ESP] = len(output)
        output[EBP] = len(output)
        output.extend([0] * STACK_SIZE)
        output[STC] = len(output)
        output.extend(statics)
        return output


def write_array_as_bytes(array, path_out):
    np.array(array, dtype=int).tofile(path_out)


if __name__ == '__main__':
    if len(sys.argv) not in [2, 3]:
        print("Usage: assembler.py <source file> [<dest file>]")
        exit(-1)
    output_path = str(sys.argv[1]) + ".btc"  # bytecode, not bitcoin
    if len(sys.argv) == 3:
        output_path = sys.argv[2]

    output_array = make_array_from_asm(sys.argv[1])
    write_array_as_bytes(output_array, output_path)