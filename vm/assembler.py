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


def translate_labels(path_in):
    with open(path_in, mode='r') as command_file:
        labels = []
        pos = 1
        for line in command_file:
            if line.startswith("label"):
                line = line.strip(":\n").split(' ')[1]
                labels.append((line, pos))
                continue
            pos += 1
        return dict(labels)


def make_array_from_asm(path_in):
    labels = translate_labels(path_in)
    with open(path_in, mode='r', encoding='utf-8') as command_file:
        output = []
        output += [0] * len(registers)
        output[EIP] = FIRST_COMMAND_ADDR
        statics = []
        statics_pos = 0

        for line in command_file:
            if line.startswith("label"):
                continue
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
                line[1] = labels.get(line[1], line[1])
                output.extend(parse_command(line, "line"))
            elif command_id == JLZ:
                line[1] = labels.get(line[1], line[1])
                output.extend(parse_command(line, "line", "reg"))
            elif command_id == PUSH:
                output.extend(parse_command(line, "reg"))
            elif command_id == POP:
                output.extend(parse_command(line, "reg"))
            elif command_id == CALL:
                line[1] = labels.get(line[1], line[1])
                output.extend(parse_command(line, "line"))
            elif command_id == RET:
                output.extend(parse_command(line))
            elif command_id == END:
                output.extend(parse_command(line))
            elif command_id == PRINT:
                if print_static:
                    output.extend([statics_pos, 1])
                    encoded = list(line[1].encode('utf-8'))
                    encoded.extend([0] * (4 - len(encoded) % 4))
                    packed = np.zeros(len(encoded) // 4, dtype=np.uint)
                    for i in np.arange(0, len(encoded), 4):
                        packed[i//4] = ((encoded[i] << 24) +
                                        (encoded[i + 1] << 16) +
                                        (encoded[i + 2] << 8) +
                                        (encoded[i + 3]))

                    statics.append(len(packed))
                    statics_pos += 1 + len(packed)
                    statics.extend(packed.view(dtype=np.int))
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
        np.array(array, dtype=np.int).tofile(path_out)


if __name__ == '__main__':
    if len(sys.argv) not in [2, 3]:
        print("Usage: assembler.py <source file> [<dest file>]")
        exit(-1)
    output_path = str(sys.argv[1]) + ".btc"  # bytecode, not bitcoin
    if len(sys.argv) == 3:
        output_path = sys.argv[2]

    output_array = make_array_from_asm(sys.argv[1])
    write_array_as_bytes(output_array, output_path)