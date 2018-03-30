import numpy as np
import sys
from common import *


# условно пишем в исполняемый файл, но не насилуем жеский диск
class BinaryFile:
    def __init__(self, path):
        self.path = path
        self.buff = np.fromfile(path, dtype=np.int)
        self.size = len(self.buff)

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

    def dump(self, path=None):
        if path is None:
            path = self.path
        self.buff.tofile(path, dtype=np.int)


class VirtualMachine:
    def __init__(self, memory):
        self.memory = memory
        self.private_reg = [EIP, ESP, EBP, STC, NIU]

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
        self.memory.write(EIP, where - COMMAND_LEN)

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
            mask = [255 << 24, 255 << 16, 255 << 8, 255]
            packed = [self.at(start + i) for i in range(length)]
            packed = np.array(packed).view(np.uint)
            encoded = []
            for cell in packed:
                encoded.extend([cell >> 24, (cell & mask[1]) >> 16, (cell & mask[2]) >> 8, cell & mask[3]])
            print(bytes(encoded).decode('utf-8').strip(' '))
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


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: machine.py <.btc file>")
        exit(-1)

    vm = VirtualMachine(memory=BinaryFile(sys.argv[1]))
    vm.Run()
