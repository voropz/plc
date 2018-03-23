import numpy as np

DEBUG = False

COMMAND_LEN = 3
STACK_SIZE = 33 * 3
STATIC_SIZE = 33 * 3  # все выравниваем


def Check(condition, error_string="Неизвестная ошибка"):
    if not condition:
        print(error_string)
        assert False


# условно пишем в исполняемый файл, но не насилуем жеский диск
class BinaryFile:
    def __init__(self, size, buff):
        self.size = size
        self.buff = buff  # np.zeros(size, dtype=np.int32)

    def write(self, address, data):
        Check(address < self.size, "Попытка записи по адресу {0} при размере программы {1}".format(address, self.size))
        self.buff[address] = data

    def read(self, address):
        Check(address < self.size, "Попытка чтения по адресу {0} при размере программы {1}".format(address, self.size))
        return self.buff[address]

    def print(self, end=None):
        for cell in np.arange(0, self.size if end is None else end, COMMAND_LEN):
            print("[{0:3d}]".format(cell), end=' ')
            print("{0:4d} {1:4d} {2:4d}".format(self.read(cell), self.read(cell + 1), self.read(cell + 2)))

        print("")


# Коды операций
# копирует в регистр другой регистр
MOV = 0
# копирует в регистр число
MOVN = 1
# складывает два регистра
ADD = 2
# складывает регистр и число
ADDN = 3
# вычитает из регистра значение другого
SUB = 4
# вычитает из регистра число
SUBN = 5
# безусловный переход на номер строки
JMP = 6
# переход на строку, если значение регистра меньше 0
JLZ = 7
# записать регистр в стек
PUSH = 8
# записать вершину стека в регистр
POP = 9
# вызвать функцию (по номеру строки)
CALL = 10
# возврат из функции
RET = 11
# конец программы
END = 12
# вывести на экран что-нибудь
PRINT = 13
# ввести число
READN = 14
command_names = ["mov", "movn", "add", "addn", "sub", "subn", "jmp", "jlz", "push", "pop", "call", "ret", "end",
                 "print", "readn"]
command_ids = [MOV, MOVN, ADD, ADDN, SUB, SUBN, JMP, JLZ, PUSH, POP, CALL, RET, END, PRINT, READN]
commands = {command_names[i]: command_ids[i] for i in range(len(command_ids))}

# Регистры
EIP = 0
ESP = 1
EBP = 2
EAX = 3
EBX = 4
ECX = 5
EDX = 6
STC = 7
NIU = 8  #   неиспользуемы регистр, чтобы выровнять команды
reg_names = ["eip", "esp", "ebp", "eax", "ebx", "ecx", "edx", "stc", "anu"]
reg_ids = [EIP, ESP, EBP, EAX, EBX, ECX, EDX, STC, NIU]
registers = {reg_names[i]: reg_ids[i] for i in range(len(reg_ids))}

FIRST_COMMAND_ADDR = len(registers)


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


def MakeBinaryFromAsm(path_in, path_out):
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
                    encoded = list(line[1].encode('utf-32'))
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


class VirtualMachine:
    def __init__(self, memory):
        self.memory = memory
        self.private_reg = [EIP, ESP, EBP]

    def Run(self):
        while self.run_next_command():
            pass

    def mov(self, where, what):
        self.movn(where, self.at(what))

    def movn(self, where, what):
        Check(where not in self.private_reg, "Попытка записи {1} в защищенную область {0}".format(where, what))
        self.memory.write(where, what)

    def add(self, where, what):
        self.addn(where, self.at(what))

    def addn(self, where, what):
        Check(where not in self.private_reg, "Попытка записи {1} в защищенную область {0}".format(where, what))
        result = self.at(where) + what
        self.memory.write(where, result)

    def sub(self, where, what):
        self.addn(where, -self.at(what))

    def subn(self, where, what):
        self.addn(where, -what)

    def jmp(self, where):
        Check(where > EDX, "Попытка исполнения данных")
        # после всех команд происходит сдвиг, который компенсируется -3
        self.memory.write(EIP, where - 3)

    def jlz(self, where, why):
        if self.at(why) < 0:
            self.jmp(where)

    def push(self, where):
        # переполнение обнаруживается в Memory
        self.memory.write(self.at(ESP), self.at(where))
        self.memory.write(ESP, self.at(ESP) + 1)

    def pop(self, where):
        Check(self.at(ESP) >= self.at(EBP), "Извлечение из пустого стека")
        self.memory.write(ESP, self.at(ESP) - 1)
        self.memory.write(where, self.at(self.at(ESP)))

    def call(self, where):
        self.push(EBP)
        self.memory.write(EBP, self.at(ESP) - 1)
        self.push(EIP)
        self.memory.write(EIP, where - COMMAND_LEN)

    def ret(self):
        self.memory.write(ESP, self.at(EBP))  # база стека вызванной функции = вершине вызывающей
        self.memory.write(EBP, self.at(self.at(EBP)))  # там записана вершина вызывающей
        self.memory.write(EIP, self.at(self.at(ESP) + 1))  # следом записан адрес возврата

    def print(self, where, mode):
        if mode == 1:  # static
            start = self.at(STC) + where + 1
            length = self.at(start - 1)
            encoded = [self.at(start + i) for i in range(length)]
            print(bytes(encoded).decode('utf-32'))
        else:
            print(self.at(where))

    def readn(self, a1):
        while True:
            try:
                i = int(input())
                break
            except ValueError:
                print('Введено не число')
        self.memory.write(a1, i)

    # возвращает false при окончании работы (и неожиданной команде)
    def run_next_command(self):
        command = self.at(self.ip())
        arg_1 = self.at(self.ip() + 1)
        arg_2 = self.at(self.ip() + 2)

        if command == MOV:
            self.mov(arg_1, arg_2)
        elif command == MOVN:
            self.movn(arg_1, arg_2)
        elif command == ADD:
            self.add(arg_1, arg_2)
        elif command == ADDN:
            self.addn(arg_1, arg_2)
        elif command == SUB:
            self.sub(arg_1, arg_2)
        elif command == SUBN:
            self.subn(arg_1, arg_2)
        elif command == JMP:
            self.jmp(arg_1)
        elif command == JLZ:
            self.jlz(arg_1, arg_2)
        elif command == PUSH:
            self.push(arg_1)
        elif command == POP:
            self.pop(arg_1)
        elif command == CALL:
            self.call(arg_1)
        elif command == RET:
            self.ret()
        elif command == END:
            return False
        elif command == PRINT:
            self.print(arg_1, arg_2)
        elif command == READN:
            self.readn(arg_1)
        else:
            print("Error: ", command, " is not a valid command code")
            return False

        self.memory.write(EIP, self.ip() + COMMAND_LEN)
        if DEBUG:
            self.memory.print(100)
        return True

    def ip(self):
        return self.memory.read(EIP)

    def at(self, addr):
        return self.memory.read(addr)


buff = MakeBinaryFromAsm("s.txt", "")
vm = VirtualMachine(memory=BinaryFile(len(buff), buff))

vm.Run()